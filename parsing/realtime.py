"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
import os
from queue import PriorityQueue, Queue
from threading import Thread, Lock
from time import sleep
import traceback
from typing import Any, Tuple, Dict
# UI Libraries
from tkinter import messagebox
# Packages
import mss
import pynput
from PIL import Image
from pypresence import Presence
# Data Modules
from data.keys import keys
from data.abilities import rep_ships
from data import abilities
from data.maps import MAP_TYPE_NAMES, MAP_NAMES
from data.servers import SERVERS
# network Modules
from network.minimap.client import MiniMapClient
from network.discord import DiscordClient
# Parsing Modules
from parsing.logstalker import LogStalker
from parsing.gsfinterface import GSFInterface
from parsing.guiparsing import get_player_guiname
from parsing.parser import Parser
from parsing.pointer import PointerParser
from parsing.realtimedb import RealTimeDB
from parsing.rgb import RGBController
from parsing.screen import ScreenParser
from parsing.shipstats import ShipStats
from parsing.timer import TimerParser
from parsing import vision
# Utility Modules
from utils.utilities import get_screen_resolution
from utils.utilities import get_cursor_position
from utils.window import Window
import variables


def pair_wise(iterable: (list, tuple)):
    """Create generator to loop over iterable in pairs"""
    return list(zip(*tuple(iterable[i::2] for i in range(2))))


screen_perf: Dict[str, Tuple[int, float]] = dict()
screen_slow: Dict[str, float] = dict()


def screen_func(feature: str) -> callable:
    """Function decorator that records the performance of function"""

    def outer(func: callable) -> callable:
        """Enable function performance measurement if enabled"""
        if not variables.settings["screen"]["perf"] is True:
            return func

        def benchmark(*args) -> Tuple[Any, float]:
            """Call the function and record its performance"""
            start = datetime.now()
            r = func(*args)
            elapsed = (datetime.now() - start).total_seconds()
            screen_perf[feature][0] += 1
            screen_perf[feature][1] += elapsed
            return r, elapsed

        # Record slow features if disabling them is enabled
        if variables.settings["screen"]["disable"] is True:
            def inner(*args) -> Any:
                r, elapsed = benchmark(*args)
                v = 1.0 if elapsed > 0.25 else -0.5
                if feature not in screen_slow:
                    screen_slow[feature] = 0
                screen_slow[feature] += v
                return r
        else:
            def inner(*args) -> Any:
                return benchmark(*args)[0]

        return inner
    return outer


