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
from variables import settings
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
from tools.utilities import get_cursor_position
from parsing.shipstats import ShipStats
from parsing.keys import keys
from parsing.ships import ships, Ship
from parsing.abilities import rep_ships
from time import sleep

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
            ships_db,
            companions_db,
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
        self._screen_parsing_features = screen_parsing_features if screen_parsing_features is not None else []
        # Queues
        self._data_queue = data_queue
        self._return_queue = return_queue
        self._exit_queue = exit_queue
        # Data
        self._character_data = character_data
        self._character_db = character_db
        self._realtime_db = {}
        self.diff = None
        self.ships_db = ships_db
        self.companions_db = companions_db

        """
        File parsing
        """
        # LogStalker
        self._stalker = LogStalker(watching_callback=self.file_callback)
        # Data attributes
        self.dmg_d, self.dmg_t, self.dmg_s, self._healing, self.abilities = 0, 0, 0, 0, {}
        self.active_id, self.active_ids = "", []
        self.hold, self.hold_list = 0, []
        self.player_name = "Player Name"
        self.is_match = False
        self.start_match = None
        self.start_spawn = None
        self.lines = []
        self.primary_weapon = False
        self.secondary_weapon = False
        self.scope_mode = False

        """
        Screen parsing
        """
        self._mss = None
        self._kb_listener = None
        self._ms_listener = None
        self.setup_screen_parsing()
        self.ship = None
        self.ship_stats = None
        resolution = get_screen_resolution()
        self._monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}
        self._interface = None
        self._coordinates = {}
        self.screen_data = {"tracking": "", "health": (None, None, None), "power_mgmt": 4}
        self._resolution = resolution
        self._pixels_per_degree = 10

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
        self._pixels_per_degree = self._interface.get_pixels_per_degree()

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
        if self.diff.total_seconds() < 0.5:
            sleep(0.5 - self.diff.total_seconds())
        # print("[RealTimeParser] {}.{}".format(diff.seconds, diff.microseconds))

    """
    FileParser
    """

    def process_line(self, line):
        """
        Parse a single line dictionary and update the data attributes of the instance accordingly
        """
        # Skip any and all SetLevel or Infection events
        ignorable = ("SetLevel", "Infection")
        if any(to_ignore in line["ability"] for to_ignore in ignorable):
            return
        # Handle logins
        if line["source"] == line["destination"] and "@" in line["source"] and "Login" in line["ability"] and \
                ":" not in line["source"]:
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
            self.process_login()
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
                self.match_callback()
        # Handle changes of player ID (new spawns)
        if line["source"] != self.active_id and line["destination"] != self.active_id:
            self.active_id = ""
            # Call the spawn callback
            self.start_spawn = line["time"]
            self.spawn_callback()
            self.ship = None
            self.ship_stats = None
            self.primary_weapon, self.secondary_weapon, self.scope_mode = False, False, False
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

        """
        Special ability processing
        """
        if line["ability"] == "Scope Mode":
            self.scope_mode = not self.scope_mode
        elif line["ability"] == "Primary Weapon Swap":
            self.primary_weapon = not self.primary_weapon
        elif line["ability"] == "Secondary Weapon Swap":
            self.secondary_weapon = not self.secondary_weapon
        """
        Ship processing
        """
        if self.ship is None:
            abilities = Parser.get_abilities_dict(self.lines)
            ship = Parser.get_ship_for_dict(abilities)
            if len(ship) != 1:
                return
            ship = ship[0]
            if self._character_db[self._character_data]["Faction"].lower() == "republic":
                ship = rep_ships[ship]
            if self._screen_parsing_enabled is False:
                return
            self.ship = self._character_db[self._character_data]["Ship Objects"][ship]
            args = (self.ship, self.ships_db, self.companions_db)
            self.ship_stats = ShipStats(*args)
        return

    """
    ScreenParser
    """

    def process_screenshot(self, screenshot):
        """
        Analyze a screenshot and take the data to save it
        """
        now = datetime.now()
        if self._stalker.file not in self._realtime_db:
            print("[RealTimeParser] Processing screenshot while file is not in DB yet.")
            return
        elif self.start_match not in self._realtime_db[self._stalker.file]:
            print("[RealTimeParser] Processing screenshot while match is not in DB yet.")
            return
        elif self.start_spawn not in self._realtime_db[self._stalker.file][self.start_match]:
            print("[RealTimeParser] Processing screenshot while spawn is not in DB yet.")
            return
        spawn_dict = self._realtime_db[self._stalker.file][self.start_match][self.start_spawn]
        """
        Tracking penalty
        
        Retrieves cursor coordinates and saves the following:
        - Absolute cursor position
        - Relative cursor position
        - Tracking penalty percentage
        """
        if "Tracking penalty" in self._screen_parsing_features:
            # Absolute cursor position
            mouse_coordinates = get_cursor_position()
            spawn_dict["cursor_pos"][now] = mouse_coordinates
            # Relative cursor position
            distance = vision.get_distance_from_center(mouse_coordinates, self._resolution)
            spawn_dict["distance"][now] = distance
            # Tracking penalty
            degrees = vision.get_tracking_degrees(distance, self._pixels_per_degree)
            if self.ship_stats is not None:
                constants = self.get_tracking_penalty()
                penalty = vision.get_tracking_penalty(degrees, *constants)
            else:
                penalty = None
            spawn_dict["tracking"][now] = penalty
            # Set the data for the string building
            unit = "°" if penalty is None else "%"
            string = "{:.1f}{}".format(degrees if penalty is None else penalty, unit)
            self.screen_data["tracking"] = string
        """
        Power Management
        """
        if "Power Management" in self._screen_parsing_features:
            power_mgmt = vision.get_power_management(screenshot, *self._coordinates["power_mgmt"])
            self.screen_data["power_mgmt"] = power_mgmt
        """
        Ship Health
        """
        if "Ship Health " in self._screen_parsing_features:
            health_hull = vision.get_ship_health_hull(screenshot)
            (health_shields_f, health_shields_r) = vision.get_ship_health_shields(
                screenshot, self._coordinates["health"])
            self.set_for_current_spawn("health", now, (health_hull, health_shields_f, health_shields_r))

        # Finally, save data
        self._realtime_db[self._stalker.file][self.start_match][self.start_spawn] = spawn_dict
        self.save_data_dictionary()

    def get_tracking_penalty(self):
        """
        Determine the correct weapon to determine the tracking penalty for and then retrieve that data
        """
        if self.ship_stats is None:
            print("[RealTimeParser] get_tracking_penalty was called while ship_stats is None")
            return 0, 0  # Fail silently
        primaries = ["PrimaryWeapon", "PrimaryWeapon2"]
        secondaries = ["SecondaryWeapon", "SecondaryWeapon2"]
        if self.scope_mode is True:
            weapon_key = secondaries[int(self.secondary_weapon)]
        else:  # self.scope_mode is False
            weapon_key = primaries[int(self.primary_weapon)]
        if weapon_key not in self.ship_stats:
            print("[RealTimeParser] Failed to retrieve statistics for weapon '{}' on {}".format(weapon_key, self.ship))
            return 0, 0, 0
        firing_arc = self.ship_stats[weapon_key]["Weapon_Firing_Arc"]
        tracking_penalty = self.ship_stats[weapon_key]["trackingAccuracyLoss"]
        if "Weapon_Tracking_Bonus" not in self.ship_stats[weapon_key]:
            upgrade_constant = self.ship_stats[weapon_key]["Weapon_Tracking_Bonus"]
        else:
            upgrade_constant = 0
        return tracking_penalty, upgrade_constant, firing_arc

    """
    TimerParser
    """

    def process_login(self):
        """
        TimerParser attempts for ten seconds to determine if there is a spawn timer available on the screen
        """
        if "Spawn Timer" not in self._screen_parsing_features:
            return

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
        if not self.is_match or key not in keys:
            return
        self.set_for_current_spawn("keys", datetime.now(), (keys[key], True))

    def _on_kb_release(self, key):
        if not self.is_match or key not in keys:
            return
        self.set_for_current_spawn("keys", datetime.now(), (keys[key], False))

    def _on_ms_press(self, x, y, button, pressed):
        if not self.is_match:
            return
        self.set_for_current_spawn("clicks", datetime.now(), (pressed, button))

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
        if callable(self._match_callback):
            self._match_callback()

    def spawn_callback(self):
        self._realtime_db[self._stalker.file][self.start_match][self.start_spawn] = {}
        self.create_keys()
        if callable(self._spawn_callback):
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

    def set_for_current_spawn(self, *args):
        if len(args) == 2:
            self._realtime_db[self._stalker.file][self.start_match][self.start_spawn][args[0]] = args[1]
        elif len(args) == 3:
            self._realtime_db[self._stalker.file][self.start_match][self.start_spawn][args[0]][args[1]] = args[2]
        else:
            raise ValueError()

    """
    String manipulation
    """

    @property
    def overlay_string(self):
        if self.is_match is False and settings["realtime"]["overlay_when_gsf"]:
            return ""
        overlay_string = ""
        tracking = self.get_tracking_string()
        parsing = self.get_parsing_string()
        power = self.get_power_mgmt_string()
        for string in [parsing, tracking, power]:
            overlay_string += string
        return overlay_string

    def get_tracking_string(self):
        if "Tracking penalty" not in self._screen_parsing_features:
            return ""
        return "Tracking: {}\n".format(self.screen_data["tracking"])

    def get_parsing_string(self):
        string = "Damage Dealt: {}\n" \
                 "Damage Taken: {}\n" \
                 "Selfdamage: {}\n" \
                 "Healing Recv: {}\n".format(
            self.dmg_d, self.dmg_t, self.dmg_s, self._healing
        )
        return string

    def get_power_mgmt_string(self):
        return "Power Management: {}\n".format(self.screen_data["power_mgmt"])

    def get_timer_string(self):
        pass

    def get_health_string(self):
        pass
