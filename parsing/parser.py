# A new parsing engine built by RedFantom based on principles from parse.py and realtime.py
# Is capable of parsing files as well as realtime parsing
import re
import os
from datetime import datetime
from tkinter.ttk import Frame
from queue import Queue
# Own modules
from parsing.screen import ScreenParser
from parsing.stalking_alt import LogStalker
from parsing.screen import ScreenParser
from parsing import abilities, effects, durations
# Variables
import variables


class Parser(object):
    """
    A Parsing engine that can sequentially parse CombatLog lines and supports staticmethods for parsing individual
    spawns and matches to keep some backwards compatibility with the functions found in parse.py. Replaces the Parsing
    engine found in realtime.py.

    Capabilities:
    - Determine player name and IDs
    - Count damage and healing
    - Count hits and critical hits
    - Parse screenshots separately
    - In real-time mode, determine hits/misses
    - Determine ship and components
    - Count ability usage
    - Save build data for a match and read it when required
    - Manage a spawn events Treeview
    """

    # Line constants
    LINE_NUMBER = "number"
    LINE_ABILITY = "ability"
    LINE_EFFECT = "effect"

    def __init__(self, file_name, events_view=None, line_queue=None, character_data=None, real_time=False,
                 screen_parsing=False):
        """
        :param events_view: An EventsView widget with .timeline and .eventslist attributes
        :param line_queue: Queue object (or object with .put()) to pass lines parsed to
        :param character_data: Character dictionary with "Ship Objects" keys
        :param file_name: The name of the log being parsed (e.g. to collect data from FileHandler)
        :param mode: The mode the new Parser is started in
        """
        # Perform type checks
        if not isinstance(events_view, Frame):
            raise ValueError("events_view argument is not a ttk.Frame")
        if not isinstance(line_queue, Queue):
            raise ValueError("line_queue argument is not a Queue")
        if not isinstance(character_data, dict):
            raise ValueError("character_data argument is not a dict")
        # Attributes required for ScreenParser
        self.sp_data_queue = None if not screen_parsing else Queue()
        self.sp_exit_queue = None if not screen_parsing else Queue()
        self.sp_query_queue = None if not screen_parsing else Queue()
        self.sp_return_queue = None if not screen_parsing else Queue()
        # Create attributes
        self.events_view = events_view
        self.line_queue = line_queue
        self.character_data = character_data
        self.log_stalker = Parser.setup_log_stalker() if real_time is True else None
        self.screen_parser = self.setup_screen_parser() if screen_parsing is True else None

        # Settings for this object
        self.file_name = file_name

        # Initiate the data processing
        self.process_file()

    def process_file(self):
        """
        Split the file into matches and spawns
        """
        pass

    def process_line(self, line):
        pass

    def setup_screen_parser(self):
        """
        Sets up a ScreenParser object with the correct arguments and keyword arguments
        """
        args = (self.sp_data_queue, self.sp_exit_queue, self.sp_query_queue, self.sp_return_queue)
        kwargs = Parser.get_screen_parser_kwargs()
        self.screen_parser = ScreenParser(*args, **kwargs)
        return self.screen_parser

    @staticmethod
    def setup_log_stalker():
        """
        Sets up a LogStalker
        """
        log_stalker = LogStalker()
        return log_stalker

    @staticmethod
    def get_screen_parser_kwargs():
        """
        Return a dictionary of keyword arguments for a ScreenParser instance based on the settings for screen parsing
        """
        feature_list = variables.settings_obj["realtime"]["screenparsing_features"]
        arguments = {
            "rgb": False,
            "cooldowns": None,
            "powermgmt": "Power management" in feature_list,
            "health": "Ship health" in feature_list,
            "name": "Enemy name and ship type" in feature_list,
            "ttk": "Time to kill" in feature_list,
            "tracking": "Tracking penalty" in feature_list,
            "ammo": "Ammunition" in feature_list,
            "distance": "Distance to target" in feature_list,
            "cursor": "Mouse pointer location and state" in feature_list
        }
        return arguments

    @staticmethod
    def line_to_dictionary(line):
        """
        Turn a line into a dictionary that makes it easier to parse
        :param line: A GSF CombatLog line
        :return: dictionary for line, or None if failed
        """
        if isinstance(line, dict):
            return line
        line_pattern = r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \((.*?)\)'
        pattern = re.compile(line_pattern)
        group = pattern.match(line) if isinstance(line, str) else pattern.match(line.decode('cp1252'))
        if not hasattr(group, "groups"):
            return None
        group_tuple = group.groups()
        colnames = ('time', 'source', 'target', 'ability', 'effect', 'amount')
        log = dict(list(zip(colnames, group_tuple)))
        if not log['amount'] == '':
            log['amount'] = log['amount'].split(None, 1)[0]
        log["time"] = datetime.strptime(log["time"], "%H:%M:%S.%f")
        log["target"] = log["target"] if log["target"].strip() != "" else "System"
        log["destination"] = log["target"]
        log["ability"] = log["ability"].split("{", 1)[0].strip()
        log["line"] = line
        if log["target"] == log["source"] and log["ability"] in abilities.secondaries:
            log["target"] = "Launch Projectile"
        return log

    @staticmethod
    def line_to_event_dictionary(line, active_id, lines):
        """
        Turn a line into a dictionary that makes it suitable for all sorts of operations, including adding an effect to
        the event and making it easier to sort them into categories. Event structure:
        {
            "line": str line,
            "time": datetime,
            "source": str source identifier,
            "target": str target identifier,
            "ability": str ability,
            "effect": str effect,
            "amount": int amount,
            "type": LINE_NUMBER, LINE_ABILITY or LINE_EFFECT,
            "effect": effect line dictionary or None,
            "color": color for this type of event,
            "active_id": id that was activate when this ability was fired
        }
        :param line: A GSF CombatLog line
        :return: dictionary
        """
        # Get the base dictionary
        line_dict = line if isinstance(line, dict) else Parser.line_to_dictionary(line)
        # Determine line type
        if "Damage" in line["effect"] or "Heal" in line["effect"]:
            line_type = Parser.LINE_NUMBER
        elif "AbilityActivate" in line["effect"]:
            line_type = Parser.LINE_ABILITY
        else:
            line_type = Parser.LINE_EFFECT
        # Get the right text color
        color = Parser.get_event_color(line_dict, active_id)
        # Create the dictionary with additional items
        effects = Parser.get_effects_ability(line_dict, lines, active_id)
        if effects is False:
            return None
        additional = {
            "effects": effects,
            "line": line,
            "type": line_type,
            "color": color,
            "active_id": active_id
        }
        # Make one nice dictionary and return it
        line_dict.update(additional)
        return line_dict

    @staticmethod
    def get_effects_ability(line_dict, lines, active_id):
        """
        Parse the lines after an event to determine what events are effects of the event specified
        :param line_dict: line dictionary
        :param lines: lines
        :param active_id: argument for Parser.compare_ids
        :return: dict with events or None or False if not eligible for having effects
        """
        eligibility = Parser.get_effects_eligible(line_dict, lines, active_id)
        if eligibility is False or eligibility is None:
            return eligibility
        ability = line_dict["ability"]
        ability_effects = {}
        effects_list = effects.ability_to_effects[ability]
        ability_duration = durations.durations[ability]
        for event in lines[lines.index(line_dict):]:
            if (event["time"] - line_dict["time"]).total_seconds() > ability_duration[1] + 5:
                break
            effect = event["effect"].split(":")[1].split("{")[0].strip()
            if "RemoveEffect" in event["effect"] and effect in ability_effects:
                time_diff = (event["time"] - ability_effects[effect]["start"]["time"]).total_seconds()
                ability_effects[effect]["duration"] = time_diff
            if effect not in effects_list or line_dict["source"] != event["source"]:
                continue
            if event["ability"] != ability:
                continue
            if effect not in ability_effects:
                ability_effects[effect] = {
                    "name": effect,
                    "start": event,
                    "allied": durations.durations[ability][0] if effect != "Missile Lock Immunity" else True,
                    "count": 1,
                    "duration": 0,
                    "damage": int(event["amount"].replace("*", "")) if event["amount"] != "" else 0,
                    "dot": (event["time"] - line_dict["time"]).total_seconds() if ability_duration[2] is True else None
                }
            else:
                ability_effects[effect]["count"] += 1
                if effect == "Damage":
                    ability_effects[effect]["damage"] += int(event["amount"].replace("*", ""))
                    if ability_effects[effect]["dot"] is not None:
                        ability_effects[effect]["dot"] = (event["time"] - line_dict["time"]).total_seconds()
        return ability_effects

    @staticmethod
    def get_effects_eligible(line_dict, lines, active_id):
        """
        Determine whether or not this event is eligible for having events. Only abilities that are applied to more
        than a single target or that are applied for a certain time are eligible by default. A special exclusion
        is set up for the activation of secondary weapons (launching projectiles)
        """
        # Exclusion for launching projectiles, only hits have effects
        if line_dict["ability"] in abilities.secondaries and "AbilityActivate" in line_dict["effect"]:
            return False
        # Exclusion for any event that is not in the durations dictionary (and thus either is not applied to multiple
        # targets or does apply an effect over time or is not included for some other reason)
        ability = line_dict["ability"]
        if ability not in effects.ability_to_effects or ability not in durations.durations:
            return None
        # The previous line is used in determining whether
        index = lines.index(line_dict)
        if index == 0:
            return None
        # The requirements for being eligible are quite strict
        for prev_line in lines[index-5:index-1]:
            # The source of the previous event must be equal
            source_is_equal = prev_line["source"] == line_dict["source"]
            ability_is_equal = prev_line["ability"] == line_dict["ability"]
            ability_is_special = any(special in line_dict["line"] for special in durations.special_cases)
            time_diff = (line_dict["time"] - prev_line["time"]).total_seconds()
            source_is_player = Parser.compare_ids(prev_line["source"], active_id)
            if source_is_equal and ability_is_equal and not ability_is_special:
                return False
            if ability_is_special and source_is_player and time_diff < 15 and ability_is_equal:
                return False
        return True

    @staticmethod
    def get_event_color(line_dict, active_id, colors=variables.color_scheme):
        """
        Return the correct text color for a certain event dictionary
        :param line_dict: line dictionary
        :param active_id: active ID for the log
        :param colors: color scheme dict-like
        :return: str color
        """
        category = Parser.get_event_category(line_dict, active_id)
        return colors[category][1]

    @staticmethod
    def get_event_category(line_dict, active_id):
        """
        Get the correct category for an event
        :param line_dict: line dictionary
        :param active_id: active ID for the log or list of IDs
        :return: str category
        """
        # Ability string, stripped and formatted to be compatible with the data structures
        ability = line_dict['ability'].split(' {', 1)[0].strip()
        # If the ability is empty, this is a Gunship scope activation
        if ability == "":
            return "other"
        # Damage events
        if "Damage" in line_dict['effect']:
            # Check for damage taken
            if Parser.compare_ids(line_dict["destination"], active_id):
                # Selfdamage
                if line_dict['source'] == line_dict['target']:
                    return "selfdmg"
                # Damage taken
                else:
                    if ability in abilities.secondaries:
                        return "dmgt_sec"
                    else:
                        return "dmgt_pri"
            # Damage dealt
            else:
                if ability in abilities.secondaries:
                    return "dmgd_sec"
                else:
                    return "dmgd_pri"
        # Healing
        elif "Heal" in line_dict['effect']:
            # Selfhealing
            if Parser.compare_ids(line_dict["source"], active_id):
                return "selfheal"
            # Other healing
            else:
                return "healing"
        # AbilityActivate
        elif "AbilityActivate" in line_dict['effect']:
            if line_dict["ability"] in abilities.engines:
                return "engine"
            elif line_dict["ability"] in abilities.shields:
                return "shield"
            elif line_dict["ability"] in abilities.systems:
                return "system"
            else:
                return "other"
        elif "RemoveEffect" in line_dict["effect"] or "ApplyEffect" in line_dict["effect"]:
            return "other"
        raise ValueError("Could not determine category of line dictionary: '{}'".format(line_dict))

    @staticmethod
    def compare_ids(id, active_ids):
        """
        Compare an ID to either a single active ID or a list of IDs
        :param id: id to compare
        :param active_ids: either a list of IDs, or a single ID
        :return: True if ID is a match, False if not
        """
        if isinstance(active_ids, list):
            return id in active_ids
        elif isinstance(active_ids, str):
            return id == active_ids
        else:
            raise ValueError("Invalid type of active_ids: {}".format(repr(active_ids)))

    @staticmethod
    def get_effect_allied(ability):
        """
        Determine whether an ability is an allied (positive) one or an enemy (negative) one.
        :param ability: ability str
        :return: True if allied, False if enemy
        """
        return ability in effects.allied_effects

    """
    This section contains mostly legacy code that might or might not be re-used in the new Parser parsing engine. Treat
    with care, might not be suitable for the most up-to-date CombatLogs (if GSF ever got updated).
    """

    @staticmethod
    def log_splitter_file(file_name, player_id_list=None):
        """
        Split a CombatLog into matches and spawns with a file name and an optional player id number list
        """
        # Check if file exists, else add the combatlogs folder to it
        combatlogs_path = variables.settings_obj["parsing"]["cl_path"]
        file_name = file_name if os.path.exists(file_name) else os.path.join(combatlogs_path, file_name)
        if not os.path.exists(file_name):
            raise FileNotFoundError("CombatLog {} was not found.".format(file_name))
        # Execute the splitting
        with open(file_name, "r") as fi:
            lines = fi.readlines()
        return Parser.log_splitter_lines(lines, player_id_list)

    @staticmethod
    def log_splitter_lines(lines, player_id_list=None):
        """
        Split the lines of a CombatLog into matches and spawns
        """
        player_id_list = player_id_list if player_id_list is not None else Parser.get_player_id_list(lines)
        if len(player_id_list) == 0:
            raise ValueError("Emtpy player id list received!")
        # Check if the lines received are not 0
        if len(lines) == 0:
            raise ValueError("Empty list of lines received")

        # Create variables to store data in
        file_cube = []
        match_matrix = []
        spawn_list = []
        is_match = False
        match_index = -1
        active_id = None
        spawn_timings_matrix = []
        match_timings_list = []
        line_dict = None

        # Loop through the lines and sort them
        for line in lines:

            # Get the line dictionary for the line
            line_dict = Parser.line_to_dictionary(line)

            # Perform general checks to determine whether this line is a special case and should be skipped, bug #47
            if "SetLevel" in line or "Infection" in line:  # Check for level-up and Rakghoul infection events
                continue

            # If '@' is in the source or target, then this is not a GSF ability
            if '@' in line_dict["source"] or '@' in line_dict["target"]:
                # If this is a match, then this is the end of it
                if is_match is True:
                    match_timings_list.append(line_dict["time"])  # The new line dictionary already has a datetime
                    # Save the spawns
                    file_cube.append(match_matrix)
                    match_matrix.clear()
                is_match = False
                continue

            # Process match
            if is_match is False:
                # Open a new match
                is_match = True
                match_index += 1
                # Add the time to the list and matrix
                match_timings_list.append(line_dict["time"])
                spawn_timings_matrix.append(list())
                # The spawn is processed after this

            # Process spawn
            if line_dict["source"] != active_id and line_dict["target"] != active_id:
                # Match is already running, new spawn
                if line_dict["source"] not in player_id_list and line_dict["target"] not in player_id_list:
                    raise ValueError("Event found with ID that was not in the player_id_list: {}\n{}".format(
                        player_id_list, line_dict
                    ))
                # Save the spawn if it is not empty
                if len(spawn_list) != 0:
                    match_matrix.append(spawn_list)
                    spawn_list.clear()
                # Add the new spawn time to the spawn timings matrix
                spawn_timings_matrix[match_index].append(line_dict["time"])
                # Determine the new active_id
                active_id = line_dict["source"] if line_dict["source"] in player_id_list else line_dict["target"]

            # Add the line to the current spawn
            spawn_list.append(line_dict)

        # The log may end in a GSF event
        if is_match is True:
            # Save the data
            match_matrix.append(spawn_list) if len(spawn_list) != 0 else None
            file_cube.append(match_matrix) if len(match_matrix) != 0 else None
            # The timing of the end of the match was the time of the last line
            match_timings_list.append(line_dict)

        # Return a cube of lines with only GSF line dictionaries, a list of timings (start and end) of matches and the
        # spawn timings matrix which contains the start times of the spawns per match
        return file_cube, match_timings_list, spawn_timings_matrix

    @staticmethod
    def get_player_id_list(lines):
        """
        Get a list of player ID numbers for a certain list of lines
        """
        if not isinstance(lines[0], dict):
            lines = [Parser.line_to_dictionary(line) for line in lines]
        player_list = []
        for line in lines:
            # print("Processing line: {}".format(line.replace("\n", "")))
            if "@" in line:
                continue
            dictionary = Parser.line_to_dictionary(line)
            if dictionary["source"] == dictionary["target"]:
                player_list.append(dictionary["source"])
        return player_list

    @staticmethod
    def get_player_name(lines):
        """
        Get the character name for a set of lines
        """
        for line in lines:
            if "@" not in line or ":" in line:
                continue
            dictionary = Parser.line_to_dictionary(line)
            if dictionary["source"] == dictionary["target"]:
                return dictionary["source"]
        return None

    @staticmethod
    def get_enemies_list(spawn, player_list):
        """
        Get the list of enemies for a certain list of lines that describe a spawn
        """
        enemies = []
        for line in spawn:
            dictionary = Parser.line_to_dictionary(line)
            source = dictionary["source"]
            target = dictionary["target"]
            if source not in player_list and source not in enemies:
                enemies.append(source)
                # Performance optimization
                continue
            if target not in player_list and target not in enemies:
                enemies.append(target)
        return enemies

    @staticmethod
    def get_amount_enemies(spawn, player_list):
        """
        Get the amount of enemies for a certain list of lines that describe a spawn
        """
        return len(Parser.get_enemies_list(spawn, player_list))

    @staticmethod
    def get_ship_for_dict(abilities_dict):
        """
        Get a list containing the possible ships for a certain abilities dictionary
        """
        ships_list = abilities.ships
        for ability in abilities_dict.keys():
            if ability in abilities.excluded_abilities:
                continue
            temp_list = ships_list
            for ship in temp_list:
                if ability not in abilities.ships_abilities[ship]:
                    ships_list.remove(ship)
        return ships_list

    @staticmethod
    def get_gsf_in_file(file_name):
        """
        Get a boolean of whether there are GSF matches in a file
        """
        combatlogs_path = variables.settings_obj["parsing"]["cl_path"]
        abs_path = os.path.join(combatlogs_path, file_name)
        if not os.path.exists(abs_path):
            return None
        with open(abs_path, "r") as fi:
            lines = fi.readlines()
        for line in lines:
            if "@" in line:
                continue
            return True
        return False

    @staticmethod
    def parse_filename(file_name):
        """
        Get datetime object for a filename
        """
        try:
            return datetime.strptime(file_name[:-10], "combat_%Y-%m-%d_%H_%M_%S_")
        except ValueError:
            return None