class RealTimeParser(Thread):
    """
    Class to parse Galactic StarFighter in real-time

    Runs a LogStalker to monitor the log files and parse the lines in
    the CombatLogs.
    Additionally, Python-MSS is used to capture screenshots of the
    game if screen parsing is enabled. Those screenshots are used for
    additional advanced parsing purposes, for which the functions can
    be identified with update_*feature_name*.
    """

    TIMER_MARGIN = 10

    SCREEN_DATA_DEF = {
        "tracking": "", "health": (None, None, None), "map": None}

    def __init__(
            self,
            character_db,
            character_data,
            ships_db,
            companions_db,
            spawn_callback=None,
            match_callback=None,
            file_callback=None,
            event_callback=None,
            minimap_share=False,
            minimap_user=None,
            minimap_address: str = None,
            minimap_window=None,
            rpc: Presence = None,
    ):
        """
        :param character_db: Character database
        :param spawn_callback: Callback called with spawn_timing when a new spawn has been detected
        :param match_callback: Callback called with match_timing when a new match has been detected
        :param file_callback: Callback called with file_timing when a new file has been detected
        :param event_callback: Callback called with line_dict when a new event has been detected
        :param character_data: Character tuple with the character name and network to retrieve data with
        :param minimap_share: Whether to share minimap location with a server
        :param minimap_address: Address of the MiniMap sharing server
        :param minimap_user: Username for the MiniMap sharing server
        """
        Thread.__init__(self)

        self.options = variables.settings.dict()
        self.raven = variables.raven

        """
        Attributes
        """
        # Callbacks
        self._spawn_callback = spawn_callback
        self._match_callback = match_callback
        self._file_callback = file_callback
        self.event_callback = event_callback
        # Settings
        self._screen_enabled = self.options["screen"]["enabled"]
        self._screen_features = self.options["screen"]["features"]
        # Queues
        self.shots_queue = PriorityQueue()
        self._exit_queue = Queue()
        # Data
        self._character_data = character_data
        self._character_db = character_db
        self._character_db_data = self._character_db[self._character_data]
        self._realtime_db = RealTimeDB()
        self.diff = None
        self.ships_db = ships_db
        self.companions_db = companions_db
        # Discord Rich Presence
        self._rpc = rpc

        """
        File parsing
        """
        # LogStalker
        self._stalker = LogStalker(watching_callback=self._file_callback)
        # Data attributes
        self.dmg_d, self.dmg_t, self.dmg_s, self._healing, self.abilities = 0, 0, 0, 0, {}
        self.active_id, self.active_ids = "", []
        self.hold, self.hold_list = 0, []
        self.player_name = "Player Name"
        self.is_match = False
        self.start_match = None
        self.end_match = None
        self.start_spawn = None
        self.lines = []
        self.primary_weapon = False
        self.secondary_weapon = False
        self.scope_mode = False
        self.discord = DiscordClient()
        self.tutorial = False
        self._read_from_file = False

        """
        Screen parsing
        """
        self._screen_parsing_setup = False
        self._mss = None
        self._kb_listener = None
        self._ms_listener = None
        self._key_states = None
        self.ship = None
        self.ship_stats = None
        resolution = get_screen_resolution()
        self._monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}
        self._interface = None
        self._coordinates = {}
        self.screen_data = self.SCREEN_DATA_DEF.copy()
        self._resolution = resolution
        self._pixels_per_degree = 10
        self._waiting_for_timer = False
        self._spawn_timer_res_flag = False
        self._spawn_time = None
        self._window = Window("swtor.exe") if self.options["screen"]["dynamic"] else None
        self.setup_screen_parsing()
        self._lock = Lock()
        self._configured_flag = False
        self._pointer_parser = None
        self._delayed_shots = list()
        self._rof = None
        self._rgb_enabled = self.options["realtime"]["rgb"]
        self._rgb = RGBController()
        self._active_map = None
        self._timer_parser = None
        if "Power Regeneration Delays" in self._screen_features:
            self._timer_parser = TimerParser()
        global screen_perf
        screen_perf.clear()
        screen_perf = {feature: [0, 0.0] for feature in self._screen_features}

        """
        MiniMap Sharing
        """
        self._username = minimap_user
        self._minimap = minimap_window
        self._address = minimap_address
        self._client = None
        if minimap_share is True:
            self.setup_minimap_share()

        self.update_presence()

    def setup_screen_parsing(self):
        """
        If it is enabled, set up the attribute objects with the correct
        parameters for use in the loop.
        """
        self._mss = mss.mss()
        self._kb_listener = pynput.keyboard.Listener(on_press=self._on_kb_press, on_release=self._on_kb_release)
        self._ms_listener = pynput.mouse.Listener(on_click=self._on_ms_press)
        file_name = get_player_guiname(self._character_db_data["Name"], self._character_db_data["Server"])
        self._interface = GSFInterface(file_name)
        self._coordinates = {
            "health": self._interface.get_ship_health_coordinates(),
            "minimap": self._interface.get_minimap_coordinates(),
            "hull": self._interface.get_ship_hull_box_coordinates(),
            "scorecard": self._interface.get_scorecard_coordinates(),
        }
        self._pixels_per_degree = self._interface.get_pixels_per_degree()
        self._screen_parsing_setup = True

    def setup_minimap_share(self):
        """Create a MiniMapClient and setup everything to share location"""
        if "MiniMap Location" not in self._screen_features:
            raise ValueError("MiniMap Location parsing not enabled.")
        print("[RealTimeParser: MiniMap]", self._address)
        addr, port = self._address.split(":")
        self._client = MiniMapClient(addr, int(port), self._username)
        self._minimap.set_client(self._client)

    def start_listeners(self):
        """Start the keyboard and mouse listeners"""
        if not self._screen_enabled or "Mouse and Keyboard" not in self._screen_features:
            return
        print("[RealTimeParser] Mouse and Keyboard parsing enabled.")
        self._kb_listener.start()
        self._ms_listener.start()

    def stop_listeners(self):
        """Stop the keyboard and mouse listeners"""
        if not self._screen_enabled:
            return
        self._kb_listener.stop()
        self._ms_listener.stop()
        self._kb_listener = None
        self._ms_listener = None

    def update_presence(self):
        """Update the Discord Rich Presence with new data"""
        if self._rpc is None:
            return
        assert isinstance(self._rpc, Presence)
        pid = os.getpid()
        if self._character_db_data["Discord"] is False:
            state = "Activity Hidden"
            self._rpc.update(pid, state, large_image="logo_green_png")
            return
        state = "In match" if self.is_match else "Out of match"
        if self.tutorial is True:
            state = "In tutorial"
        large_image, large_text, small_image, small_text = "starfighter", "Galactic StarFighter", None, None
        if self.is_match and self._active_map is not None:
            map_type, map_name = self._active_map
            large_text = MAP_TYPE_NAMES[map_type][map_name]
            large_image = MAP_NAMES[large_text]
        if self.is_match and self.ship is not None:
            small_image = self.ship.name.lower().replace(" ", "_")
            small_text = self.ship.ship_name
        if self.tutorial is True and self.is_match:
            large_text = MAP_TYPE_NAMES["dom"]["ls"]
            large_image = MAP_NAMES[large_text]
            small_image, small_text = "sting", "Sting"
        details = "{}: {}".format(self._character_db_data["Server"], self._character_db_data["Name"])
        start = None
        if self.start_match is not None and self.is_match:
            assert isinstance(self.start_match, datetime)
            start = datetime.combine(datetime.now().date(), self.start_match.time()).timestamp()
        self._rpc.update(
            pid=pid, state=state, details=details, start=start,
            large_image=large_image, large_text=large_text,
            small_image=small_image, small_text=small_text)

    def update(self):
        """Perform all the actions required for a single loop cycle"""
        now = datetime.now()
        # File parsing
        lines = self._stalker.get_new_lines()
        for line in lines:
            if line is None:
                continue
            if not isinstance(line["line"], str):
                raise TypeError()
            self.process_line(line)
        if not self.is_match and not self._waiting_for_timer:
            self.diff = datetime.now() - now
            return
        # Screen parsing
        if self._screen_enabled:
            screenshot = self._mss.grab(self._monitor)
            screenshot_time = datetime.now()
            image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            del screenshot
            self.process_screenshot(image, screenshot_time)
            del image
        # RealTimeParser sleep limiting
        self.diff = datetime.now() - now
        if self.options["realtime"]["sleep"] is True and self.diff.total_seconds() < 0.5:
            sleep(0.5 - self.diff.total_seconds())

    def process_line(self, line: dict):
        """
        Parse a single line dictionary and update the data attributes
        of the instance accordingly
        """
        if Parser.is_ignorable(line):
            return
        if Parser.is_login(line):
            self.handle_login(line)
        # First check if this is still a match event
        if self.is_match and ("@" in line["source"] or "@" in line["target"]):
            self.handle_match_end(line)
            return
        # Handle out-of-match events
        if not self.is_match:
            # Check if this event is still not in-match
            if "@" in line["source"] or "@" in line["target"]:
                return
            else:  # Valid match event
                self.handle_match_start(line)
        if Parser.is_tutorial_event(line):
            self.tutorial = True
        self.handle_spawn(line)
        self.update_player_id(line)
        if self.active_id == "":
            print("[RealTimeParser] Holding line.")
            self.hold_list.append(line)
            self.hold += 1
            return
        self.parse_line(line)
        self.update_rgb_keyboard(line)
        self.update_ship()

    def handle_match_end(self, line: dict):
        """Handle the end of a GSF match"""
        print("[RealTimeParser] Match end.")
        server, date, time = self._character_db_data["Server"], line["time"], line["time"]
        id_fmt = self.active_id[:8]
        if not self.tutorial:
            self.discord.send_match_end(server, date, self.start_match, id_fmt, time)
            match_map = self._realtime_db.get_for_spawn("map")
            if match_map is not None:
                self.discord.send_match_map(server, date, self.start_match, id_fmt, match_map)
        self.end_match = line["time"]
        # No longer a match
        self.is_match = False
        self.tutorial = False
        self.lines.clear()
        # Spawn timer
        self._spawn_time = None
        # Reset match statistics
        self.dmg_d, self.dmg_t, self.dmg_s, self._healing = 0, 0, 0, 0
        self.abilities.clear()
        self.active_id = ""
        self.primary_weapon, self.secondary_weapon = False, False
        if self._pointer_parser is not None:
            self._pointer_parser.stop()
            self._pointer_parser = None
        self._active_map = None
        self.update_presence()
        if self._timer_parser is not None:
            self._timer_parser.match_end()
        self._active_map = None
        self._realtime_db.write_spawn_data()

    def handle_match_start(self, line: dict):
        """Handle the start of a new GSF match"""
        print("[RealTimeParser] Match start.")
        self.start_match = datetime.combine(datetime.now().date(), line["time"].time())
        self.is_match = True
        self.update_presence()
        # Call the new match callback
        self._match_callback()
        if self._timer_parser is not None:
            self._timer_parser.match_start()

    def handle_spawn(self, line: dict):
        """Check for a new spawn and handle it if required"""
        if line["source"] != self.active_id and line["target"] != self.active_id:
            self.abilities.clear()
            self.active_id = ""
            # Call the spawn callback
            self.start_spawn = line["time"]
            self._spawn_callback()
            self.ship = None
            self.ship_stats = None
            self.primary_weapon, self.secondary_weapon, self.scope_mode = False, False, False
            self.update_presence()
            self._realtime_db.set_spawn(self._stalker.file, self.start_match, self.start_spawn)

    def update_player_id(self, line: dict):
        """Update the Player ID if this line allows it"""
        if self.active_id == "" and line["source"] == line["target"]:
            print("[RealTimeParser] New player ID: {}".format(line["source"]))
            self.active_id = line["source"]
            self.active_ids.append(line["source"])
            server, date, start = self._character_db_data["Server"], self.start_match, self.start_match
            self.discord.send_match_start(server, date, start, self.active_id[:8])
            # Parse the lines that are on hold
            if self.hold != 0:
                self.hold = 0  # For recursive calls, this must be zero to prevent an infinite loop
                for line_dict in reversed(self.hold_list):
                    self.process_line(line_dict)
                self.hold_list.clear()

    def handle_login(self, line: dict):
        """Handle a login event"""
        self.player_name = line["source"][1:]  # Do not store @
        print("[RealTimeParser] Login: {}".format(self.player_name))
        self.process_login()
        # Spawn Timer
        if (self._screen_enabled and "Spawn Timer" in self._screen_features and
                self._waiting_for_timer is False and self.is_match is False):
            # Only activates if the Spawn Timer screen parsing
            # feature is enabled and there is no match active.
            # If a match is active, then this probably marks the end
            # of a match instead of the start of one.
            self._waiting_for_timer = datetime.now()

        # Perform error handling. Using real-time parsing with a
        # different character name is not possible for screen parsing
        if self.player_name != self._character_data[1]:
            print("[RealTimeParser] WARNING: Different character name")

    def parse_line(self, line: dict):
        """Parse an actual GSF event line"""
        Parser.get_event_category(line, self.active_id)
        if line["amount"] == "":
            line["amount"] = "0"
        line["amount"] = int(line["amount"].replace("*", ""))
        if "Heal" in line["effect"]:
            self._healing += line["amount"]
            self._rgb.data_queue.put(("press", "hr"))
        elif "Damage" in line["effect"]:
            if "Selfdamage" in line["ability"]:
                self.dmg_s += line["amount"]
            elif line["source"] in self.active_ids:
                self.dmg_d += line["amount"]
                self._rgb.data_queue.put(("press", "dd"))
            else:
                self.dmg_t += line["amount"]
                self._rgb.data_queue.put(("press", "dt"))

        if line["ability"] in self.abilities:
            self.abilities[line["ability"]] += 1
        else:  # line["ability"] not in self.abilities:
            self.abilities[line["ability"]] = 1
        self.lines.append(line)
        if callable(self.event_callback):
            line_effect = Parser.line_to_event_dictionary(line, self.active_id, self.lines)
            self.event_callback(line_effect, self.player_name, self.active_ids, self.start_match)
        self.process_weapon_swap(line)
        self._read_from_file = True

    def process_weapon_swap(self, line: dict):
        """Determine if a weapon was swapped in this event"""
        if line["ability"] == "Scope Mode":
            self.scope_mode = not self.scope_mode
        elif line["ability"] == "Primary Weapon Swap":
            self.primary_weapon = not self.primary_weapon
            if self._timer_parser is not None:
                self._timer_parser.primary_weapon_swap()
        elif line["ability"] == "Secondary Weapon Swap":
            self.secondary_weapon = not self.secondary_weapon

    def update_rgb_keyboard(self, line: dict):
        """Pass data to the RGB Keyboard Handler"""
        if "AbilityActivate" in line["effect"] and line["source"] in self.active_ids:
            ability = line["ability"]
            if ability in abilities.systems:
                self._rgb.data_queue.put(("press", "1"))
            elif ability in abilities.shields:
                self._rgb.data_queue.put(("press", "2"))
            elif ability in abilities.engines:
                self._rgb.data_queue.put(("press", "3"))
            elif ability in abilities.copilots:
                self._rgb.data_queue.put(("press", "4"))

    def update_ship(self):
        """Update the Ship and ShipStats attributes"""
        if self.ship is not None:
            return
        ship = Parser.get_ship_for_dict(self.abilities)
        if len(ship) > 1:
            return
        elif len(ship) == 0:
            self.abilities.clear()
            return
        ship = ship[0]
        if self._character_db[self._character_data]["Faction"].lower() == "republic":
            ship = rep_ships[ship]
        if self._screen_enabled is False:
            return
        ship_objects = self._character_db[self._character_data]["Ship Objects"]
        if ship not in ship_objects:
            self._configured_flag = True
            print("[RealTimeParser] Ship not configured: {}".format(ship))
            return
        self._configured_flag = False
        self.ship = ship_objects[ship]
        args = (self.ship, self.ships_db, self.companions_db)
        self.ship_stats = ShipStats(*args)
        self._realtime_db.set_for_spawn("ship", self.ship)
        self.update_presence()
        if self._timer_parser is not None:
            self._timer_parser.set_ship_stats(self.ship_stats)

    def update_pointer_parser_ship(self):
        """Update the PointerParser data after the Ship has been set"""
        key = "PrimaryWeapon" if self.primary_weapon is False else "PrimaryWeapon2"
        if key in self.ship_stats:
            rof = self.ship_stats[key]["Weapon_Rate_of_Fire"]
            c_rof = self._pointer_parser.rof
            if c_rof is not None and abs(1 / c_rof - rof) < 0.01:
                return
            self._pointer_parser.set_rate_of_fire(rof, self.ship.ship_class)
            self._rof = rof

    def process_login(self):
        """Process a Safe Login event"""
        server, name = self._character_data
        if name != self.player_name:
            self._character_data = (server, self.player_name)
            if self._character_data not in self._character_db:
                messagebox.showerror("Error", "The GSF Parser does not know this character yet!")
                raise KeyError("Unknown character")
            self._character_db_data = self._character_db[self._character_data]
        self.update_presence()

    def process_screenshot(self, screenshot: Image.Image, screenshot_time: datetime):
        """Analyze a screenshot and take the data to save it"""
        if self._screen_parsing_setup is False:
            self.setup_screen_parsing()
        now = datetime.now()

        if "Spawn Timer" in self._screen_features:
            self.update_timer_parser(screenshot, screenshot_time)
        if "Tracking penalty" in self._screen_features:
            self.update_tracking_penalty(now)
        if "Ship health" in self._screen_features:
            self.update_ship_health(screenshot, now)
        if "Map and match type" in self._screen_features:
            self.update_map_match_type(screenshot)
        if "MiniMap Location" in self._screen_features:
            self.update_minimap_location(screenshot)
        if "Match score" in self._screen_features:
            self.update_match_score(screenshot)
        if "Pointer Parsing" in self._screen_features:
            self.update_pointer_parser()

        if self.options["screen"]["perf"] is True and self.options["screen"]["disable"] is True:
            self.disable_slow_features()

    def disable_slow_features(self):
        """
        Remove slow performing features from the screen feature list

        Screen parsing features have their performance recorded by the
        @screen_func decorator. For each fast run, a feature has their
        slow count reduced by 0.5, for each slow run it is increased by
        1. If a feature consistently performs slow and their count
        increases to 3, it is disabled.
        """
        global screen_slow
        for feature, count in screen_slow.items():
            if count > 10 and feature in self._screen_features:
                self._screen_features.remove(feature)
                print("[RealTimeParser] Disabled feature {}".format(feature))

    @screen_func("Spawn Timer")
    def update_timer_parser(self, screenshot: Image.Image, screenshot_time: datetime):
        """
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
                self._waiting_for_timer = False
            # Check if the resolution is supported
            if self._resolution not in vision.timer_boxes:
                self._spawn_timer_res_flag = True
                return
            # Now crop the screenshot, see vision.timer_boxes for details
            source = screenshot.crop(vision.timer_boxes[self._resolution])
            source.save("timer.png")
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

    @screen_func("Tracking penalty")
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
        self._realtime_db.set_for_spawn("cursor_pos", now, mouse_coordinates)
        # Relative cursor position
        distance = vision.get_distance_from_center(mouse_coordinates, self._resolution)
        self._realtime_db.set_for_spawn("distance", now, distance)
        # Tracking penalty
        degrees = vision.get_tracking_degrees(distance, self._pixels_per_degree)
        if self.ship_stats is not None:
            constants = self.get_tracking_penalty()
            penalty = vision.get_tracking_penalty(degrees, *constants)
        else:
            penalty = None
        self._realtime_db.set_for_spawn("tracking", now, penalty)
        # Set the data for the string building
        unit = "°" if penalty is None else "%"
        string = "{:.1f}{}".format(degrees if penalty is None else penalty, unit)
        self.screen_data["tracking"] = string

    @screen_func("Ship health")
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
        self._realtime_db.set_for_spawn("health", now, (health_hull, health_shields_f, health_shields_r))
        if "minimap" in self._screen_features and self._client is not None:
            self._client.send_health(int(health_hull))

    @screen_func("MiniMap Location")
    def update_minimap_location(self, screenshot: Image.Image):
        """
        MiniMap Location

        Determines the location of the player marker on the MiniMap for
        a given screenshot. The screenshot is cropped to the MiniMap
        location and then the vision module gets the location.
        """
        if self._client is None:
            return
        minimap = screenshot.crop(self.get_coordinates("minimap"))
        fracs = vision.get_minimap_location(minimap)
        self._client.send_location(fracs)
        self._minimap.update_location("location_{}_{}".format(self.player_name, fracs))

    @screen_func("Map and match type")
    def update_map_match_type(self, screenshot: Image.Image):
        """
        Map and match type

        Uses feature matching to attempt to determine the map that the
        player is currently engaged in. If the map is determined at one
        point, detection is not attempted again.
        """
        if self._active_map is not None or self.active_id != "":
            return
        minimap = screenshot.crop(self.get_coordinates("minimap"))
        match_map = vision.get_map(minimap)
        if match_map is not None:
            self._realtime_db.set_for_spawn("map", match_map)
            self._active_map = match_map
            if self.discord is not None:
                server, date, start = self._character_db_data["Server"], self.start_match, self.start_match
                if None not in (server, date, start):
                    id_fmt = self.active_id[:8]
                    self.discord.send_match_map(server, date, start, id_fmt, match_map)
            print("[RealTimeParser] Minimap: {}".format(match_map))
            self.update_presence()
        if self._active_map is not None and self._realtime_db.get_for_spawn("map") is None:
            self._realtime_db.set_for_spawn("map", self._active_map)

    @screen_func("Match score")
    def update_match_score(self, screenshot: Image.Image):
        """
        Match score

        Continuously attempts to determine the ratio of the team scores
        """
        # TODO: Implement support for detecting wargames
        # The starting position of the team (what side of the map)
        # determines where their score bar is located (top or bottom)
        # TODO: Implement OCR or some other more accurate technique
        # Currently, only the ratio of the two scores is calculated,
        # and it is rather ineffective. White or very light pixels
        # have a huge impact on the result.
        # TODO: Implement feature to only detect at match end
        # The progression of the score of a match is not as interesting
        # in most cases as the actual end score. Another option is to
        # only determine it once a minute or some similar technique to
        # limit the performance impact of this feature.
        if self.active_id == "":
            return
        scorecard = screenshot.crop(self.get_coordinates("scorecard"))
        score = vision.get_score(scorecard)
        self._realtime_db.set_for_spawn("score", score)
        if self.discord is not None:
            self.discord.send_match_score(
                self._character_db_data["Server"], self.start_match, self.start_match, self.active_id[:8],
                self._character_db_data["Faction"], score)

    @screen_func("Pointer Parsing")
    def update_pointer_parser(self):
        """
        Pointer Parsing

        Pointer parsing is capable of matching shots fired with a
        PrimaryWeapon
        """
        if self._pointer_parser is None:
            # Create a new PointerParser for each match
            self._pointer_parser = PointerParser(self._interface)
            self._pointer_parser.start()
        # If Ship is not set, the PointerParser doesn't work
        if self.ship is None or self.ship_stats is None:
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
                self.event_callback(event, self.player_name, self.active_ids, self.start_match)
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
                if "Damage" in line["line"] and line["source"] == self.active_id:
                    hits[moment] = "Hit"
                    shots.remove(moment)
                    used.append(line)
        hits.update({moment: "Evade" for moment in shots if moment not in hits})
        for shot, state in hits.items():
            event = self.build_shot_event(shot, state)
            if event is None:
                continue
            self.event_callback(event, self.player_name, self.active_ids, self.start_match)

    def get_coordinates(self, key: str):
        """
        Return coordinates for a given key corrected for dynamic window
        location.
        """
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
        except ValueError:
            print(traceback.format_exc())
            print(coords, print(list(list(elem) for elem in pair_wise(coords))))
            return coords
        corrected = tuple(map(int, corrected))
        print("[RealTimeParser/Window] Corrected coordinates for {}: {} -> {}".format(
            key, coords, corrected))
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
    def primary(self)->str:
        """Return the name of the active primary weapon"""
        if self.ship is None:
            return "Unknown Ship"
        key = "PrimaryWeapon{}".format("" if self.primary_weapon is False else "2")
        component = self.ship[key]
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

    def run(self):
        """Run the loop and provide error handling, cleanup afterwards"""
        self._rgb.start()
        self.start_listeners()
        if self._timer_parser is not None:
            self._timer_parser.start()
        while True:
            if not self._exit_queue.empty():
                break
            try:
                self.update()
            except Exception as e:
                # Errors are not often handled well in Threads
                self.raven.captureException()
                error = traceback.format_exc()
                print("[RealTimeParser] encountered an error: ", error)
                messagebox.showerror(
                    "Error",
                    "The real-time parsing back-end encountered an error while performing operations. "
                    "The error has been reported to the developer.")
                raise
        self._realtime_db.write_spawn_data()
        # Perform closing actions
        self.stop_listeners()
        self.cleanup()

    def cleanup(self):
        """Clean up all the object references"""
        self.lines.clear()
        if self._rgb is not None and hasattr(self._rgb, "stop"):
            self._rgb.stop()
            self._rgb = None
        if self._timer_parser is not None:
            self._timer_parser.stop()
            self._timer_parser = None

    def stop(self):
        """Stop the RealTimeParser activities"""
        if self._pointer_parser is not None:
            self._pointer_parser.stop()
        self._exit_queue.put(True)
        if self._rgb.is_alive():
            self._rgb.stop()
        if self._timer_parser is not None:
            self._timer_parser.stop()

    def _on_kb_press(self, key):
        if not self.is_match or key not in keys:
            return
        key = keys[key]
        if key in self._key_states and self._key_states[key] is True:
            return  # Ignore press hold repeat
        time = datetime.now()
        self._realtime_db.set_for_spawn("keys", time, (key, True))
        self._key_states[key] = True
        if self._rgb.enabled and self._rgb_enabled and key in self._rgb.WANTS:
            self._rgb.data_queue.put(("press", key))
        if "F" in key and len(key) == 2:
            effect = ScreenParser.create_power_mode_event(self.player_name, time, key, self.ship_stats)
            self.event_callback(effect, self.player_name, self.active_ids, self.start_match)

    def _on_kb_release(self, key):
        if not self.is_match or key not in keys:
            return
        self._key_states[keys[key]] = False
        self._realtime_db.set_for_spawn("keys", datetime.now(), (keys[key], False))
        if self._rgb.enabled and self._rgb_enabled and key in self._rgb.WANTS:
            self._rgb.data_queue.put(("release", key))

    def _on_ms_press(self, x, y, button, pressed):
        if not self.is_match:
            return
        self._realtime_db.set_for_spawn("clicks", datetime.now(), (pressed, button))

    @property
    def perf_string(self) -> str:
        """Return a string with screen parsing feature performance"""
        if len(self._screen_features) == 0:
            return "No screen parsing features enabled"
        string = str()
        global screen_perf
        for feature, (count, time) in screen_perf.items():
            if count == 0 or time / count < 0.25:
                continue
            avg = time / count
            if feature not in self._screen_features:
                # Feature has been disabled by perf profiler
                string += "{}: {:.3f}s, disabled\n".format(feature, avg)
            else:
                string += "{}: {:.3f}s\n".format(feature, avg)
        return string

    @property
    def overlay_string(self) -> str:
        """String of text to set in the Overlay"""
        if self.is_match is False and self.options["realtime"]["overlay_when_gsf"] is True:
            return ""
        string = self.notification_string + self.parsing_data_string
        if "Spawn Timer" in self._screen_features:
            string += self.spawn_timer_string
        if "Tracking penalty" not in self._screen_features:
            string += self.tracking_string
        if "Map and match type" in self._screen_features:
            string += self.map_match_type_string
        if self._timer_parser is not None and self._timer_parser.is_alive():
            string += self._timer_parser.string
        return string.strip()

    @property
    def tracking_string(self) -> str:
        return "Tracking: {}\n".format(self.screen_data["tracking"])

    @property
    def parsing_data_string(self) -> str:
        """Simple normal parsing data string"""
        return "Damage Dealt: {}\n" \
               "Damage Taken: {}\n" \
               "Selfdamage: {}\n" \
               "Healing Recv: {}\n". \
            format(self.dmg_d, self.dmg_t, self.dmg_s, self._healing)

    @property
    def spawn_timer_string(self) -> str:
        """Spawn timer parsing string for the Overlay"""
        if self._spawn_timer_res_flag:
            return "Unsupported resolution for Spawn Timer\n"
        if self._spawn_time is None:
            return ""
        return "Spawn in {:02d}s\n".format(
            divmod(int((datetime.now() - self._spawn_time).total_seconds()), 20)[1])

    @property
    def map_match_type_string(self) -> str:
        """Map and match type string"""
        if self.screen_data["map"] is None:
            return "Map: Unknown\n"
        map_type, map_name = self.screen_data["map"]
        return "Map: {}\n".format(MAP_TYPE_NAMES[map_type][map_name])

    @property
    def notification_string(self):
        """String that notifies the user of special situations"""
        string = "Character: {}\n".format(self._character_db_data["Name"]) + \
                 "Server: {}\n".format(SERVERS[self._character_db_data["Server"]])
        ship = "Ship: {}".format(self.ship.name if self.ship is not None else "Unknown")
        if self._configured_flag is True:
            ship += " (Not fully configured)"
        ship += "\n\n"
        return string + ship
