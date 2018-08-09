"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard library
from datetime import timedelta, datetime
# Project modules
from data.components import PLURAL_TO_SINGULAR
from data.patterns import Patterns
from data import abilities
from parsing.ships import Ship, Component, get_ship_category
from parsing.shipstats import ShipStats
from parsing.parser import Parser


class InvalidDescriptor(ValueError):
    def __init__(self, event_descriptor: tuple):
        ValueError.__init__(
            self, "Invalid event descriptor for this function:  {}".format(event_descriptor))


class PatternParser(object):
    """
    Parses patterns that are predefined in data/patterns.py to gather
    more data from CombatLogs and screen parsing to aggregate data and
    synthesize more useful information for the user.
    """

    @staticmethod
    def parse_patterns(lines: list, screen: dict, patterns: list, active_ids: list):
        """
        Parse a set of patterns over the data for a given spawn. These
        sets are described in the Patterns class in data/patterns.py .

        For each line, all the patterns are parsed by checking if the
        line is a valid trigger for a pattern and then checking if the
        pattern is satisfied by checking the other data available.

        Then returns a set of markers suitable for displaying on a
        TimeLine, a lot like the FileHandler supports.
        """
        print("[PatternParser] Parsing Patterns.")
        markers = list()
        for pattern in patterns:
            print("[PatternParser] Parsing pattern:", pattern["name"])
            for line in lines:
                line["enemy"] = line["source"] not in active_ids
                result = PatternParser.parse_pattern(pattern, line, lines, screen)
                if result is True:
                    start = PatternParser.datetime_to_float(line["time"])
                    end = PatternParser.datetime_to_float(line["time"] + timedelta(seconds=1))
                    args = ("patterns", start, end)
                    kwargs = {"background": pattern["color"], "tags": (pattern["tag"],)}
                    markers.append((args, kwargs))
        return markers

    @staticmethod
    def parse_pattern(pattern: dict, line: dict, lines: list, screen: dict):
        """
        Parse a single pattern for a given CombatLog event. The format
        of a pattern dictionary is given in data/patterns.py/Patterns.

        Aggregates data from the screen data dictionary as well as the
        CombatLog lines in dictionary format.

        :param pattern: Pattern dictionary from Patterns class
        :param line: Event dictionary to check pattern for
        :param lines: List of event dictionaries of the full CombatLog
        :param screen: Screen data dictionary with the data of spawn
        :return: True if pattern is detected for this event, else False
        """
        triggered = False
        # Check if line is a valid trigger line
        for trigger in pattern["trigger"]:
            if PatternParser.compare_events(line, trigger) is True:
                print("[PatternParser] {} triggered at {}.".format(
                    pattern["name"], line["time"].time()))
                triggered = True
                break
            continue
        if not triggered:
            return False
        # Check all required events
        events = pattern["events"]
        results = list()
        requirements = list()
        for (span, event, eid) in events:
            requirements.append(eid)
            print("[PatternParser] Parsing event {} with eid {}.".format(event, eid))
            # Requirements already satisfied are skipped
            if eid in results:
                continue
            # Check requirement against given data
            if PatternParser.parse_event(line, lines, screen, event, span) is True:
                print("[PatternParser] Requirement {} satisfied.".format(eid))
                results.append(eid)
        print("[PatternParser] Requirements: {}, Results: {}".format(requirements, results))
        return PatternParser.compare_requirements(set(results), set(requirements))

    @staticmethod
    def parse_event(line: dict, lines: list, screen: dict, event: tuple, span: tuple):
        """
        Parse an event_descriptor over a given set of data.

        :param line: The line to parse the given event_descriptor for
        :param lines: List of lines for the spawn being parsed
        :param screen: Screen data dictionary for this spawn
        :param event: Event descriptor (Patterns docstring)
        :param span: (lower, higher) spawn tuple (Patterns docstring)

        :return: bool, whether the event was detected in this set

        :raises: ValueError - Invalid event descriptor
        """
        event_type = event[0]
        # File Event: (FILE, event_compare: dict)
        if event_type == Patterns.FILE:
            _, reference = event
            occurred = reference.pop("occurred", True)
            line_sub = PatternParser.get_lines_subsection(lines, line, span)
            print("[PatternParser] Comparing a file event: {}".format(reference))
            for line in line_sub:
                if PatternParser.compare_events(line, reference) is not occurred:
                    continue
                return True
            return False
        # Screen Event: (SCREEN, category: str, compare: callable, args: tuple)
        elif event_type == Patterns.SCREEN:
            if screen is None:
                return False
            _, category, func, args = event
            screen_sub = PatternParser.get_screen_subsection(screen, category, line["time"], span)
            print("[PatternParser] Screen subsection retrieved with length:", len(screen_sub))
            for key in sorted(screen_sub.keys()):
                print("[PatternParser]     Checking {} against {} function.".format(screen_sub[key], func))
                if func(screen_sub[key], args) is False:
                    continue
                return True
            return False
        # Ship Requirement, either ability, component, crew
        elif event_type == Patterns.SHIP:
            ship = PatternParser.get_ship_from_screen_data(screen)
            if ship is None:
                return False
            return PatternParser.parse_ship_descriptor(ship, line, lines, event)
        raise InvalidDescriptor(event)

    @staticmethod
    def parse_ship_descriptor(ship: Ship, line: dict, lines: list, event: tuple):
        """
        Parse an event_descriptor of the SHIP type. Supports ability,
        component and crew type operations.
        :param ship: Ship instance for the spawn described by lines
        :param line: Trigger line dictionary
        :param lines: List of lines in this spawn
        :param event: Event descriptor tuple (PatternParser docstring)
        :return: The result of parsing this SHIP event descriptor
        """
        if event[0] != Patterns.SHIP:
            raise InvalidDescriptor(event)
        event_type, args = event[1], event[2:]  # "ability", "component", "crew"
        # Parse Component selected
        if event_type == "component":
            # Component must be selected on the Ship for this spawn
            component, = args
            return PatternParser.get_component_in_ship(lines, ship, component)
        # Parse Crew selected
        elif event_type == "crew":
            crew, = args
            return PatternParser.get_crew_in_ship(ship, crew)
        # Parse Ability Available
        elif event_type == "ability":
            return PatternParser.parse_ability_availability(line, lines, event, ship)
        # Parse ship type selected
        elif event_type == "type":
            ship_name = ship.name if ship is None else Parser.get_ship_for_dict(Parser.get_abilities_dict(lines))
            ship_type, = args
            return get_ship_category(ship_name) == ship_type
        raise InvalidDescriptor(event)

    @staticmethod
    def compare_events(superset: dict, subset: dict):
        """Compare two line event dictionaries for subset"""
        for key, value in subset.items():
            if key in ("amount", "damage"):
                amount = superset["amount"] if superset["amount"] not in (0, "") else 0
                string = subset[key].format(amount)
                if eval(string.replace("*", "")) is False:
                    return False
                continue
            if key in ("ability",) and hasattr(abilities, value):
                if superset[key] not in getattr(abilities, value):
                    return False
                continue
            if superset[key] != subset[key]:
                return False
        return True

    @staticmethod
    def get_lines_subsection(lines: list, origin: dict, span: tuple):
        """Get a subsection of a list of lines based on time span"""
        result = list()
        limit_l = origin["time"] + timedelta(seconds=span[0])
        limit_h = origin["time"] + timedelta(seconds=span[1])
        for event in lines:
            if limit_l <= event["time"] <= limit_h:
                result.append(event)
            if event["time"] > limit_h:
                break
        print("[LinesSubSection] Created sub-list of {} items between limits {}, {}".format(len(result), limit_l.time(), limit_h.time()))
        return result

    @staticmethod
    def get_screen_subsection(data: dict, category: str, origin: datetime, span: tuple):
        """Get a subsection of the screen data dictionary of a match"""
        sub = data[category]
        low, high = origin + timedelta(seconds=span[0]), origin + timedelta(seconds=span[1])
        results = dict()
        low, high = low.time(), high.time()
        for time, data in sub.items():
            time = time.time()
            if low <= time <= high:
                results[time] = data
        return results

    @staticmethod
    def get_ship_from_screen_data(data: dict):
        """Return the Ship object contained in the spawn data"""
        if data is None or "ship" not in data:
            return None
        ship = data["ship"]
        if not isinstance(ship, Ship):
            print("[PatternParser] Unexpected data type found for ship key: {}".format(ship))
        return ship

    @staticmethod
    def get_component_in_ship(lines: list, ship: Ship, component: (str, Component)):
        """Return whether a component is found within a Ship instance"""
        if isinstance(component, Component):
            name, category = component.name, component.category
        else:  # str
            name = component
            category = PatternParser.get_component_category(component)
        abilities = Parser.get_abilities_dict(lines)
        if name in abilities:
            return True
        if ship is None:
            return False  # Ship option not available at parsing time
        if category not in ship:
            return False  # Configured improperly at parsing time
        categories = (category,)
        if "Weapon" in category:  # Extend to double primaries/secondaries
            categories += (category[0] + "2",)
        # Loop over categories
        result = False
        for category in categories:
            if category not in ship:  # Double primaries/secondaries
                continue
            component = ship[category]
            if not isinstance(component, Component):  # Improper config
                print("[PatternParser] Improperly configured Ship instance:", ship, component)
                continue
            if component.name == name:
                result = True
                break
            continue
        return result

    @staticmethod
    def get_crew_in_ship(ship: Ship, crew: str):
        """Return whether a Crew member is found within a Ship instance"""
        if ship is None:
            return False  # Ship option not available at parsing time
        return crew in ship.crew.values()

    @staticmethod
    def get_component_category(component: str)->str:
        """Return the category of a given component"""
        if component in abilities.primaries:
            return "PrimaryWeapon"
        if component in abilities.secondaries:
            return "SecondaryWeapon"
        if component in abilities.engines:
            return "Engine"
        if component in abilities.systems:
            return "Systems"
        if component in abilities.shields:
            return "ShieldProjector"
        if component in abilities.copilots:
            return "CoPilot"
        raise ValueError("Invalid component type given:", component)

    @staticmethod
    def compare_requirements(results: (list, set), requirements: (list, set)):
        return all(req in results for req in requirements)

    @staticmethod
    def parse_ability_availability(line: dict, lines: list, descriptor: tuple, ship: Ship):
        """
        Return whether the availability of an ability matches the
        availability required by a SHIP-Ability event descriptor.
        :param line: Trigger line for Pattern
        :param lines: List of lines for this spawn
        :param descriptor: Ship-Ability event descriptor
        :param ship: Ship instance for this spawn
        :return: Whether the ability availability of an ability matches
            the availability described by the SHIP-Ability event
            descriptor
        """
        if ship is None:  # Ship option not available at parsing time
            return False
        _, event_type, (ability, available) = descriptor
        if ability in dir(abilities):
            category = PLURAL_TO_SINGULAR[ability]
            ability = list(getattr(abilities, ability))
        else:
            category = PatternParser.get_component_category(ability)
        if ship[category] is None:  # Not correctly configured
            return False
        elif ship[category].name in ability:  # list/str __contains__
            return False
        if "Weapon" in ability:  # PrimaryWeapon, SecondaryWeapon
            return True
        """
        In order to determine availability with optimum efficiency, all 
        lines preceding the trigger are parsed in reverse order to find 
        the first ability activation to check the availability of the
        ability as described in the event descriptor.
        """
        result = None
        for event in reversed(lines[0:lines.index(line)]):
            if event["ability"] == ability and event["effect"] == "AbilityActivate":
                result = event
                break
        if result is None:  # Ability was never activated
            return available
        # The ability was activated in the event result. Now check cooldown of
        # ability and determine if the ability was available yet again
        stats = ShipStats(ship, None, None)
        if category == "CoPilot":
            cooldown = 60
        elif category in ship:
            cooldown = stats[category]["Cooldown"]
        else:
            cooldown = abilities.cooldowns[ability]
        time_diff = (line["time"] - result["time"]).total_seconds()
        return (time_diff > cooldown) is available

    @staticmethod
    def datetime_to_float(date_time_obj):
        """Convert a datetime object to a float value"""
        if not isinstance(date_time_obj, datetime):
            raise TypeError("date_time_obj not of datetime type but {}".format(repr(date_time_obj)))
        return float(
            "{}.{}{}".format(date_time_obj.minute, (int((date_time_obj.second / 60) * 100)), date_time_obj.microsecond))
