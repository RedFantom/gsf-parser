"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
import os
import sys
from time import sleep
import traceback
from typing import Any
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
from data.keys import KEYS
from data.abilities import REPUBLIC_SHIPS
from data import abilities
from data.maps import MAP_TYPE_NAMES, MAP_NAMES
# network Modules
from network.minimap.client import MiniMapClient
# Parsing Modules
from parsing.gsfinterface import GSFInterface
from parsing.guiparsing import get_player_guiname
from parsing.parser import Parser
from children.pointer import PointerParser
from parsing.realtimedb import RealTimeDB
from children.rgb import RGBController
from parsing.post import PostParser
from parsing.shipstats import ShipStats
from children.speed import SpeedParser
from children.delay import DelayParser
from parsing import vision
# Processes or Threads
# Utility Modules
from utils.utilities import get_screen_resolution
from utils.utilities import get_cursor_position
from utils.window import Window
import variables


def pair_wise(iterable: (list, tuple)):
    """Create generator to loop over iterable in pairs"""
    return list(zip(*tuple(iterable[i::2] for i in range(2))))


def printf(string: str):
    """Write a string to stdout and flush"""
    sys.stdout.write(string + "\n")
    sys.stdout.flush()


class RealTimeParser(object):
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
        self._exit_queue = Queue()
        self._overlay_string_q = Queue()
        self._perf_string_q = Queue()
        # Data
        self._char_i = character_data
        self._char_db = character_db
        self._char_data = self._char_db[self._char_i]
        self._realtime_db = RealTimeDB()

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
        if "Power Regeneration Delays" in self._screen_features:
            self._timer_parser = DelayParser()
        self._speed_parser = None
        if "Engine Speed" in self._screen_features:
            self._speed_parser = SpeedParser()
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
        file_name = get_player_guiname(self._char_data["Name"], self._char_data["Server"])
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

    def update_rgb_keyboard(self, line: dict):
        """Pass data to the RGB Keyboard Handler"""
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
            ship = REPUBLIC_SHIPS[ship]
        if self._screen_enabled is False:
            return
        ship_objects = self._char_db[self._char_i]["Ship Objects"]
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
        if self._speed_parser is not None:
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

    @property
    def _overlay_string(self) -> str:
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
        if self._speed_parser is not None:
            string += self._speed_parser.string
        string += "\nLast updated: {}".format(datetime.now().strftime("%M:%S"))
        return string.strip()

    @property
    def tracking_string(self) -> str:
        if "Tracking Penalty" not in self._screen_features:
            return ""
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
