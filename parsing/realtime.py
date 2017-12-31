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
from parsing import vision


"""
These classes use data in a dictionary structure, dumped to a file in the temporary directory of the GSF Parser. This
dictionary contains all the data acquired by screen parsing and is stored with the following structure:

Dictionary structure:
data_dictionary[filename] = file_dictionary
file_dictionary[datetime_obj] = match_dictionary
match_dictionary[datetime_obj] = spawn_dictionary
spawn_dictionary["power_mgmt"] = power_mgmt_dict
    power_mgmt_dict[datetime_obj] = integer
spawn_dictionary["cursor_pos"] = cursor_pos_dict
    cursor_pos_dict[datetime_obj] = (x, y)
spawn_dictionary["tracking"] = tracking_dict
    tracking_dict[datetime_obj] = percentage
spawn_dictionary["clicks"] = clicks_dict
    clicks_dict[datetime_obj] = (left, right)
spawn_dictionary["keys"] = keys_dict
    keys_dict[datetime_obj] = keyname
spawn_dictionary["health"] = health_dict
    health_dict[datetime_obj] = (hull, shieldsf, shieldsr), all ints
spawn_dictionary["distance"] = distance_dict
    distance_dict[datetime_obj] = distance, int
spawn_dictionary["target"] = target_dict
    target_dict[datetime_obj] = (type, name)
spawn_dictionary["player_name"]
spawn_dictionary["ship"]
spawn_dictionary["ship_name"]


The realtime screen parsing uses Queue objects to communicate with other parts of the program. This is required because
the screen parsing takes place in a separate process for performance optimization and itself runs several threads to
monitor mouse and keyboard activity. This only gets recorded if the user is in a match, for otherwise it might be
possible to extract keylogs of different periods, and this would impose an extremely dangerous security issue. The Queue
objects used by the ScreenParser object are the following:

data_queue:         This Queue object receives any data from the realtime file parsing that is relevant for the
                    Screen Parser object. This includes data about the file watched, the match detected, the spawn
                    detected and other information. A list of expected data:
                    - ("file", str new_file_name)           new CombatLog watched
                    - ("match", True, datetime)             new match started
                    - ("match", False, datetime)            match ended
                    - ("spawn", datetime)                   new spawn
exit_queue:         This Queue object is checked to see if the ScreenParser should stop running or not. Because this
                    is running in a separate process, one cannot just simply call __exit__, all pending operations
                    must first be completed. A list of expected data:
                    - True                                  keep running
                    - False                                 exit ASAP
query_queue         This Queue object is for communication between the process and the realtime parsing thread in the
                    main process so the main process can receive data and display it in the overlay. A list of
                    expected data:
                    - "power_mgmt"                          return int power_mgmt
                    - "tracking"                            return int tracking degrees
                    - "health"                              return (hull, shieldsf, shieldsr), all ints
return_queue        The Queue in which the data requested from the query_queue is returned.
_internal_queue:    This Queue object is for internal communication between the various Thread objects running in this
                    Process object. A list of expected data:
                    - ("keypress", *args)                   key pressed
                    - ("mousepress", *args)                 mouse button pressed
                    - ("mouserelease", *args)               mouse button released
                    This is not yet a complete list.
"""


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
        self._spawn_callback = spawn_callback
        self._match_callback = match_callback
        self._file_callback = file_callback
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
        self._stalker = LogStalker(watching_callback=self._file_callback)
        # Data attributes
        self.dmg_d, self.dmg_t, self.dmg_s, self._healing, self.abilities = 0, 0, 0, 0, {}
        self.active_id, self.active_ids = "", []
        self.hold, self.hold_list = 0, []
        self.player_name = ""
        self.is_match = False
        self.start_match = None
        self.start_spawn = None
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
        self._coordinates = {}
        self.screen_data = {"tracking": 0.0, "health": (None, None, None), "power_mgmt": 4}

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
        self._coordinates = {
            "power_mgmt": self._interface.get_ship_powermgmt_coordinates(),
            "health": self._interface.get_ship_health_coordinates()
        }

    def start_listeners(self):
        """
        Start the keyboard and mouse listeners
        """
        if not self._screen_parsing_enabled or "Mouse and Keyboard" not in self._screen_parsing_features:
            return
        print("[RealTimeParser] Mouse and Keyboard parsing enabled.")
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

    def read_data_dictionary(self, create_new_database=False):
        """
        Read the data dictionary with backwards compatibility
        """
        if not os.path.exists(self._file_name) or create_new_database is True:
            messagebox.showinfo("Info", "The GSF Parser is creating a new real-time parsing database.")
            self.save_data_dictionary()
        try:
            with open(self._file_name, "rb") as fi:
                self._realtime_db = pickle.load(fi)
        except OSError:  # Inaccessible
            messagebox.showerror(
                "Error", "An OS Error occurred while trying to read the real-time parsing database. This likely means "
                         "that either it does not exist, or your user account does not have permission to access it.")
            self.read_data_dictionary(create_new_database=True)
        except EOFError:  # Corrupted
            messagebox.showerror(
                "Error", "The real-time parsing database has been corrupted, and cannot be restored. The GSF Parser "
                         "will create a new database, discarding all your old real-time parsing data.")
            self.read_data_dictionary(create_new_database=True)

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
        if self._screen_parsing_enabled:
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
            self.start_match = None
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
                self.start_match = line["time"]
                self.is_match = True
                # Call the new match callback
                if callable(self._match_callback):
                    self._match_callback()
        # Handle changes of player ID (new spawns)
        if line["source"] != self.active_id and line["destination"] != self.active_id:
            self.active_id = ""
            # Call the spawn callback
            if callable(self._spawn_callback):
                self._spawn_callback()
            self.start_spawn = line["time"]
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
            self.event_callback(line_effect, self.player_name, self.active_ids, self.start_match)

    def process_screenshot(self, screenshot):
        """
        Analyze a screenshot and take the data to save it
        """
        if "Tracking Penalty" in self._screen_parsing_features:
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
        self._realtime_db[self._stalker.file][self.start_match][self.start_spawn]["keys"][datetime.now()] = key

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

    """
    Callbacks
    """

    def file_callback(self, *args):
        self._realtime_db[self._stalker.file] = {}
        self._file_callback(*args)

    def match_callback(self):
        self._realtime_db[self._stalker.file][self.start_match] = {}
        self._match_callback()

    def spawn_callback(self):
        self._realtime_db[self._stalker.file][self.start_match][self.start_spawn] = {}
        self._spawn_callback()

    def create_keys(self):
        self._realtime_db[self._stalker.file][self.start_match][self.start_spawn] = {
            "keys": {},
            "clicks": {},
            "target": {},
            "distance": {},
            "health": {},
            "tracking": {},
            "cursor_pos": {},
            "power_mgmt": {},
            "player_name": None,
            "ship": None,
            "ship_name": None
        }
