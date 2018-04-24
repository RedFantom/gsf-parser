"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import os
from datetime import datetime
from data import abilities, effects, durations
from variables import settings, colors


class Parser(object):
    """
    A Parsing engine that can sequentially parse CombatLog lines and
    supports staticmethods for parsing individual spawns and matches to
    keep some backwards compatibility with the functions found in
    parse.py. Replaces the Parsing engine found in realtime_alt.py.

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

    # Date format
    TIME_FORMAT = "%H:%M:%S.%f"
    DATE_FORMAT = ""

    @staticmethod
    def line_to_dictionary(line, enemies: dict=None):
        """
        Turn a line into a dictionary that makes it easier to parse
        :param line: A GSF CombatLog line
        :param enemies: Dictionary with enemies, optional
        :return: dictionary for line, or None if failed
        """
        if isinstance(line, dict):
            return line

        # Split the line into elements
        def remove_brackets(elem):
            return elem.replace("[", "").replace("]", "").replace("(", "").replace(")", "").strip()

        elements = [remove_brackets(elem) for elem in line.split("]")]
        """
        Valid GSF CombatLog event:
        [time] [source] [target] [ability] [effect] (amount)
        """
        log = dict()
        log["line"] = line
        effect = "{}: {}".format(*tuple(element.split("{")[0].strip() for element in elements[4].split(":")))
        log["time"] = datetime.strptime(elements[0], Parser.TIME_FORMAT)
        log["source"] = elements[1]
        log["target"] = elements[2]
        if len(elements) != 6:
            return log  # Invalid non-GSF CombatLog line
        log.update({
            "ability": elements[3].split("{", 1)[0].strip(),
            "effect": effect,
            "amount": elements[5],
            "destination": log["target"]
        })
        if log["target"] == log["source"] and log["ability"] in abilities.secondaries:
            log["target"] = "Launch Projectile"
        if log["ability"].strip() == "":
            log["ability"] = "Railgun Charge"
        if log["amount"].strip() != "":
            log["amount"] = log["amount"].split(" ")[0]
        if enemies is not None:
            if log["source"] in enemies:
                log["source"] = enemies[log["source"]]
            if log["target"] in enemies:
                log["target"] = enemies[log["target"]]
        log["destination"] = log["target"]
        log["self"] = log["source"] == log["target"]
        amount = log["amount"].replace("*", "")
        log["damage"] = int(amount) if amount.isdigit() else 0
        log["crit"] = "*" in log["amount"]
        return log

    @staticmethod
    def line_to_event_dictionary(line, active_id, lines):
        """
        Turn a line into a dictionary that makes it suitable for all
        sorts of operations, including adding an effect to the event and
        making it easier to sort them into categories. Event structure:
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
    def get_abilities_dict(lines: list):
        """Get the abilities dict for a list of lines"""
        abilities = {}
        for line in lines:
            if not isinstance(line, dict):
                line = Parser.line_to_dictionary(line)
            if line["ability"] not in abilities:
                abilities[line["ability"]] = 1
            else:
                abilities[line["ability"]] += 1
        return abilities

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
                    "damage": int(event["amount"].replace("*", "")) if isinstance(event["amount"], str) and event[
                        "amount"] != "" else "",
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
        Determine whether or not this event is eligible for having
        events. Only abilities that are applied to more than a single
        target or that are applied for a certain time are eligible by
        default. A special exclusion is set up for the activation of
        secondary weapons (launching projectiles)
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
        for prev_line in lines[max(index - 5, 0):index - 1]:
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
    def get_event_color(line_dict, active_id, colors=colors):
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
    def get_event_category(line_dict: dict, active_id: (list, str)):
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
            elif line_dict["ability"] == "Player Death":
                return "death"
            else:
                return "other"
        elif "RemoveEffect" in line_dict["effect"] or "ApplyEffect" in line_dict["effect"]:
            return "other"
        raise ValueError("Could not determine category of line dictionary: '{}'".format(line_dict))

    @staticmethod
    def compare_ids(id: str, active_ids: (list, str)):
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
        Determine whether an ability is an allied (positive) one or an
        enemy (negative) one.
        :param ability: ability str
        :return: True if allied, False if enemy
        """
        return ability in effects.allied_effects

    """
    This section contains mostly legacy code that might or might not be re-used in the new Parser parsing engine. Treat
    with care, might not be suitable for the most up-to-date CombatLogs (if GSF ever got updated).
    """

    @staticmethod
    def split_combatlog_file(file_name, player_id_list=None):
        """
        Split a CombatLog into matches and spawns with a file name and
        an optional player id number list
        """
        # Check if file exists, else add the combatlogs folder to it
        combatlogs_path = settings["parsing"]["path"]
        file_name = file_name if os.path.exists(file_name) else os.path.join(combatlogs_path, file_name)
        # Execute the splitting
        lines = Parser.read_file(file_name)
        return Parser.split_combatlog(lines, player_id_list)

    @staticmethod
    def get_player_id_list(lines):
        """Get a list of player ID numbers for a certain list of lines"""
        if not isinstance(lines[0], dict):
            lines = [Parser.line_to_dictionary(line) for line in lines]
        player_list = []
        for line in lines:
            if "@" in line["line"]:
                continue
            dictionary = Parser.line_to_dictionary(line)
            if dictionary["source"] == dictionary["target"] and dictionary["source"] not in player_list:
                player_list.append(dictionary["source"])
        return player_list

    @staticmethod
    def get_player_name(lines: list):
        """Get the character name for a set of lines"""
        lines = [Parser.line_to_dictionary(line) for line in lines]
        for line in lines:
            if "@" not in line["source"] or ":" in line["source"]:
                continue
            if line["source"] == line["target"]:
                return line["source"].replace("@", "")
        return None

    @staticmethod
    def get_enemy_id_list(lines: list, player_list: list):
        """
        Get the list of enemies for a certain list of lines that
        describe a spawn
        """
        enemies = []
        for line in lines:
            dictionary = Parser.line_to_dictionary(line)
            source = dictionary["source"]
            target = dictionary["target"]
            if "@" in source or "@" in target:
                continue
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
        Get the amount of enemies for a certain list of lines that
        describe a spawn
        """
        return len(Parser.get_enemy_id_list(spawn, player_list))

    @staticmethod
    def get_ship_for_dict(abilities_dict):
        """
        Get a list containing the possible ships for a certain
        abilities dictionary
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
        """Get a boolean of whether there are GSF matches in a file"""
        combatlogs_path = settings["parsing"]["path"]
        abs_path = os.path.join(combatlogs_path, file_name)
        if not os.path.exists(abs_path):
            return None
        lines = Parser.read_file(file_name)
        for line in lines:
            if "@" in line["line"]:
                continue
            return True
        return False

    @staticmethod
    def parse_filename(file_name):
        """Get datetime object for a filename"""
        file_name = os.path.basename(file_name)
        try:
            return datetime.strptime(file_name[:-10], "combat_%Y-%m-%d_%H_%M_%S_")
        except ValueError:
            return None

    @staticmethod
    def split_combatlog(lines: list, player_list: list):
        """
        Split a CombatLog containing GSF matches into a file cube (with
        indexing [match][spawn][event]) and provide the same interface
        as the legacy parse.splitter function.
        """
        if player_list is None:
            player_list = Parser.get_player_id_list(lines)

        # Data variables
        file_cube = []
        match = []
        spawn = []
        spawn_timings = []
        spawn_timings_temp = []  # Holds spawn timings for a single match while splitting
        match_timings = []
        is_match = False
        current_id = None

        # Loop over all the lines in the file and split
        for line in lines:
            # See print at checking argument
            if not isinstance(line, dict):
                line = Parser.line_to_dictionary(line)
            # Skip over SetLevel and Infection abilities, see issue #47
            if "SetLevel" in line["line"] or "Infection" in line["line"]:
                continue
            # Get the required data from the line
            time, source, target = line["time"], line["source"], line["target"]
            # Handle non-match lines
            if "@" in source or "@" in target:
                # If there was no match, then skip data manipulation
                if is_match is False:
                    continue
                # There was a match, so save data
                match.append(spawn.copy())
                file_cube.append(match.copy())
                # Clear temporary data
                match.clear()
                spawn.clear()
                # Set is_match to False again
                is_match = False
                current_id = None
                # Save the time this match ended
                match_timings.append(time)
                spawn_timings.append(spawn_timings_temp.copy())
                spawn_timings_temp.clear()
                # Done, continue with the next line
                continue
            # Neither source nor target contains '@', so this is a match event
            # Please note that isdigit() is not used because System events have an empty source

            # Process new matches
            if is_match is False:
                is_match = True
                # Save this as the start of a match and a spawn
                match_timings.append(time)
                spawn_timings_temp.append(time)
            # Process a change of ID
            if source != current_id and target != current_id:
                # New spawn
                if current_id is not None:
                    match.append(spawn.copy())
                    spawn.clear()
                    spawn_timings_temp.append(time)
                # Set the new ID
                if source in player_list:
                    current_id = source
                elif target in player_list:
                    current_id = target
                else:
                    print("[Parser] parse_spawn found a line in which neither source or target provide a valid player "
                          "ID:", line["line"].replace("\n", ""))
                    # raise ValueError("Neither source nor target contained a valid player ID in line:", line["line"])
            # Add this line to the spawn list and continue
            spawn.append(line)

        # Handle EOF before match ended
        if is_match is True and len(spawn) != 0:
            match.append(spawn.copy())
            file_cube.append(match.copy())
            match_timings.append(time)  # time cannot be undefined if is_match is True
            spawn_timings.append(spawn_timings_temp)
        # Return the results
        return file_cube, match_timings, spawn_timings

    @staticmethod
    def read_file(file_name: str, sharing_db: dict=None):
        """
        Read a file with the given filename in a safe and error handled
        manner. All attempts at reading GSF CombatLogs should use this
        function.
        """
        # If the file does not exist in CWD, then attempt to find it in
        # the CombatLogs folder
        if not os.path.exists(file_name):
            file_name = os.path.join(settings["parsing"]["path"], os.path.basename(file_name))
        if not os.path.exists(file_name):
            raise FileNotFoundError("File '{}' not found in absolute path, cwd or CombatLogs folder".format(file_name))
        # Attempt to read the file as bytes
        try:
            with open(file_name, "rb") as fi:
                lines = fi.readlines()
        except OSError:
            print("[Parser] Failed to read file: {}".format(os.path.basename(file_name)))
            raise
        lines_decoded = []
        # Convert each line into str (utf-8) separately
        for index, line in enumerate(lines):
            try:
                line = line.decode()
            except UnicodeDecodeError:  # Mostly occurs on Unix systems
                continue
            lines_decoded.append(line)
        enemies = sharing_db[file_name]["enemies"] if sharing_db is not None and file_name in sharing_db else None
        return [Parser.line_to_dictionary(line, enemies) for line in lines_decoded]

    @staticmethod
    def parse_spawn(spawn: list, player_list: list):
        """
        Parse a spawn list of lines and return various statistics for
        this spawn with the same interface as parse.parse_spawn()
        """
        if not isinstance(spawn[0], dict):
            print("[Parser] Unoptimized parsing of spawn")
        # Data variables
        abilities_dict = {}
        dmg_d, dmg_t, dmg_s, healing = 0, 0, 0, 0
        enemies = []
        enemy_dmg_d, enemy_dmg_t = {}, {}
        hitcount, critcount = 0, 0
        # Parse the spawn
        for event in spawn:
            # See arg check
            if not isinstance(event, dict):
                event = Parser.line_to_dictionary(event)
            # Get the data into locals
            time, source, target = event["time"], event["source"], event["target"]
            ability, effect, amount = event["ability"], event["effect"], event["damage"]
            # If source is empty, then rename source to ability
            if source == "":
                source = ability
            # Count ability usage. Note that self-targeted Damage abilities are skipped
            if source in player_list and "AbilityActivate" in effect and not (source == target and "Damage" in effect):
                if ability not in abilities_dict:
                    abilities_dict[ability] = 0
                abilities_dict[ability] += 1
            # Process enemy ID
            for id in [source, target]:
                if id in player_list or id in enemies:
                    continue
                enemies.append(id)
            # Process damage
            if "Damage" in effect:
                # Self damage
                if source == target:
                    dmg_s += amount
                # Damage dealt
                elif source in player_list:
                    dmg_d += amount
                    # Process hit
                    hitcount += 1
                    critcount += event["crit"]
                    # Process enemy
                    if target not in enemy_dmg_t:
                        enemy_dmg_t[target] = 0
                    enemy_dmg_t[target] += amount
                    # Also add to the other dictionary
                    if target not in enemy_dmg_d:
                        enemy_dmg_d[source] = 0
                # Damage taken
                else:
                    dmg_t += amount
                    # Process enemy
                    if source not in enemy_dmg_d:
                        enemy_dmg_d[source] = 0
                    enemy_dmg_d[source] += amount
                    # Also add to the other dicionary
                    if source not in enemy_dmg_t:
                        enemy_dmg_t[source] = 0
            # Process healing
            elif "Healing" in effect:  # Damage and Healing are not in the same effect
                # Healing given is not supported currently, see #25
                if target not in player_list:
                    continue
                healing += amount
            # Other types of events are not currently supported
            continue
        # Determine the ship used
        ships_list = abilities.ships.copy()
        # This list keeps track of the secondary weapons. If there are two, it might
        # be possible to eliminate more ships after parsing all abilities
        primaries, secondaries = [], []
        # Check all abilities
        for ability in abilities_dict.keys():
            # Some abilities are excluded from the ship parsing
            if ability in abilities.excluded_abilities:
                continue
            # If this is a secondary, then add the ability to the secondaries list
            if ability in abilities.secondaries:
                secondaries.append(ability)
            if ability in abilities.primaries:
                primaries.append(ability)
            # Parse for each ship
            ships_list_copy = ships_list.copy()
            # Loop over the ships
            for ship in ships_list_copy:
                # Check if this ship can use the ability
                if ability not in abilities.ships_abilities[ship]:
                    ships_list.remove(ship)
                # If no ships are left, then something must have gone wrong with the excluded abilities,
                # or the abilities for each ship are not up-to-date with the current version of GSF
                if len(ships_list) == 0:
                    raise ValueError("No ships possible for this spawn. Last ability was:", ability)
        # Remove duplicates from secondaries list
        primaries, secondaries = set(primaries), set(secondaries)
        # Remove all ships that do not fit primaries and secondaries requirements
        for category in ["primaries", "secondaries"]:
            if len(ships_list) == 1:
                break
            if len(locals()[category]) != 2:
                continue
            # Dual primaries or secondaries
            ships_list_copy = ships_list.copy()
            for ship in ships_list_copy:
                if ship not in getattr(abilities, "ships_dual_{}".format(category)):
                    ships_list.remove(ship)
        # Calculate critical luck
        crit_luck = critcount / hitcount if hitcount != 0 else 0  # ZeroDivisionError
        # Return the expected variables
        return (abilities_dict, dmg_t, dmg_d, healing, dmg_s, enemies, critcount,
                crit_luck, hitcount, ships_list, enemy_dmg_d, enemy_dmg_t)

    @staticmethod
    def parse_match(match: list, player_list: list):
        """
        Parse a match list of spawn event lists by using the
        Parser.parse_spawn function.
        """
        abilities_dict = {}
        dmg_d, dmg_t, dmg_s, healing = 0, 0, 0, 0
        enemies = []
        enemy_dmg_d, enemy_dmg_t = {}, {}
        critcount, hitcount = 0, 0
        ships = {ship: 0 for ship in abilities.ships}
        uncounted = 0
        for spawn in match:
            results = Parser.parse_spawn(spawn, player_list)
            # Damage and healing
            dmg_d += results[2]
            dmg_t += results[1]
            dmg_s += results[4]
            healing += results[3]
            hitcount += results[8]
            critcount += results[6]
            # Abilities
            for ability, amount in results[0].items():
                if ability not in abilities_dict:
                    abilities_dict[ability] = 0
                abilities_dict[ability] += amount
            # Enemies
            enemies.extend(results[5])
            enemy_dmg_d.update(results[10])
            enemy_dmg_t.update(results[11])
            # Ships
            if len(results[9]) > 1:
                uncounted += 1
            else:
                ships[results[9][0]] += 1
        # Crit luck
        crit_luck = critcount / hitcount if hitcount != 0 else 0
        # Return
        return (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount, critcount,
                crit_luck, enemies, enemy_dmg_d, enemy_dmg_t, ships, uncounted)

    @staticmethod
    def parse_file(file_cube: list, player_list: list):
        """
        Parse a file providing sums instead of lists and matrices like
        parse.parse_file()
        """
        abilities_dict = {}
        dmg_d, dmg_t, dmg_s, healing = 0, 0, 0, 0
        enemies = []
        enemy_dmg_d, enemy_dmg_t = {}, {}
        critcount, hitcount = 0, 0
        ships = {ship: 0 for ship in abilities.ships}
        uncounted = 0
        for match in file_cube:
            results = Parser.parse_match(match, player_list)
            # Damage and healing
            dmg_d += results[1]
            dmg_t += results[2]
            dmg_s += results[3]
            healing += results[4]
            hitcount += results[5]
            critcount += results[6]
            # Abilities
            for ability, amount in results[0].items():
                if ability not in abilities_dict:
                    abilities_dict[ability] = 0
                abilities_dict[ability] += amount
            # Enemies
            enemies.extend(results[8])
            enemy_dmg_d.update(results[9])
            enemy_dmg_t.update(results[10])
            # Ships
            uncounted += results[12]
            for ship, amount in results[11].items():
                ships[ship] += amount
        # Crit luck
        crit_luck = critcount / hitcount if hitcount != 0 else 0
        # Return
        return (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount, critcount,
                crit_luck, enemies, enemy_dmg_d, enemy_dmg_t, ships, uncounted)

    @staticmethod
    def parse_folder():
        """
        Return a nice tuple of parsed statistics with the parse_file
        helper function.
        """
        abilities_dict = {}
        dmg_d, dmg_t, dmg_s, healing = 0, 0, 0, 0
        enemies = []
        enemy_dmg_d, enemy_dmg_t = {}, {}
        critcount, hitcount = 0, 0
        ships = {ship: 0 for ship in abilities.ships}
        uncounted = 0
        deaths = 0
        time = 0
        file_list = os.listdir(settings["parsing"]["path"])
        for file in file_list:
            if not Parser.get_gsf_in_file(file):
                continue
            lines = Parser.read_file(file)
            player_ids = Parser.get_player_id_list(lines)
            file_cube, match_timings, _ = Parser.split_combatlog(lines, player_ids)
            results = Parser.parse_file(file_cube, player_ids)
            # Damage and healing
            dmg_d += results[1]
            dmg_t += results[2]
            dmg_s += results[3]
            healing += results[4]
            hitcount += results[5]
            critcount += results[6]
            deaths += sum([len(match) for match in file_cube])
            # Abilities
            for ability, amount in results[0].items():
                if ability not in abilities_dict:
                    abilities_dict[ability] = 0
                abilities_dict[ability] += amount
            # Enemies
            enemies.extend(results[8])
            enemy_dmg_d.update(results[9])
            enemy_dmg_t.update(results[10])
            # Ships
            uncounted += results[12]
            for ship, amount in results[11].items():
                ships[ship] += amount

            start = None
            for timing in match_timings:
                if start is not None:
                    time += (timing - start).total_seconds()
                    start = None
                    continue
                start = timing
        # Crit luck
        crit_luck = critcount / hitcount if hitcount != 0 else 0
        # Return
        return (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount,
                critcount, crit_luck, enemies, enemy_dmg_d, enemy_dmg_t,
                ships, uncounted, deaths, time)

    @staticmethod
    def build_spawn_from_match(match: list)->list:
        """Join the spawns of a match together to a single big spawn"""
        result = list()
        for spawn in match:
            result.extend(spawn)
            id_list = Parser.get_player_id_list(spawn)
            line = spawn[-1]
            death_event = "[{}] [{}] [{}] [{}] [{}] ()".format(
                line["time"].strftime(Parser.TIME_FORMAT),
                line["source"],
                Parser.get_player_id_from_line(line, id_list),
                "Player Death",
                "ApplyEffect {}: AbilityActivate {}")
            result.append(Parser.line_to_dictionary(death_event))
        return result

    @staticmethod
    def get_player_id_from_line(line: dict, active_id: (str, list)):
        """Return the active ID of a line based on a single line"""
        for player_id in (line["source"], line["target"]):
            if Parser.compare_ids(player_id, active_id) is True:
                return player_id
        return None

    @staticmethod
    def gsf_combatlogs():
        """Return a list of absolute paths to all files with GSF matches"""
        files = os.listdir(settings["parsing"]["path"])
        for file in files:
            if not Parser.get_gsf_in_file(file):
                continue
            path = os.path.join(settings["parsing"]["path"], file)
            yield path

    @staticmethod
    def get_id_format(spawn: list):
        """Return the player ID format of a match or spawn"""
        id_list = Parser.get_player_id_list(spawn)
        return id_list[0][:8]

    @staticmethod
    def is_tutorial(match: dict):
        for spawn in match:
            for line in spawn:
                if "Tutorial" in line["line"] or "Invulnerable" in line["line"]:
                    return True
        return False

