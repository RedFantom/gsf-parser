# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
# UI imports
from tkinter import messagebox
# Own modules
from parsing.parser import Parser
from parsing.logstalker import LogStalker
from threading import Thread
from tools.utilities import get_temp_directory, get_screen_resolution
# File parsing
import os
import _pickle as pickle  # known as cPickle
# Screen parsing
import mss
import pynput
from PIL import Image
from datetime import datetime
from parsing.guiparsing import GSFInterface


class RealTimeParser(Thread):
    """
    Class to parse Galactic StarFighter in real-time. Manages LogStalker instance to gather all data
    and save it to a data dictionary, in realtime.db.
    """

    def __init__(
            self,
            character_db,
            character_data,
            exit_queue,
            spawn_callback=None,
            match_callback=None,
            file_callback=None,
            event_callback=None,
            screen_parsing_enabled=False,
            screen_parsing_features=None,
            data_queue=None,
            return_queue=None
    ):
        """
        :param character_db: Character database
        :param spawn_callback: Callback called with spawn_timing when a new spawn has been detected
        :param match_callback: Callback called with match_timing when a new match has been detected
        :param file_callback: Callback called with file_timing when a new file has been detected
        :param event_callback: Callback called with line_dict when a new event has been detected
        :param screen_parsing_enabled: boolean that enables screen parsing features
        :param screen_parsing_features: list of screen parsing features
        :param data_queue: Queue to communicate queries for data with
        :param return_queue: Queue to answer queries for data with
        :param exit_queue: Queue to make the RealTimeParser stop activities
        :param character_data: Character tuple with the character name and server to retrieve data with
        """
        Thread.__init__(self)

        """
        Attributes
        """
        # Callbacks
        self.spawn_callback = spawn_callback
        self.match_callback = match_callback
        self.file_callback = file_callback
        self.event_callback = event_callback
        # Settings
        self._screen_parsing_enabled = screen_parsing_enabled
        self._screen_parsing_features = screen_parsing_features
        # Queues
        self._data_queue = data_queue
        self._return_queue = return_queue
        self._exit_queue = exit_queue
        # Data
        self._character_data = character_data
        self._character_db = character_db
        self._realtime_db = {}
        self.diff = None

        """
        File parsing
        """
        # LogStalker
        self._stalker = LogStalker(watching_callback=self.file_callback)
        # Data attributes
        self.dmg_d, self.dmg_t, self.dmg_s, self._healing, self.abilities = 0, 0, 0, 0, {}
        self.active_id, self.active_ids = "", []
        self.hold, self.hold_list = 0, []
        self.player_name = ""
        self.is_match = False
        self.start_time = None
        self.lines = []

        """
        Screen parsing
        """
        self._mss = None
        self._kb_listener = None
        self._ms_listener = None
        self.setup_screen_parsing()
        self.ship = None
        resolution = get_screen_resolution()
        self._monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}
        self._interface = None

        """
        Data processing
        """
        self._file_name = os.path.join(get_temp_directory(), "realtime.db")
        self.read_data_dictionary()

    def setup_screen_parsing(self):
        """
        If it is enabled, set up the attribute objects with the correct parameters for use in the loop.
        """
        if not self._screen_parsing_enabled:
            return
        self._mss = mss.mss()
        self._kb_listener = pynput.keyboard.Listener(on_press=self._on_kb_press, on_release=self._on_kb_release)
        self._ms_listener = pynput.mouse.Listener(on_click=self._on_ms_press)
        file_name = self._character_db[self._character_data]["GUI"]
        self._interface = GSFInterface(file_name)

    def start_listeners(self):
        """
        Start the keyboard and mouse listeners
        """
        if not self._screen_parsing_enabled:
            return
        self._kb_listener.start()
        self._ms_listener.start()

    def stop_listeners(self):
        """
        Stop the keyboard and mouse listeners
        """
        if not self._screen_parsing_enabled:
            return
        self._kb_listener.stop()
        self._ms_listener.stop()

    """
    Data dictionary interaction
    """

    def save_data_dictionary(self):
        """
        Save the data dictionary from memory to pickle
        """
        with open(self._file_name, "wb") as fo:
            pickle.dump(self._realtime_db, fo)

    def read_data_dictionary(self):
        """
        Read the data dictionary with backwards compatibility
        """
        pass

    """
    Parsing processes
    """

    def update(self):
        """
        Perform all the actions required for a single loop cycle
        """
        now = datetime.now()
        # File parsing
        lines = self._stalker.get_new_lines()
        for line in lines:
            self.process_line(line)
        if not self.is_match:
            self.diff = datetime.now() - now
            return
        # Screen parsing
        screenshot = self._mss.grab(self._monitor)
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        self.process_screenshot(image)
        # Performance measurements
        self.diff = datetime.now() - now
        # print("[RealTimeParser] {}.{}".format(diff.seconds, diff.microseconds))

    def process_line(self, line):
        """
        Parse a single line dictionary and update the data attributes of the instance accordingly
        """
        # Skip any and all SetLevel or Infection events
        ignorable = ("SetLevel", "Infection")
        if any(to_ignore in line["ability"] for to_ignore in ignorable):
            return
        # Handle logins
        if line["source"] == line["destination"] and "@" in line["source"] and "Login" in line["ability"]:
            self.player_name = line["source"][1:]  # Do not store @
            print("[RealTimeParser] Login: {}".format(self.player_name))
            if self.player_name != self._character_data[1]:
                messagebox.showerror(
                    "Error",
                    "Another character name than the one provided was detected. The GSF Parser cannot continue."
                )
                raise ValueError(
                    "Invalid character name in CombatLog. Expected: {}, Received: {}".format(
                        self._character_data[1], self.player_name
                    ))
        # First check if this is still a match event
        if self.is_match and ("@" in line["source"] or "@" in line["destination"]):
            print("[RealTimeParser] Match end.")
            self.start_time = None
            # No longer a match
            self.is_match = False
            self.lines.clear()
            return
        # Handle out-of-match events
        if not self.is_match:
            # Check if this event is still not in-match
            if "@" in line["source"] or "@" in line["destination"]:
                return
            else:  # Valid match event
                print("[RealTimeParser] Match start.")
                self.start_time = line["time"]
                self.is_match = True
                # Call the new match callback
                if callable(self.match_callback):
                    self.match_callback()
        # Handle changes of player ID (new spawns)
        if line["source"] != self.active_id and line["destination"] != self.active_id:
            self.active_id = ""
            # Call the spawn callback
            if callable(self.spawn_callback):
                self.spawn_callback()
        # Update player ID if possible and required
        if self.active_id == "" and line["source"] == line["destination"]:
            print("[RealTimeParser] New player ID: {}".format(line["source"]))
            self.active_id = line["source"]
            self.active_ids.append(line["source"])
            # Parse the lines that are on hold
            if self.hold != 0:
                self.hold = 0  # For recursive calls, this must be zero to prevent an infinite loop
                for line_dict in reversed(self.hold_list):
                    self.process_line(line_dict)
                self.hold_list.clear()

        # self.is_match must be True to get to this point

        # If no active ID is set, then this line must be put on hold
        if self.active_id == "":
            print("[RealTimeParser] Holding line.")
            self.hold_list.append(line)
            self.hold += 1
            return

        # Parse the line
        if line["amount"] == "":
            line["amount"] = "0"
        line["amount"] = int(line["amount"].replace("*", ""))
        if "Heal" in line["effect"]:
            self._healing += line["amount"]
        elif "Damage" in line["effect"]:
            if "Selfdamage" in line["ability"]:
                self.dmg_s += line["amount"]
            elif line["source"] in self.active_ids:
                self.dmg_d += line["amount"]
            else:
                self.dmg_t += line["amount"]

        if line["ability"] in self.abilities:
            self.abilities[line["ability"]] += 1
        else:  # line["ability"] not in self.abilities:
            self.abilities[line["ability"]] = 1
        if callable(self.event_callback):
            self.lines.append(line)
            line_effect = Parser.line_to_event_dictionary(line, self.active_id, self.lines)
            self.event_callback(line_effect, self.player_name, self.active_ids, self.start_time)

    def process_screenshot(self, screenshot):
        pass

    def run(self):
        """
        Run the loop and exit if necessary and perform error-handling for everything
        """
        self.start_listeners()
        while True:
            if not self._exit_queue.empty():
                break
            try:
                self.update()
            except Exception as e:
                # Errors are not often handled well in Threads
                print("RealTimeParser encountered an error: ", e)
                messagebox.showerror(
                    "Error",
                    "The real-time parsing back-end encountered an error while performing operations. Please report "
                    "this to the developer with the debug message below and, if possible, the full strack-trace. "
                    "\n\n{}".format(e)
                )
                raise
        # Perform closing actions
        self.stop_listeners()

    """
    Input listener callbacks
    """

    def _on_kb_press(self, key):
        if not self.is_match:
            return

    def _on_kb_release(self, key):
        if not self.is_match:
            return

    def _on_ms_press(self, x, y, button, pressed):
        if not self.is_match:
            return

    """
    General functions
    """

    def __enter__(self):
        return self

    def __exit__(self):
        self._exit_queue.put(True)

    def close(self):
        self.__exit__()

    def stop(self):
        self.__exit__()
