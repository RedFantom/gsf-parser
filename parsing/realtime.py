"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
from multiprocessing import Event
import os
import six
import sys
from queue import Queue
from threading import Thread, Lock
from time import sleep
import traceback
from typing import Any, Tuple, Dict, List
# UI Libraries
from tkinter import messagebox
# Packages
import mss
import pynput
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
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
from parsing.gsf import GSFInterface
from parsing.gui import get_player_guiname
from parsing import opencv
from parsing.parser import Parser
from parsing.pointer import PointerParser
from parsing.realtimedb import RealTimeDB
from parsing.rgb import RGBController
from parsing.scoreboards import ScoreboardParser
from parsing.screen import ScreenParser
from parsing.shipstats import ShipStats
from parsing.speed import SpeedParser
from parsing import tesseract
from parsing.delay import DelayParser
from parsing import vision
# Utility Modules
from utils.directories import get_assets_directory
from utils.utilities import get_screen_resolution, get_cursor_position
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
            if feature not in screen_perf:
                screen_perf[feature] = [0, 0]
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


def printf(string: str):
    """Write a string to stdout and flush"""
    sys.stdout.write(string + "\n")
    sys.stdout.flush()


class RealTimeParser(Thread):
    """
    Class to parse Galactic StarFighter in real-time

    Runs a LogStalker to monitor the log files and parse the lines in
    the CombatLogs.
    Additionally, Python-MSS is used to capture screenshots of the
    game if screen parsing is enabled. Those screenshots are used for
    additional advanced results purposes, for which the functions can
    be identified with update_*feature_name*.
    """

    TIMER_MARGIN = 20

    SCREEN_DATA_DEF = {
        "tracking": "", "health": (None, None, None), "map": None}

    def __init__(
            self,
            char_db,
            char_data,
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
        :param char_db: Character database
        :param spawn_callback: Callback called with spawn_timing when a new spawn has been detected
        :param match_callback: Callback called with match_timing when a new match has been detected
        :param file_callback: Callback called with file_timing when a new file has been detected
        :param event_callback: Callback called with line_dict when a new event has been detected
        :param char_data: Character tuple with the character name and network to retrieve data with
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
        self._features = self.options["screen"]["features"]
        # Queues
        self._exit_queue = Queue()
        self._overlay_string_q = Queue()
        self._perf_string_q = Queue()
        # Data
        self._char_i = char_data
        self._char_db = char_db
        self._char_data = self._char_db[self._char_i]
        self._realtime_db = RealTimeDB()
        self.diff = None
        self.ships_db = ships_db
        self.companions_db = companions_db
        # Discord Rich Presence
        self._rpc = rpc

        """
        File results
        """
        # LogStalker
        self._stalker: LogStalker = LogStalker(watching_callback=self._file_callback)
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
        self._abilities_disabled = dict()

        """
        Screen results
        """
        self._screen_parsing_setup = False
        self._mss = None
        self._kb_listener = None
        self._ms_listener = None
        self._key_states = dict()
        self.ship = None
        self.ship_stats = None
        resolution = get_screen_resolution()
        self._monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}
        self._interface: GSFInterface = GSFInterface(get_player_guiname(*reversed(char_data)))
        self._coordinates = {}
        self.screen_data = self.SCREEN_DATA_DEF.copy()
        self._resolution = resolution
        self._pixels_per_degree = 10 * self._interface.global_scale
        self._waiting_for_timer: datetime = None
        self._spawn_time = None
        self._window: Window = Window("swtor.exe") if self.options["screen"]["dynamic"] else None
        self.setup_screen_parsing()
        self._lock = Lock()
        self._configured_flag = False
        self._pointer_parser = None
        self._delayed_shots = list()
        self._rof = None
        self._rgb_enabled = self.options["realtime"]["rgb"]
        self._rgb: RGBController = RGBController.build() if self._rgb_enabled else None
        self._active_map = None
        self._timer_parser = None
        if "Power Regeneration Delays" in self._features:
            self._timer_parser = DelayParser()
        self._speed_parser = None
        if "Engine Speed" in self._features:
            self._speed_parser = SpeedParser()
        global screen_perf
        screen_perf.clear()
        screen_perf = {feature: [0, 0.0] for feature in self._features}
        self._ready_button_img: Image.Image = None
        self.power_mode = "F4"

        self._scoreboard_parsers: List[ScoreboardParser] = list()
        self._scoreboard = False
        self._scoreboard_parser: ScoreboardParser = None
        self._mp_exit: Event = Event()

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

    def start(self):
        """Redirect for Thread.start or Process.start"""
        print("[RealTimeParser] Starting Thread/Process...")
        Thread.start(self)

    def setup_screen_parsing(self):
        """
        If it is enabled, set up the attribute objects with the correct
        parameters for use in the loop.
        """
        if not self._screen_enabled:
            return
        try:
            self._mss = mss.mss()
        except Exception as e:
            print("Could not open MSS")
            messagebox.showerror("Error", "Could not initialize screenshot subsystem.")
            return
        self._kb_listener = pynput.keyboard.Listener(
            on_press=self._on_kb_press, on_release=self._on_kb_release, catch=False)
        self._ms_listener = pynput.mouse.Listener(on_click=self._on_ms_press, catch=False)
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
        if "MiniMap Location" not in self._features:
            raise ValueError("MiniMap Location results not enabled.")
        print("[RealTimeParser: MiniMap]", self._address)
        addr, port = self._address.split(":")
        self._client = MiniMapClient(addr, int(port), self._username)
        self._minimap.set_client(self._client)

    def start_listeners(self):
        """Start the keyboard and mouse listeners"""
        if not self._screen_enabled or "Mouse and Keyboard" not in self._features:
            return
        print("[RealTimeParser] Mouse and Keyboard results enabled.")
        self._kb_listener.start()
        self._ms_listener.start()

    def stop_listeners(self):
        """Stop the keyboard and mouse listeners"""
        if not self._screen_enabled or "Mouse and Keyboard" not in self._features:
            return
        print("[RealTimeParser] Stopping Listeners")
        self._kb_listener.stop()
        self._ms_listener.stop()
        self._kb_listener.join()
        self._ms_listener.join()
        self._kb_listener = None
        self._ms_listener = None

    def update_presence(self):
        """Update the Discord Rich Presence with new data"""
        if variables.settings["sharing"]["presence"] is not True or self._rpc is None:
            return
        assert isinstance(self._rpc, Presence)
        pid = os.getpid()
        if self._char_data["Discord"] is False:
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
        details = "{}: {}".format(self._char_data["Server"], self._char_data["Name"])
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
        # File results
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
        # Screen results
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
        if self._kb_listener is not None and not self._kb_listener._queue.empty():
            exception, value, traceback = self._kb_listener._queue.get()
            six.reraise(exception, value, traceback)

    def process_line(self, line: dict):
        """
        Parse a single line dictionary and update the data attributes
        of the instance accordingly
        """
        if Parser.is_ignorable(line):
            return
        if Parser.is_login(line):
            self.handle_login(line)
        if "effect" not in line:
            print("[RealTimeParser] Event missung 'effect', issues expected: {}".format(line))
        # First check if this is still a match event
        if self.is_match and not Parser.is_gsf_event(line):
            self.handle_match_end(line)
            return
        # Handle out-of-match events
        if not self.is_match:
            # Check if this event is still not in-match
            if "@" in line["source"] or "@" in line["target"]:
                return
            else:  # Valid match event
                self.handle_match_start(line)
        self.tutorial = self.tutorial or Parser.is_tutorial_event(line)
        self.handle_spawn(line)
        self.update_player_id(line)
        if self.active_id == "":
            print("[RealTimeParser] Holding line.")
            self.hold_list.append(line)
            self.hold += 1
            return
        self.parse_line(line)
        if self._rgb_enabled is True:
            self.update_rgb_keyboard(line)
        self.update_ship()
        if self._speed_parser is not None and Parser.compare_ids(line["target"], self.active_ids):
            self._speed_parser.process_slowed_event(line)
        self.update_disabled_parser(line)

    def handle_match_end(self, line: dict):
        """Handle the end of a GSF match"""
        print("[RealTimeParser] Match end.")
        self._match_callback(False)
        server, date, time = self._char_data["Server"], line["time"], line["time"]
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
        if self._speed_parser is not None:
            self._speed_parser.match_end()
        self._active_map = None
        self._realtime_db.write_spawn_data()

    def handle_match_start(self, line: dict):
        """Handle the start of a new GSF match"""
        print("[RealTimeParser] Match start.")
        self.start_match = datetime.combine(datetime.now().date(), line["time"].time())
        self.is_match = True
        self.update_presence()
        # Call the new match callback
        self._match_callback(True)
        if self._timer_parser is not None:
            self._timer_parser.match_start()
        if self._speed_parser is not None:
            self._speed_parser.match_start()

    def handle_spawn(self, line: dict):
        """Check for a new spawn and handle it if required"""
        if line["source"] == self.active_id or line["target"] == self.active_id:
            return
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
        if self._pointer_parser is not None:
            self._pointer_parser.new_spawn()
        if self._speed_parser is not None:
            self._speed_parser.reset()
        self.power_mode = "F4"

    def update_player_id(self, line: dict):
        """Update the Player ID if this line allows it"""
        if self.active_id == "" and line["source"] == line["target"]:
            print("[RealTimeParser] New player ID: {}".format(line["source"]))
            self.active_id = line["source"]
            self.active_ids.append(line["source"])
            server, date, start = self._char_data["Server"], self.start_match, self.start_match
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
        if (self._screen_enabled and "Spawn Timer" in self._features and
                self._waiting_for_timer is None and self.is_match is False):
            # Only activates if the Spawn Timer screen results
            # feature is enabled and there is no match active.
            # If a match is active, then this probably marks the end
            # of a match instead of the start of one.
            self._waiting_for_timer = datetime.now()

        # Perform error handling. Using real-time results with a
        # different character name is not possible for screen results
        if self.player_name != self._char_i[1]:
            print("[RealTimeParser] WARNING: Different character name")

    def parse_line(self, line: dict):
        """Parse an actual GSF event line"""
        if "effect" not in line:
            variables.raven.captureMessage("Effect element not present in line dictionary: {}".format(line))
            return
        Parser.get_event_category(line, self.active_id)
        if "amount" not in line or line["amount"] == "":
            line["amount"] = "0"
        if not isinstance(line["amount"], int):
            line["amount"] = int(line["amount"].replace("*", ""))
        if "Heal" in line["effect"]:
            self._healing += line["amount"]
            self.rgb_queue_put(("press", "hr"))
        elif "Damage" in line["effect"]:
            if "Selfdamage" in line["ability"]:
                self.dmg_s += line["amount"]
            elif line["source"] in self.active_ids:
                self.dmg_d += line["amount"]
                self.rgb_queue_put(("press", "dd"))
            else:
                self.dmg_t += line["amount"]
                self.rgb_queue_put(("press", "dt"))

        if line["source"] in self.active_ids:
            if line["ability"] not in self.abilities:
                self.abilities[line["ability"]] = 0
            self.abilities[line["ability"]] += 1
        
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
            if self._pointer_parser is not None:
                self._pointer_parser.set_scope_mode(self.scope_mode)
            if self._speed_parser is not None:
                self._speed_parser.set_scope_mode(self.scope_mode)
        elif line["ability"] == "Primary Weapon Swap":
            self.primary_weapon = not self.primary_weapon
            if self._timer_parser is not None:
                self._timer_parser.primary_weapon_swap()
        elif line["ability"] == "Secondary Weapon Swap":
            self.secondary_weapon = not self.secondary_weapon

    def update_rgb_keyboard(self, line: dict):
        """Pass data to the RGB Keyboard Handler"""
        if "effect" not in line or "source" not in line:
            print("[RealTimeParser] Invalid RGB line: {}".format(line))
            return
        if "AbilityActivate" in line["effect"] and line["source"] in self.active_ids:
            ability = line["ability"]
            if ability in abilities.systems:
                self.rgb_queue_put(("press", "1"))
            elif ability in abilities.shields:
                self.rgb_queue_put(("press", "2"))
            elif ability in abilities.engines:
                self.rgb_queue_put(("press", "3"))
            elif ability in abilities.copilots:
                self.rgb_queue_put(("press", "4"))

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
        if self._char_db[self._char_i]["Faction"].lower() == "republic":
            ship = rep_ships[ship]
        if self._screen_enabled is False:
            return
        ship_objects = self._char_db[self._char_i]["Ship Objects"]
        if ship not in ship_objects:
            self._configured_flag = True
            print("[RealTimeParser] Ship not configured: {}".format(ship))
            return
        print("[RealTimeParser] Detected new ship: {}".format(ship))
        self._configured_flag = False
        self.ship = ship_objects[ship]
        args = (self.ship, self.ships_db, self.companions_db)
        self.ship_stats = ShipStats(*args)
        self._realtime_db.set_for_spawn("ship", self.ship)
        self.update_presence()
        if self._timer_parser is not None:
            print("[RealTimeParser] Sending new ship to DelayParser")
            self._timer_parser.set_ship_stats(self.ship_stats)
        if self._speed_parser is not None:
            print("[RealTimeParser] Sending new ship to SpeedParser")
            self._speed_parser.update_ship_stats(self.ship_stats)

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
        server, name = self._char_i
        if name != self.player_name:
            self._char_i = (server, self.player_name)
            if self._char_i not in self._char_db:
                messagebox.showerror("Error", "The GSF Parser does not know this character yet!")
                raise KeyError("Unknown character")
            self._char_data = self._char_db[self._char_i]
        self.update_presence()

    def update_disabled_parser(self, line: dict):
        """Check a line for ability disable events"""
        if "Ability Disabled" in line["effect"]:
            applicant, ability, source = line["source"], line["effect"], line["effect_id"]
            if "ApplyEffect" in line["effect"]:  # Ability now disabled
                # Together, the applicant and source are considered unique
                # Multiple effects from the same applicant always overlap
                self._abilities_disabled[(applicant, source)] = ability
            elif "RemoveEffect" in line["effect"]:  # Ability no longer disabled
                # Applicant may have died in the mean-time
                if applicant == "System":  # Remove all effects of this type
                    for (applicant, source_id) in self._abilities_disabled.copy().keys():
                        if source_id != source:
                            continue
                        del self._abilities_disabled[(applicant, source_id)]
                else:  # Applicant still alive
                    del self._abilities_disabled[(applicant, source)]

    def process_screenshot(self, screenshot: Image.Image, screenshot_time: datetime):
        """Analyze a screenshot and take the data to save it"""
        if self._screen_parsing_setup is False:
            self.setup_screen_parsing()
        now = datetime.now()

        if "Spawn Timer" in self._features:
            self.update_timer_parser(screenshot, screenshot_time)
        if "Tracking penalty" in self._features:
            self.update_tracking_penalty(now)
        if "Ship health" in self._features:
            self.update_ship_health(screenshot, now)
        if "Map and match type" in self._features:
            self.update_map_match_type(screenshot)
        if "MiniMap Location" in self._features:
            self.update_minimap_location(screenshot)
        if "Scoreboard Parsing" in self._features:
            self.update_scoreboard_parser(screenshot)
        if "Pointer Parsing" in self._features:
            self.update_pointer_parser()

        if self.options["screen"]["perf"] is True and self.options["screen"]["disable"] is True:
            self.disable_slow_features()

    def disable_slow_features(self):
        """
        Remove slow performing features from the screen feature list

        Screen results features have their performance recorded by the
        @screen_func decorator. For each fast run, a feature has their
        slow count reduced by 0.5, for each slow run it is increased by
        1. If a feature consistently performs slow and their count
        increases to 3, it is disabled.
        """
        global screen_slow
        for feature, count in screen_slow.items():
            if count > 10 and feature in self._features:
                self._features.remove(feature)
                print("[RealTimeParser] Disabled feature {}".format(feature))

    @screen_func("Spawn Timer")
    def update_timer_parser(self, screenshot: Image.Image, screenshot_time: datetime):
        """
        TimerParser

        Attempts to parse a screenshot that is expected to show the
        GSF pre-match interface with a spawn timer.
        """
        if self._waiting_for_timer is None or self._spawn_time is not None or self.is_match is True:
            return

        if self._ready_button_img is None:
            img: Image.Image = Image.open(os.path.join(get_assets_directory(), "vision", "ready_button.png"))
            scale: float = self._interface.global_scale
            size = map(lambda s: int(round((s * scale))), img.size)
            self._ready_button_img = img.resize(size, Image.LANCZOS)
            del img

        print("[TimerParser] Spawn timer results activating.")
        # Only activates after a login event was detected and no
        # match is active and no time was already determined.

        # self._waiting_for_timer is a datetime instance, or False.
        if (datetime.now() - self._waiting_for_timer).total_seconds() > self.TIMER_MARGIN:
            # If a certain time has passed, give up on finding the timer
            print("[TimerParser] Last timer results attempt.")
            self._waiting_for_timer = None

        # Find the Ready Button image in the screenshot
        screenshot = screenshot.crop((screenshot.width // 2, screenshot.height // 2, *screenshot.size))
        is_match, location = opencv.template_match(screenshot, self._ready_button_img, 80.0)
        if not is_match:
            print("[TimerParser] Ready button not located")
            return  # Ready Button not located

        # Calculate the box of the spawn timer
        (x, y), (w, h) = location, self._ready_button_img.size
        _x1, _y1, _x2, _y2 = w // 2 - 15, -50, w // 2 + 55, -50 + 20
        scale = self._interface.global_scale
        _x1, _y1, _x2, _y2 = map(lambda v: int(round(v * (scale / 1.05))), (_x1, _y1, _x2, _y2))
        x1, y1, x2, y2 = x + _x1, y + _y1, x + _x2, y + _y2
        box: Tuple[int, int, int, int] = (x1, y1, x2, y2)
        print("[TimerParser] Box: {}".format(box))

        # Perform OCR on this box
        template = screenshot.crop(box)
        result: str = tesseract.perform_ocr(template)
        if result is None:  # OCR failed
            return

        # Interpret OCR results
        elements: Tuple[str, str] = result.split(":", 1)
        if len(elements) != 2:
            return
        minutes, seconds = elements
        if not seconds.isdigit():
            return
        result: int = int(seconds) % 20
        print("[TimerParser] Determined spawn time to be in {} seconds".format(result))
        self._spawn_time = screenshot_time + timedelta(seconds=result)

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
        if "minimap" in self._features and self._client is not None:
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
        if self._active_map is not None or self.active_id == "" or self.is_match is False:
            return
        minimap = screenshot.crop(self.get_coordinates("minimap"))
        match_map = vision.get_map(minimap)
        if match_map is not None:
            self._realtime_db.set_for_spawn("map", match_map)
            self._active_map = match_map
            if self.discord is not None:
                server, date, start = self._char_data["Server"], self.start_match, self.start_match
                if None not in (server, date, start):
                    id_fmt = self.active_id[:8]
                    self.discord.send_match_map(server, date, start, id_fmt, match_map)
            print("[RealTimeParser] Minimap: {}".format(match_map))
            self.update_presence()
        if self._active_map is not None and self._realtime_db.get_for_spawn("map") is None:
            self._realtime_db.set_for_spawn("map", self._active_map)

    @screen_func("Scoreboard Parsing")
    def update_scoreboard_parser(self, screenshot: Image.Image):
        """
        Scoreboard Parsing

        Attempt to parse a scoreboard once ctrl_l is pressed
        """
        if self._scoreboard_parser is not None and self._scoreboard_parser.is_done():
            self._scoreboard_parsers.remove(self._scoreboard_parser)
            self._scoreboard_parser = None
        if self._scoreboard_parser is None and len(self._scoreboard_parsers) > 0:
            self._scoreboard_parser = self._scoreboard_parsers[0]
            self._scoreboard_parser.start()

        if self._scoreboard is False:
            return
        self._scoreboard = False
        if self.start_match is None:
            return

        if not ScoreboardParser.is_scoreboard(screenshot, self._interface.global_scale):
            return
        print("[RealTimeParser:ScoreboardParser] Activated")
        parser = ScoreboardParser(self.start_match, screenshot)
        self._scoreboard_parsers.append(parser)
        self._scoreboard_parser = parser
        self._scoreboard_parser.start()

    @screen_func("Pointer Parsing")
    def update_pointer_parser(self):
        """
        Pointer Parsing

        Pointer results is capable of matching shots fired with a
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
    def primary(self) -> str:
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
        printf("[RealTimeParser] Starting Subprocesses")
        self.rgb_start()
        printf("[RealTimeParser] RGBController started")
        if "Mouse and Keyboard" in self._features:
            self.start_listeners()
            printf("[RealTimeParser] Listeners started")
        if self._timer_parser is not None:
            self._timer_parser.start()
            printf("[RealTimeParser] TimerParser started")
        if self._speed_parser is not None:
            self._speed_parser.start()
            printf("[RealTimeParser] SpeedParser started")
        while True:
            if not self._exit_queue.empty():
                break
            try:
                self.update()
            except Exception as e:
                self.raven.captureException()
                error = traceback.format_exc()
                print("[RealTimeParser] encountered an error: ", error)
                event = {
                    "time": datetime.now(),
                    "source": "GSF Parser",
                    "target": str(type(e)),
                    "ability": str(e.args),
                    "effect": "",
                    "effects": (),
                    "custom": True,
                    "self": True,
                    "crit": False,
                    "type": Parser.LINE_ABILITY,
                    "icon": "spvp_iffmimic",
                    "amount": 0,
                    "category": "other"
                }
                self.event_callback(event, self.player_name, self.active_ids, self.start_match)
        self._realtime_db.write_spawn_data()
        # Perform closing actions
        self.stop_listeners()
        self.cleanup()

    def cleanup(self):
        """Clean up all the object references"""
        self.lines.clear()
        self.rgb_stop()
        if self._timer_parser is not None:
            self._timer_parser.stop()
            self._timer_parser = None

    def stop(self):
        """Stop the RealTimeParser activities"""
        if self._pointer_parser is not None:
            self._pointer_parser.stop()
        self._exit_queue.put(True)
        if self._timer_parser is not None:
            self._timer_parser.stop()
        if self._speed_parser is not None:
            self._speed_parser.stop()

    def _on_kb_press(self, key: (Key, KeyCode)):
        """
        Callback for pynput.keyboard.Listener(on_press)

        Process the press of a key on the keyboard. Only keys that are
        relevant are processed and stored, and only if a match is
        active. Provides RGBController interaction.
        """
        if self._speed_parser is not None:
            self._speed_parser.on_key(key, True)
        if not self.is_match or key not in keys:
            return True
        key = keys[key]
        if key in self._key_states and self._key_states[key] is True:
                return True  # Ignore press hold repeat
        time = datetime.now()
        self._realtime_db.set_for_spawn("keys", time, (key, True))
        self._key_states[key] = True
        self.rgb_queue_put(("press", key))
        if "F" in key and len(key) == 2:
            if self.power_mode == key:
                return
            self.power_mode = key
            event = ScreenParser.create_power_mode_event(self.player_name, time, key, self.ship_stats)
            self.event_callback(event, self.player_name, self.active_ids, self.start_match)

    def _on_kb_release(self, key: (Key, KeyCode)):
        """
        Callback for pynput.Keyboard.Listener(on_release)

        Process the release of a key on the Keyboard. Only keys that are
        relevant are processed and stored, and only if a match is
        active. Provides RGBController interaction.
        """
        if self._speed_parser is not None:
            self._speed_parser.on_key(key, False)
        if not self.is_match or key not in keys:
            return
        self._key_states[keys[key]] = False
        self._realtime_db.set_for_spawn("keys", datetime.now(), (keys[key], False))
        self.rgb_queue_put(("release", key))
        if key == Key.ctrl_l or key == Key.ctrl:
            print("[RealTimeParser] ScoreboardParser triggered")
            self._scoreboard = True

    def _on_ms_press(self, x: int, y: int, button: Button, pressed: bool):
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
        self._realtime_db.set_for_spawn("clicks", now, (pressed, button))
        if button == Button.left and pressed is True:  # PrimaryWeapon shot
            self._realtime_db.set_for_spawn("shots", now, (x, y))
        if self._pointer_parser is not None and button == Button.left:
            self._pointer_parser.mouse_queue.put(pressed)

    def rgb_queue_put(self, item: Any):
        """Put an item in the RGBController Queue if RGB is enabled"""
        if self._rgb_enabled and self._rgb is not None and isinstance(self._rgb, RGBController):
            self._rgb.data_queue.put(item)

    def rgb_start(self):
        """Start the RGBController Thread if enabled"""
        if self._rgb is not None and isinstance(self._rgb, RGBController):
            self._rgb.start()

    def rgb_stop(self):
        """Stop the RGBController Thread if enabled"""
        if self._rgb is not None and isinstance(self._rgb, RGBController) and self._rgb.is_alive():
            self._rgb.stop()  # Joins itself

    @property
    def perf_string(self) -> str:
        """Return a string with screen results feature performance"""
        if len(self._features) == 0:
            return "No screen results features enabled"
        string = str()
        global screen_perf
        for feature, (count, time) in screen_perf.items():
            if count == 0 or time / count < 0.25:
                continue
            avg = time / count
            if feature not in self._features:
                # Feature has been disabled by perf profiler
                string += "{}: {:.3f}s, disabled\n".format(feature, avg)
            else:
                string += "{}: {:.3f}s\n".format(feature, avg)
        return string

    @property
    def overlay_string(self) -> str:
        """String of text to set in the Overlay"""
        if self.is_match is False and self.options["overlay"]["when_gsf"] is True:
            return ""
        string = self.notification_string + self.parsing_data_string
        if "Spawn Timer" in self._features:
            string += self.spawn_timer_string
        if "Tracking penalty" in self._features:
            string += self.tracking_string
        if "Map and match type" in self._features:
            string += self.map_match_type_string
        if self._timer_parser is not None and self._timer_parser.is_alive():
            string += self._timer_parser.string
        if self._speed_parser is not None:
            string += self._speed_parser.string
        if self._scoreboard_parser is not None:
            string += self._scoreboard_parser.string
        return string.strip()

    @property
    def tracking_string(self) -> str:
        if "Tracking Penalty" not in self._features:
            return ""
        return "Tracking: {}\n".format(self.screen_data["tracking"])

    @property
    def parsing_data_string(self) -> str:
        """Simple normal results data string"""
        return "Damage Dealt: {}\n" \
               "Damage Taken: {}\n" \
               "Selfdamage: {}\n" \
               "Healing Recv: {}\n". \
            format(self.dmg_d, self.dmg_t, self.dmg_s, self._healing)

    @property
    def spawn_timer_string(self) -> str:
        """Spawn timer results string for the Overlay"""
        if self.is_match is False:
            return ""
        if self._spawn_time is None:
            return "Next spawn unknown\n"
        return "Spawn in {:02d}s\n".format(
            20 - divmod(int((datetime.now() - self._spawn_time).total_seconds()), 20)[1])

    @property
    def map_match_type_string(self) -> str:
        """Map and match type string"""
        if self.screen_data["map"] is None:
            return "Map: Unknown\n"
        map_type, map_name = self.screen_data["map"]
        return "Map: {}\n".format(MAP_TYPE_NAMES[map_type][map_name])

    @property
    def notification_string(self) -> str:
        """String that notifies the user of special situations"""
        string = "Character: {}\n".format(self._char_data["Name"]) + \
                 "Server: {}\n".format(SERVERS[self._char_data["Server"]])
        ship = "Ship: {}".format(self.ship.name if self.ship is not None else "Unknown")
        if self._configured_flag is True:
            ship += " (Not fully configured)"
        ship += "\n\n"
        return string + ship

    @property
    def disabled_string(self):
        """String containing the disabled abilities for display in red"""
        disabled: list = list(set(self._abilities_disabled.values()))
        return "\n".join(disabled)
