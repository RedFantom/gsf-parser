"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import pickle as pickle
from datetime import datetime
# Packages
from pynput.mouse import Button
# Project Modules
from utils.directories import get_temp_directory
from utils.colors import *
from parsing.parser import Parser
from parsing.vision import *
from data import abilities
from parsing.shipstats import ShipStats
from parsing.patterns import PatternParser, Patterns


class FileHandler(object):
    """
    Reads the files generated by ScreenParser for file parsing, for
    information on the contents of the database, please consult the
    realtime.py docstring.
    """
    feature_strings = {
        "health": "Ship Health",
        "power_mgmt": "Power Management",
        "keys": "Mouse and Keyboard",
        "clicks": "Mouse and Keyboard",
        "tracking": "Tracking Penalty",
        "cursor_pos": "Tracking Penalty"
    }

    colors = {
        "primaries": "#ff6666",
        "secondaries": "#ff003b",
        "shields_front": "green",
        "shields_rear": "green",
        "hull": "brown",
        "systems": "#668cff",
        "engines": "#b380ff",
        "shields": "#8cac20",
        "copilot": "#17a3ff",
        "tracking": "#ffcc00",
        "wpower": "#ff9933",
        "epower": "#751aff",
        "power_mgmt": "darkblue",
    }

    keys = {
        "1": "systems",
        "2": "shields",
        "3": "engines",
        "4": "copilot",
        "F1": ("power_mgmt", 1),
        "F2": ("power_mgmt", 2),
        "F3": ("power_mgmt", 3),
        "F4": ("power_mgmt", 4)
    }

    health_colors = {
        None: "grey",
        0: "black",
        25: "red",
        50: "orange",
        75: "yellow",
        100: "green",
        125: "blue"
    }

    power_mgmt_colors = {
        1: "orange",
        2: "cyan",
        3: "purple",
        4: "darkblue",
        None: "black"
    }

    click_colors = {
        "primaries": "#ff7070",
        "secondaries": "#ff5179",
        "engines": "#c9a5ff",
        "shields": "#c0d86e",
        "systems": "#9bb4ff",
        "copilot": "#77c3f4"
    }

    @staticmethod
    def get_dictionary_key(dictionary, timing, value=False):
        """
        Returns a dictionary key where the key is a datetime object.
        This is necessary because datetime comparisons do not work
        reliably.
        """
        if not isinstance(dictionary, dict):
            raise ValueError()
        if not isinstance(timing, datetime):
            raise ValueError()
        for key, val in dictionary.items():
            if not isinstance(key, datetime):
                continue
            if key == timing:
                if value:
                    return val
                return key
        return None

    @staticmethod
    def get_dictionary_key_secondsless(dictionary, timing):
        """
        Retrieve an item from a dictionary with a datetime instance as
        key, but ignoring seconds. By ignoring seconds, the chances of
        finding a matching value is increased and reliability of
        finding results is thus higher.

        This was mostly required for earlier versions of screen parsing
        where timing was not very accurate.
        """
        # The match_dt as received is not found in the dictionary, so further searching is required
        # First, searching starts by removing the seconds from the match_dt
        timing_secondsless = timing.replace(second=0, microsecond=0)
        # Now we build a dictionary that also has secondsless keys
        dictionary_secondsless_keys = \
            {key.replace(second=0, microsecond=0): value for key, value in dictionary.items()}
        # Now we attempt to match the secondsless key in the secondsless file_dict
        correct_key = FileHandler.get_dictionary_key(dictionary_secondsless_keys, timing_secondsless)
        if correct_key:
            # We have found the correct key for the match
            return correct_key
        return None

    @staticmethod
    def get_spawn_dictionary(data, file_name, match_dt, spawn_dt):
        """
        Function to get the data dictionary for a spawn based on a file
        name, match datetime and spawn datetime. Uses a lot of code to
        make the searching as reliable as possible.
        """
        print("[FileHandler] Spawn data requested for: {}/{}/{}".format(file_name, match_dt, spawn_dt))
        # First check if the file_name is available
        if file_name not in data:
            return "Not available for this file.\n\nScreen parsing results are only available for spawns in files " \
                   "which were spawned while screen parsing was enabled and real-time parsing was running."

        file_dt = Parser.parse_filename(file_name)
        if file_dt is None:
            return "Not available for this file.\n\nScreen parsing results are not supported for file names which do " \
                   "not match the original Star Wars - The Old Republic CombatLog file name format."
        file_dict = data[file_name]
        # Next up comes the checking of datetimes, which is slightly more complicated due to the fact that even equal
        # datetime objects with the == operators, are not equal with the 'is' operator
        # Also, for backwards compatibility, different datetimes must be supported in this searching process
        # Datetimes always have a correct time, but the date is not always the same as the filename date
        # If this is the case, the date is actually set to January 1 1900, the datetime default
        # Otherwise the file name of the CombatLog must have been altered
        match_dict = None
        for key, value in file_dict.items():
            if key.hour == match_dt.hour and key.minute == match_dt.minute:
                match_dict = value
        if match_dict is None:
            return "Not available for this match\n\nScreen parsing results are only available for spawns " \
                   "in matches which were spawned while screen parsing was enabled and real-time parsing " \
                   "was running"
        # Now a similar process starts for the spawns, except that seconds matter here.
        spawn_dict = None
        for key, value in match_dict.items():
            if key is None:
                # If the key is None, something weird is going on, but we do not want to throw any data away
                # This may be caused by a bug in the ScreenParser
                # For now, we reset key to a sensible value, specifically the first moment the data was recorded, if
                # that's possible. If not, we'll skip it.
                try:
                    key = list(value[list(value.keys())[0]].keys())[0]
                except (KeyError, ValueError, IndexError):
                    continue
            if key.hour == spawn_dt.hour and key.minute == spawn_dt.minute and key.second == spawn_dt.second:
                spawn_dict = value
        if spawn_dict is None:
            return "Not available for this spawn\n\nScreen parsing results are not available for spawns which " \
                   "were not  spawned while screen parsing was enabled and real-time parsing were running."
        print("Retrieved data: {}".format(spawn_dict))
        return spawn_dict

    @staticmethod
    def get_data_dictionary(name="realtime.db"):
        """Read the real-time parsing data dictionary from"""
        file_name = os.path.join(get_temp_directory(), name)
        if not os.path.exists(file_name):
            return {}
        with open(file_name, "rb") as fi:
            data = pickle.load(fi)
        return data

    @staticmethod
    def get_markers(screen_dict: dict, spawn_list: list, active_ids: list):
        """
        Generate a dictionary of markers to insert into the TimeLine
        widget of the StatsFrame. This marker dictionary is built-up
        as follows:
        {category: [(args, kwargs)]}
        The args and kwargs are passed onto the create_marker function
        for the TimeLine widget.
        """
        if "ship" in screen_dict and screen_dict["ship"] is not None:
            stats = ShipStats(screen_dict["ship"], None, None)
        else:
            stats = None
        results = {}
        start_time = Parser.line_to_dictionary(spawn_list[-1])["time"]
        results.update(FileHandler.get_weapon_markers(screen_dict, spawn_list))
        results.update(FileHandler.get_health_markers(screen_dict, start_time))
        results.update(FileHandler.get_tracking_markers(screen_dict, stats))
        results.update(FileHandler.get_power_mgmt_markers(screen_dict, start_time))
        results.update(FileHandler.get_ability_markers(spawn_list, stats))
        results.update(FileHandler.get_engine_boost_markers(screen_dict, start_time))
        return results

    @staticmethod
    def get_features_string(file_name, match_time, spawn_time):
        """
        Build a string with all the features that were enabled for a
        certain spawn to be displayed in the StatsFrame.
        """
        # Get the screen parsing data dictionary
        realtime_data = FileHandler.get_data_dictionary()
        screen_dict = FileHandler.get_spawn_dictionary(realtime_data, file_name, match_time, spawn_time)
        if isinstance(screen_dict, str):
            return screen_dict
        # Generate the features string
        string = "Features enabled: "
        for feature, f_string in FileHandler.feature_strings.items():
            if f_string in string:
                continue
            if feature in screen_dict and len(screen_dict[feature]) != 0:
                string += f_string + ", "
        if string.endswith(", "):
            string = string[:-2]
        elif string.endswith(": "):
            string = "No features enabled for screen parsing in this match."
        return string

    @staticmethod
    def get_weapon_markers(dictionary, spawn):
        """
        Parse the given screen dictionary and spawn line list to
        generate markers for the TimeLine for the Primary Weapon
        and Secondary Weapon categories.
        The clicks are parsed into lightly coloured markers, while
        ability activations (hits) are parsed into bright markers.
        """
        # Retrieve pre-requisite data
        player_list = Parser.get_player_id_list(spawn)
        # Create lists that will hold markers
        results = {"primaries": [], "secondaries": []}
        """
        File Data
        """
        # Loop over contents of spawn
        for line in spawn:
            if isinstance(line, str):
                line = Parser.line_to_dictionary(line)
            # Retrieve the ability of the line
            ability = line["ability"]
            # If the ability was self-targeted, then it is not a weapon
            # If the ability was not activated by self, then it is not damage dealt
            if line["source"] == line["target"] or line["source"] not in player_list:
                continue
            # Determine the category of this ability
            if ability in abilities.primaries:
                category = "primaries"
            elif ability in abilities.secondaries:
                category = "secondaries"
            else:
                # Ability is not a weapon
                continue
            # Generate the arguments for the marker creation
            start = FileHandler.datetime_to_float(line["time"])
            args = (category, start, start + 1 / 60)
            # Save the marker
            results[category].append((args, {"background": FileHandler.colors[category]}))
        # If screen data does not contain mouse data, then return the
        # markers created so far
        if "clicks" not in dictionary or len(dictionary["clicks"]) == 0:
            return results
        """
        Screen Data
        """
        # This dictionary will hold when each button press was started
        buttons = {Button.left: None, Button.right: None}
        # This dictionary is for backwards compatibility, see loop
        buttons_press = {Button.left: False, Button.right: False}
        # Start looping over the data found in the screen dictionary
        for time, data in sorted(dictionary["clicks"].items()):
            # Backwards compatibility
            if isinstance(data, tuple):
                # The current interface for screen parsing
                button, press = data
                # Also for backwards-compatibility
                press = "press" in press if isinstance(press, str) else press
            else:
                # An older version of the interface saved only the button as value for the dictionary
                # This means that determining if the button was pressed has to be determined manually
                button = data
                # Does not support any other buttons than right and left
                if button not in (Button.left, Button.right):
                    continue
                # Update if the button was pressed
                buttons_press[button] = not buttons_press[button]
                press = buttons_press[button]
            # Determine the category of the button press
            category = "primaries" if button == Button.left else ("secondaries" if button == Button.right else None)
            if category is None:
                continue
            # If the button was actually pressed, then save the time for use later
            if press is True:
                buttons[button] = time
            # If the button was already pressed, then a new marker can be created
            else:
                results[category].append(
                    ((category, buttons[button], time), {"background": FileHandler.click_colors[category]})
                )
        return results

    @staticmethod
    def get_health_markers(screen_dict, start_time):
        """
        Return health markers for TimeLine
        """
        if "health" not in screen_dict:
            return {}
        sub_dict = screen_dict["health"]
        categories = ["hull", "shields_f", "shields_r"]
        health = {key: (None, None) for key in categories}
        results = {key: [] for key in categories}
        for time, (hull, shields_f, shields_r) in sorted(sub_dict.items()):
            new_values = {key: (time, locals()[key] if key in locals() else 0) for key in categories}
            for category in categories:
                if health[category][1] != new_values[category][1]:
                    start = health[category][0]
                    start = start if start is not None else start_time
                    finish = time
                    args = (category, FileHandler.datetime_to_float(start), FileHandler.datetime_to_float(finish))
                    kwargs = {"background": FileHandler.health_colors[health[category][1]]}
                    results[category].append((args, kwargs))
        return results

    @staticmethod
    def get_power_mgmt_markers(screen_dict, start_time):
        """
        Build a dictionary of markers for the power management state.
        Can work in either of two ways:
        - Mouse and Keyboard parsing (keyboard input)
        - Power Management parsing (screenshots)
        """
        categories = ["power_mgmt"]
        power_mgmt = (None, None)
        results = {key: [] for key in categories}
        sub_dict = screen_dict["keys"]
        # Keyboard input parsing
        if len(sub_dict) != 0:
            power_mode = 4
            previous = start_time
            for time, (key, pressed) in FileHandler.screen_dict_keys_generator(screen_dict):
                if pressed is False or key not in FileHandler.keys:
                    continue
                result = FileHandler.keys[key]
                if not isinstance(result, tuple) or len(result) != 2:
                    continue
                category, mode = result
                if power_mode == mode:
                    continue
                args = ("power_mgmt", FileHandler.datetime_to_float(previous), FileHandler.datetime_to_float(time))
                previous = time
                kwargs = {"background": FileHandler.power_mgmt_colors[power_mode]}
                power_mode = mode
                results["power_mgmt"].append((args, kwargs))
        # Screen parsing
        else:
            sub_dict = screen_dict["power_mgmt"]
            for time, value in sorted(sub_dict.items()):
                if power_mgmt[0] != value:
                    start = power_mgmt[0]
                    start = start if start is not None else start_time
                    finish = time
                    args = ("power_mgmt", FileHandler.datetime_to_float(start), FileHandler.datetime_to_float(finish))
                    kwargs = {"background": FileHandler.power_mgmt_colors[value]}
                    results["power_mgmt"].append((args, kwargs))
                    power_mgmt = (time, value)
        return results

    @staticmethod
    def get_tracking_markers(screen_dict, ship_stats):
        """
        Generates a dictionary of markers that indicate tracking
        penalty. Attempts to read the tracking penalty data from the
        ship statistics if possible.
        """
        # Color Processing
        base_color = color_hex_to_tuple(FileHandler.colors["tracking"])
        tuple_to_hex = color_tuple_to_hex
        # This dictionary will store the markers in an array for easy
        # processing in the calling function.
        results = {"tracking": []}
        stats = {
            "firing_arc": 40,  # degrees
            "penalty": 0,  # percentpoint per degree
            "upgrade_c": 0  # the upgrade constant
        }
        # Read build data if possible
        if ship_stats is not None and "PrimaryWeapon" in ship_stats:
            # Only the first primary weapon is currently supported.
            # TODO: Implement (1) key parsing here and thus support
            # TODO: The use of multiple primary weapons
            # TODO: Stretch: Support for Rocket Pods and Railguns
            primary_weapon_data = ship_stats["PrimaryWeapon"]
            # Tracking penalty retrieval
            if "trackingAccuracyLoss" in primary_weapon_data:
                stats["penalty"] = primary_weapon_data["trackingAccuracyLoss"]
            if "Weapon_Firing_Arc" in primary_weapon_data:
                stats["firing_arc"] = primary_weapon_data["Weapon_Firing_Arc"]
            if "Weapon_Tracking_Bonus" in primary_weapon_data:
                stats["upgrade_c"] = primary_weapon_data["Weapon_Tracking_Bonus"]
        # Loop over screen parsing cursor position data
        for key, value in sorted(screen_dict["cursor_pos"].items()):
            degrees = get_tracking_degrees(get_distance_from_center(value))
            degrees = max(min(degrees, stats["firing_arc"]), 1)
            # If tracking penalty constants are available
            if stats["penalty"] != 0:
                # Calculate the actual tracking penalty instead of using
                # the distance from the cursor to the screen center
                tracking_penalty = get_tracking_penalty(
                    degrees, stats["penalty"], stats["upgrade_c"], stats["firing_arc"])
                # Tracking penalty is now a float (percentage / 100)
                darkened = color_darken(base_color, tracking_penalty)
                background = tuple_to_hex(darkened)
            else:
                # Base the marker on the degrees from center instead
                darkened = color_darken(
                    base_color, stats["firing_arc"] / degrees)
                background = tuple_to_hex(darkened)
            # Create the marker data
            start = FileHandler.datetime_to_float(key)
            finish = start + 0.01
            args = ("tracking", start, finish)
            kwargs = {"background": background}
            results["tracking"].append((args, kwargs))
        return results

    @staticmethod
    def get_ability_markers(spawn_list, ship_stats):
        """
        Parse a spawn list of lines and take the Engine, Shield, Systems
        and CoPilot ability activations and create markers for them to
        be put in the TimeLine.
        """
        # TODO: Use ship_statistics to create availability markers
        categories = ["engines", "shields", "copilot", "systems"]
        player_id_list = Parser.get_player_id_list(spawn_list)
        results = {key: [] for key in categories}
        # Activation markers
        for line in spawn_list:
            if not isinstance(line, dict):
                line = Parser.line_to_dictionary(line)
            ability = line["ability"]
            if (line["source"] != line["target"] or line["source"] not in player_id_list or
                    "AbilityActivate" not in line["effect"]):
                continue
            if ability in abilities.copilots:
                category = "copilot"
            elif ability in abilities.shields:
                category = "shields"
            elif ability in abilities.systems:
                category = "systems"
            elif ability in abilities.engines:
                category = "engines"
            else:
                continue
            start = FileHandler.datetime_to_float(line["time"])
            args = ("abilities", start, start + 1/60)
            kwargs = {"background": FileHandler.colors[category]}
            results[category].append((args, kwargs))
        return results

    @staticmethod
    def get_engine_boost_markers(screen_dict, start_time):
        """
        Build a marker dictionary for engine boosting (indicated by the
        Space key). Only available with Mouse and Keyboard feature.
        """
        if "keys" not in screen_dict or len(screen_dict["keys"]) == 0:
            return dict()
        # Feature was enabled, so start building markers
        start = None
        results = {"boosting": []}
        for time, (key, pressed) in FileHandler.screen_dict_keys_generator(screen_dict):
            # Use default boost key
            if key != "space":
                continue
            if pressed is True:
                start = time
                continue
            # pressed is False
            args = ("boosting", FileHandler.datetime_to_float(start), FileHandler.datetime_to_float(time))
            kwargs = {"background": FileHandler.colors["engines"]}
            results["boosting"].append((args, kwargs))
        return results

    @staticmethod
    def datetime_to_float(date_time_obj):
        """Convert a datetime object to a float value"""
        if not isinstance(date_time_obj, datetime):
            raise TypeError("date_time_obj not of datetime type but {}".format(repr(date_time_obj)))
        return float(
            "{}.{}{}".format(date_time_obj.minute, (int((date_time_obj.second / 60) * 100)), date_time_obj.microsecond))

    @staticmethod
    def screen_dict_keys_generator(screen_dict):
        for time, data in sorted(screen_dict["keys"].items()):
            if isinstance(data, tuple):
                key, pressed = data
            else:
                key = data
                pressed = True
            pressed = "pressed" in pressed if isinstance(pressed, str) else pressed
            yield time, (key, pressed)
