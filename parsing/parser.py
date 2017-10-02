# A new parsing engine built by RedFantom based on principles from parse.py and realtime.py
# Is capable of parsing files as well as realtime parsing
import re
import os
from datetime import datetime
from tkinter.ttk import Frame
from queue import Queue
# Own modules
from parsing.screen import ScreenParser, FileHandler
from parsing.stalking_alt import LogStalker
from parsing.screen import ScreenParser
from parsing import abilities
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
    # Mode constants
    MODE_FILE = "file"
    MODE_MATCH = "match"
    MODE_SPAWN = "spawn"

    def __init__(self, events_view=None, line_queue=None, character_data=None, real_time=False, screen_parsing=False,
                 mode=MODE_SPAWN):
        """
        :param events_view: An EventsView widget with .timeline and .eventslist attributes
        :param line_queue: Queue object (or object with .put()) to pass lines parsed to
        :param character_data: Character dictionary with "Ship Objects" keys
        """
        # Perform type checks
        if not isinstance(events_view, Frame):
            raise ValueError("events_view argument is not a ttk.Frame")
        if not isinstance(line_queue, Queue):
            raise ValueError("line_queue argument is not a Queue")
        if not isinstance(character_data, dict):
            raise ValueError("character_data argument is not a dict")
        # Attributes required for ScreenParser
        self.sp_data_queue = None
        self.sp_exit_queue = None
        self.sp_query_queue = None
        self.sp_return_queue = None
        # Create attributes
        self.events_view = events_view
        self.line_queue = line_queue
        self.character_data = character_data
        self.log_stalker = Parser.setup_log_stalker() if real_time is True else None
        self.screen_parser = self.setup_screen_parser() if screen_parsing is True else None
        # Create

    def process_line(self, line):
        pass

    def setup_screen_parser(self):
        """
        Sets up a ScreenParser object with the correct arguments and keyword arguments
        """
        self.sp_data_queue = Queue()
        self.sp_exit_queue = Queue()
        self.sp_return_queue = Queue()
        self.sp_query_queue = Queue()
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
        return log

    @staticmethod
    def line_to_event_dictionary(line, active_id):
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
        line_dict = Parser.line_to_dictionary(line)
        # Determine line type
        if "Damage" in line or "Heal" in line:
            line_type = Parser.LINE_NUMBER
        elif "AbilityActivate" in line:
            line_type = Parser.LINE_ABILITY
        else:
            line_type = Parser.LINE_EFFECT
        # Get the right text color
        color = Parser.get_event_color(line_dict, active_id)
        # Create the dictionary with additional items
        additional = {
            "effect": None,
            "line": line,
            "type": line_type,
            "color": color,
            "active_id": active_id
        }
        # Make one nice dictionary and return it
        total = line_dict.update(additional)
        return total

    @staticmethod
    def get_event_color(line_dict, active_id, colors=variables.color_scheme):
        """
        Return the correct text color for a certain event dictionary
        :param line_dict: line dictionary
        :param active_id: active ID for the log
        :param colors: color scheme dict-like
        :return: str color
        """
        # Ability string, stripped and formatted to be compatible with the data structures
        ability = line_dict['ability'].split(' {', 1)[0].strip()
        # If the ability is empty, this is a Gunship scope activation
        if ability == "":
            return None
        # Damage events
        if "Damage" in line_dict['effect']:
            # Check for damage taken
            if line_dict['destination'] == active_id:
                # Selfdamage
                if line_dict['source'] == line_dict['target']:
                    return colors['selfdmg'][1]
                # Damage taken
                else:
                    if ability in abilities.primaries:
                        return colors['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        return colors['dmgt_sec'][1]
                    else:
                        return colors['dmgt_pri'][1]
            # Damage dealt
            else:
                if ability in abilities.primaries:
                    return colors['dmgd_pri'][1]
                elif ability in abilities.secondaries:
                    return colors['dmgd_sec'][1]
                else:
                    return colors['dmgd_pri'][1]
        # Healing
        elif "Heal" in line_dict['effect']:
            # Selfhealing
            if line_dict['source'] == active_id:
                return colors['selfheal'][1]
            # Other healing
            else:
                return colors['healing'][1]
        # AbilityActivate
        elif "AbilityActivate" in line_dict['effect']:
            if line_dict["ability"] in abilities.engines:
                return colors['engine'][1]
            if line_dict["ability"] in abilities.shields:
                return colors['shield'][1]
            if line_dict["ability"] in abilities.systems:
                return colors['system'][1]
        else:
            return None

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
                    raise ValueError("Event found with ID that was not in the player_id_list.\n{}".format(line_dict))
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
        pass
