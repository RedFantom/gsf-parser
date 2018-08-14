"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
from multiprocessing import Process, Event
from time import sleep
from typing import Any, Dict, Tuple
# Packages
from mss import mss
from PIL import Image
from pynput.keyboard import Listener as KListener, Key, KeyCode
from pynput.mouse import Listener as MListener, Button
# Project Modules
from data.keys import KEYS
from parsing import RealTimeDB
from parsing.pointer import PointerParser
from parsing.post import PostParser
from parsing.shipstats import ShipStats
from parsing import benchmarker, GSFInterface, Parser, vision
from parsing.speed import SpeedParser
from utils import Window, get_screen_resolution, get_cursor_position, pair_wise


class ScreenParser(Process):
    """Process that runs a loop that analyzes screenshots"""

    TIMER_MARGIN = 15

    def __init__(self, data_pipe, exit_event: Event, options: dict, interface: GSFInterface, **kwargs):
        """
        :param data_pipe: Data Pipe to communicate with the controlling
            FileParser Process instance.
        :param exit_event: Event that indicates an exit request
        :param options: Dictionary from settings.Settings.dict
        :param interface: GUI Profile for selected character
        """
        self.pipe, self.exit = data_pipe, exit_event
        self.interface: GSFInterface = interface
        self.options = options.copy()
        self._rectangle: Tuple[int, int, int, int] = (0, 0, *get_screen_resolution())
        self._window: Window = None
        if self.options["screen"]["dynamic"] is True:
            self._window = Window("swtor.exe")

        Process.__init__(self)

        self.features = options["screen"]["features"].copy()
        self.perf = ""
        self.db: RealTimeDB = None

        self.m_listener: MListener = None
        self.k_listener: KListener = None
        self.mss = None
        self.is_match = False

        self.screen_data = {"tracking": "", "map": None, "health": (None, None, None)}
        self.ship_stats: ShipStats = None
        self.active_id = ""

        # SpawnTimerParser
        self._waiting_for_timer: datetime = None
        self._spawn_time: datetime = None
        self._spawn_timer_res_flag: bool = False

        # PointerParser
        self._pointer_parser: PointerParser = None
        self.lines, self._delayed_shots = list(), list()
        self.active_ids, self.player_name, self.match_start = list(), str(), None
        self._read_from_file = False
        self.primary_weapon, self.secondary_weapon = False, False

        # TrackingParser
        self._configured_flag = False
        self.scope_mode = False

        # Dynamic Window Location
        self._resolution = get_screen_resolution()

        # MouseKeyboardParser
        self._key_states = dict()

        # Speed Parser
        self._speed_parser: SpeedParser = None

        self._coordinates = {
            "health": self.interface.get_ship_health_coordinates(),
            "minimap": self.interface.get_minimap_coordinates(),
            "hull": self.interface.get_ship_hull_box_coordinates(),
            "scorecard": self.interface.get_scorecard_coordinates(),
        }

    def setup(self):
        """Initialize attributes in the new Process"""
        self.pipe.send(("pid", self.pid))
        self.db = RealTimeDB()
        if "Mouse and Keyboard" in self.features:
            self.m_listener = MListener(on_click=self.on_click)
            self.k_listener = KListener(on_press=self.on_press, on_release=self.on_release)
            self.m_listener.start()
            self.k_listener.start()
        if "Engine Speed" in self.features:
            self._speed_parser = SpeedParser()
            self._speed_parser.start()
        self.mss = mss()

    def cleanup(self):
        """Close all attributes opened in setup"""
        if self.m_listener is not None:
            self.m_listener.stop()
        if self.k_listener is not None:
            self.k_listener.stop()

    def start(self):
        """Start the Process"""
        print("[ScreenParser] Starting Process...")
        Process.start(self)

    def run(self):
        """Run the loop and watch for exit signals"""
        self.setup()
        while True:
            if self.exit.is_set():
                break
            self.update()
        self.cleanup()

    def process_pipe(self):
        """Process data in the pipe received from FileParser"""
        while self.pipe.poll():
            try:
                data: Tuple[str, Any] = self.pipe.recv()
            except EOFError:
                break
            self.process_pipe_data(data)

    def process_pipe_data(self, data: Tuple[str, Any]):
        """Process a single tuple message from the FileParser"""
        type, data = data
        if type == "match":
            self.is_match = not self.is_match
            self.handle_match()
        elif type == "spawn":
            self.handle_spawn()
        elif type == "ship":
            self.ship_stats = ShipStats(data, None, None)
            if self._speed_parser is not None:
                self._speed_parser.update_ship_stats(self.ship_stats)
        elif type == "event":
            event, self.player_name, self.active_ids, self.match_start = data
            self.lines.append(event)
            self._read_from_file = True
        elif type == "swap":
            setattr(self, data, not getattr(self, data))
        elif type == "id":
            self.active_id = data
        else:
            print("[ScreenParser] Unhandled Pipe data: {}".format((type, data)))

    def handle_match(self):
        """Handle a change of state in match"""
        if not self.is_match:  # Match end
            self.lines.clear()
            if self._speed_parser is not None:
                self._speed_parser.match_end()
        else:  # Match start
            if self._speed_parser is not None:
                self._speed_parser.match_start()

    def handle_spawn(self):
        """Handle a new spawn"""
        if self._speed_parser is not None:
            self._speed_parser.reset()
        self._configured_flag = False

    def update(self):
        """Run a single iteration of tasks"""
        start = datetime.now()
        self.process_pipe()
        if self.is_match:
            self.process_screen()
        self.pipe.send(("string", self.overlay_string))
        self.pipe.send(("perf", self.perf_string))
        if self.options["realtime"]["sleep"] is True:
            diff = (datetime.now() - start).total_seconds()
            if diff < 0.25:
                sleep(0.25 - diff)

    def process_screen(self):
        """Process the contents of the screen"""
        screenshot = self.mss.grab(self.monitor)
        time = datetime.now()
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        del screenshot
        self.process_screenshot(image, time)

    def process_screenshot(self, screenshot: Image.Image, screenshot_time: datetime):
        """Analyze a screenshot and take the data to save it"""
        now = datetime.now()

        if "Spawn Timer" in self.features:
            self.update_timer_parser(screenshot, screenshot_time)
        if "Tracking penalty" in self.features:
            self.update_tracking_penalty(now)
        if "Ship health" in self.features:
            self.update_ship_health(screenshot, now)
        if "Map and match type" in self.features:
            self.update_map_match_type(screenshot)
        if "MiniMap Location" in self.features:
            self.update_minimap_location(screenshot)
        if "Pointer Parsing" in self.features:
            self.update_pointer_parser()

        if self.options["screen"]["perf"] is True and self.options["screen"]["disable"] is True:
            self.disable_slow_features()

    def disable_slow_features(self):
        """
        Remove slow performing features from the screen feature list

        Screen parsing features have their performance recorded by the
        @benchmarker.benchmark decorator. For each fast run, a feature has their
        slow count reduced by 0.5, for each slow run it is increased by
        1. If a feature consistently performs slow and their count
        increases to 3, it is disabled.
        """
        for feature, count in benchmarker.SLOW.items():
            if count > 10 and feature in self.features:
                self.features.remove(feature)
                print("[RealTimeParser] Disabled feature {}".format(feature))

    @benchmarker.benchmark("Spawn Timer")
    def update_timer_parser(self, screenshot: Image.Image, screenshot_time: datetime):
        """
        TODO: Build new implementation based on Ready-button
        TimerParser

        Attempts to parse a screenshot that is expected to show the
        GSF pre-match interface with a spawn timer.
        """
        if self._waiting_for_timer and not self.is_match and self._spawn_time is None:
            print("[TimerParser] Spawn timer parsing activating.")
            # Only activates after a login event was detected and no
            # match is active and no time was already determined.

            # self._waiting_for_timer is a datetime instance, or False.
            if (datetime.now() - self._waiting_for_timer).total_seconds() > self.TIMER_MARGIN:
                # If a certain time has passed, give up on finding the timer
                print("[TimerParser] Last timer parsing attempt.")
                self._waiting_for_timer = None
            # Check if the resolution is supported
            if self.rectangle not in vision.timer_boxes:
                self._spawn_timer_res_flag = True
                return
            # Now crop the screenshot, see vision.timer_boxes for details
            source = screenshot.crop(vision.timer_boxes[self.rectangle])
            # Attempt to determine the spawn timer status
            status = vision.get_timer_status(source)
            # Now status is a string of format "%M:%S" or None
            if status is not None:
                print("[TimerParser] Successfully determined timer status as:", status)
                # Spawn timer was successfully determined. Now parse the string
                minutes, seconds = (int(elem) for elem in status.split(":"))
                delta = timedelta(minutes=minutes, seconds=seconds)
                # Now delta contains the amount of time left until the spawn starts
                self._spawn_time = screenshot_time + delta

    @benchmarker.benchmark("Tracking penalty")
    def update_tracking_penalty(self, now: datetime):
        """
        Tracking penalty

        Retrieves cursor coordinates and saves the following:
        - Absolute cursor position
        - Relative cursor position
        - Tracking penalty percentage
        """
        # Absolute cursor position
        if not self.is_match:
            return
        mouse_coordinates = get_cursor_position()
        self.db.set_for_spawn("cursor_pos", now, mouse_coordinates)
        # Relative cursor position
        distance = vision.get_distance_from_center(mouse_coordinates, self.rectangle)
        self.db.set_for_spawn("distance", now, distance)
        # Tracking penalty
        degrees = vision.get_tracking_degrees(distance, 10)
        if self.ship_stats is not None:
            constants = self.get_tracking_penalty()
            penalty = vision.get_tracking_penalty(degrees, *constants)
        else:
            penalty = None
        self.db.set_for_spawn("tracking", now, penalty)
        # Set the data for the string building
        unit = "°" if penalty is None else "%"
        string = "{:.1f}{}".format(degrees if penalty is None else penalty, unit)
        self.screen_data["tracking"] = string

    @benchmarker.benchmark("Ship health")
    def update_ship_health(self, screenshot: Image.Image, now: datetime):
        """
        Ship health

        Crops the screenshot to the hull and shield health indicator
        portions of the interface and then determines the hull and
        shield health using the colour of the pixels.
        """
        health_hull = vision.get_ship_health_hull(screenshot.crop(self.get_coordinates("hull")))
        (health_shields_f, health_shields_r) = vision.get_ship_health_shields(
            screenshot, self.get_coordinates("health"))
        if None in (health_hull, health_shields_f, health_shields_r):
            return
        self.db.set_for_spawn("health", now, (health_hull, health_shields_f, health_shields_r))

    @benchmarker.benchmark("MiniMap Location")
    def update_minimap_location(self, screenshot: Image.Image):
        """
        MiniMap Location

        Determines the location of the player marker on the MiniMap for
        a given screenshot. The screenshot is cropped to the MiniMap
        location and then the vision module gets the location.
        """
        minimap: Image.Image = screenshot.crop(self.get_coordinates("minimap"))
        fracs: Tuple[float, float] = vision.get_minimap_location(minimap)
        self.pipe.send(("location", fracs))

    @benchmarker.benchmark("Map and match type")
    def update_map_match_type(self, screenshot: Image.Image):
        """
        Map and match type

        Uses feature matching to attempt to determine the map that the
        player is currently engaged in. If the map is determined at one
        point, detection is not attempted again.
        """
        if self.screen_data["map"] is not None or not self.is_match:
            return
        minimap = screenshot.crop(self.get_coordinates("minimap"))
        match_map = vision.get_map(minimap)
        if match_map is not None:
            self.db.set_for_spawn("map", match_map)
            self.screen_data["map"] = match_map
            self.pipe.put(("map", match_map))
            print("[ScreenParser] Minimap: {}".format(match_map))
        if self.screen_data["map"] is not None and self.db.get_for_spawn("map") is None:
            self.db.set_for_spawn("map", self.screen_data["map"])

    def update_pointer_parser_ship(self):
        """Update the PointerParser data after the Ship has been set"""
        key = "PrimaryWeapon" if self.primary_weapon is False else "PrimaryWeapon2"
        if key in self.ship_stats:
            rof = self.ship_stats[key]["Weapon_Rate_of_Fire"]
            c_rof = self._pointer_parser.rof
            if c_rof is not None and abs(1 / c_rof - rof) < 0.01:
                return
            self._pointer_parser.set_rate_of_fire(rof, self.ship_stats.ship.ship_class)

    @benchmarker.benchmark("Pointer Parsing")
    def update_pointer_parser(self):
        """
        Pointer Parsing

        Pointer parsing is capable of matching shots fired with a
        PrimaryWeapon
        """
        if self._pointer_parser is None:
            # Create a new PointerParser for each match
            self._pointer_parser = PointerParser(self.interface)
            self._pointer_parser.start()
        # If Ship is not set, the PointerParser doesn't work
        if self.ship_stats is None:
            return
        self.update_pointer_parser_ship()
        # Process each shot
        new_shots, hits = list(), dict()
        while not self._pointer_parser.chance_queue.empty():
            moment, on_target = self._pointer_parser.chance_queue.get()
            if on_target is False:
                hits[moment] = "Miss"
                continue
            new_shots.append(moment)
        if self._read_from_file is False:
            self._delayed_shots.extend(new_shots)
            for shot, state in hits.items():
                event = self.build_shot_event(shot, state)
                if event is None:
                    continue
                self.pipe.put(("event", event))
            return
        self._read_from_file = False
        shots = self._delayed_shots.copy()
        self._delayed_shots = new_shots
        # Determine whether each shot was a Hit or Evade
        lines = self.lines.copy()
        used = list()
        for line in reversed(lines):
            for moment in shots.copy():
                if line in used:
                    continue
                actual = datetime.combine(line["time"].date(), moment.time())
                if (actual - line["time"]).total_seconds() > (1 / 4.6):  # Max ROF in the game
                    continue
                if "Damage" in line["line"] and Parser.compare_ids(line["source"], self.active_ids):
                    hits[moment] = "Hit"
                    shots.remove(moment)
                    used.append(line)
        hits.update({moment: "Evade" for moment in shots if moment not in hits})
        for shot, state in hits.items():
            event = self.build_shot_event(shot, state)
            if event is None:
                continue
            self.pipe.put(("event", event))

    def get_coordinates(self, key: str) -> (Tuple[int, int], Tuple[int, int, int, int]):
        """Return coordinates corrected for dynamic window location"""
        if self._window is None:
            return self._coordinates[key]
        x1, y1, x2, y2 = self._window.get_rectangle(0)
        w, h = x2 - x1, y2 - y1
        wo, ho = self._resolution
        coords = self._coordinates[key]
        corrected = list()
        try:
            for x, y in pair_wise(coords):  # Support 2 and 4 coord tuples
                x, y = x / wo * w + x1, y / ho * h + y1  # Correct for size and offset
                corrected.append(x)
                corrected.append(y)
        except ValueError as e:
            print("[ScreenParser.get_coordinates] {}".format(e))
            return coords
        corrected = tuple(map(int, corrected))
        return corrected

    def get_tracking_penalty(self):
        """
        Determine the correct weapon to determine the tracking penalty
        for and then retrieve that data from the ship statistics object
        stored in the self.ship_stats attribute.
        """
        primaries = ["PrimaryWeapon", "PrimaryWeapon2"]
        secondaries = ["SecondaryWeapon", "SecondaryWeapon2"]
        if self.scope_mode is True:
            weapon_key = secondaries[int(self.secondary_weapon)]
        else:  # self.scope_mode is False
            weapon_key = primaries[int(self.primary_weapon)]
        if weapon_key not in self.ship_stats:
            if self._configured_flag is False:
                print("Failed to retrieve stats for weapon: {}".format(weapon_key))
                self._configured_flag = True
            return 0, 0, 0
        firing_arc = self.ship_stats[weapon_key]["Weapon_Firing_Arc"]
        tracking_penalty = self.ship_stats[weapon_key]["trackingAccuracyLoss"]
        if "Weapon_Tracking_Bonus" in self.ship_stats[weapon_key]:
            upgrade_constant = self.ship_stats[weapon_key]["Weapon_Tracking_Bonus"]
        else:
            upgrade_constant = 0
        return tracking_penalty, upgrade_constant, firing_arc

    @property
    def primary(self) -> str:
        """Return the name of the active primary weapon"""
        if self.ship_stats is None:
            return "Unknown Ship"
        key = "PrimaryWeapon{}".format("" if self.primary_weapon is False else "2")
        component = self.ship_stats.ship[key]
        if component is None:
            return "Unknown Primary Weapon"
        return component.name

    def build_shot_event(self, shot: datetime, result: str) -> (dict, None):
        """Build an event from a PointerParser Shot"""
        if result == "Hit":
            return None
        line = {
            "type": Parser.LINE_ABILITY,
            "effect": result,
            "time": shot,
            "ability": "{}: {}".format(self.primary, result),
            "amount": 0,
            "source": self.active_id,
            "target": self.active_id,
            "icon": self.primary,
            "effects": None
        }
        return line

    def on_click(self, x: int, y: int, button: Button, pressed: bool):
        """
        Callback for pynput.mouse.Listener(on_click)

        Only clicks that occur during a match are saved, and only the
        mouse button and its state are saved.

        :param x, y: Click coordinates that are used for saving a
            PrimaryWeapon shot (Button.left pressed)
        :param button: Button enum type that indicates pressed mouse
            button. Only Button.left and Button.right are recorded.
        :param pressed: The new state of the Button. May be True
            (pressed) or False (released)
        """
        if not self.is_match or button not in (Button.left, Button.right):
            return
        now = datetime.now()
        self.db.set_for_spawn("clicks", now, (pressed, button))
        if button == Button.left and pressed is True:  # PrimaryWeapon shot
            self.db.set_for_spawn("shots", now, vision.get_distance_from_center((x, y), self.rectangle))

    def on_press(self, key: (Key, KeyCode)):
        """
        Callback for pynput.keyboard.Listener(on_press)

        Process the press of a key on the keyboard. Only keys that are
        relevant are processed and stored, and only if a match is
        active. Provides RGBController interaction.
        """
        if not self.is_match or key not in KEYS:
            return
        key = KEYS[key]
        if key in self._key_states and self._key_states[key] is True:
            return  # Ignore press hold repeat
        time = datetime.now()
        self.db.set_for_spawn("keys", time, (key, True))
        self._key_states[key] = True
        # if self._rgb.enabled and self._rgb_enabled and key in self._rgb.WANTS:
        #     self.rgb_queue_put(("press", key))
        if "F" in key and len(key) == 2:
            effect = PostParser.create_power_mode_event(self.player_name, time, key, self.ship_stats)
            self.pipe.send(("event", effect))

    def on_release(self, key: (Key, KeyCode)):
        """
        Callback for pynput.Keyboard.Listener(on_release)

        Process the release of a key on the Keyboard. Only keys that are
        relevant are processed and stored, and only if a match is
        active. Provides RGBController interaction.
        """
        if not self.is_match or key not in KEYS:
            return
        self._key_states[KEYS[key]] = False
        self.db.set_for_spawn("keys", datetime.now(), (KEYS[key], False))
        # if self._rgb.enabled and self._rgb_enabled and key in self._rgb.WANTS:
        #     self.rgb_queue_put(("release", key))

    @property
    def rectangle(self) -> Tuple[int, int, int, int]:
        """Return a rectangle to the window"""
        if self.options["screen"]["dynamic"] is False:
            return self._rectangle
        return self._window.get_rectangle()

    @property
    def monitor(self) -> Dict[str, int]:
        """Return a monitor dictionary from the rectangle"""
        x1, y1, x2, y2 = self.rectangle
        return {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}

    @property
    def perf_string(self) -> str:
        """Return a string with screen parsing feature performance"""
        if len(self.features) == 0:
            return "No screen parsing features enabled"
        string = str()
        for feature, (count, time) in benchmarker.PERF.items():
            if count == 0 or time / count < 0.25:
                continue
            avg = time / count
            if feature not in self.features:
                # Feature has been disabled by perf profiler
                string += "{}: {:.3f}s, disabled\n".format(feature, avg)
            else:
                string += "{}: {:.3f}s\n".format(feature, avg)
        return string

    @property
    def overlay_string(self) -> str:
        """String of text to set in the Overlay"""
        if self.is_match is False:
            return ""
        string = str()
        if "Spawn Timer" in self.features:
            string += self.spawn_timer_string
        if "Tracking penalty" in self.features:
            string += self.tracking_string
        if self._speed_parser is not None:
            string += self._speed_parser.string
        return string

    @property
    def tracking_string(self) -> str:
        return "Tracking: {}\n".format(self.screen_data["tracking"])

    @property
    def spawn_timer_string(self) -> str:
        """Spawn timer parsing string for the Overlay"""
        if self._spawn_timer_res_flag:
            return "Unsupported resolution for Spawn Timer\n"
        if self._spawn_time is None:
            return ""
        return "Spawn in {:02d}s\n".format(
            divmod(int((datetime.now() - self._spawn_time).total_seconds()), 20)[1])
