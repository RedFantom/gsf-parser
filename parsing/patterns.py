"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard library
from datetime import timedelta, datetime
# Project modules
from data.patterns import Patterns
from data import abilities
from parsing.ships import Ship, Component


FILE = "file"
SCREEN = "screen"
SHIP = "ship"


class PatternParser(object):
    """
    Parses patterns that are predefined in data/patterns.py to gather
    more data from CombatLogs and screen parsing to aggregate data and
    synthesize more useful information for the user.
    """
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
        trigger = pattern["trigger"]
        # Check if line is a valid trigger line
        if PatternParser.compare_events(line, trigger) is False:
            return False
        # Check all required events
        events = pattern["events"]
        requirements = list()
        for (span, event, eid) in events:
            # Requirements already satisfied are skipped
            if eid in requirements:
                continue
            # Check requirement against given data
            if event[0] == FILE:
                line_sub = PatternParser.get_lines_subsection(lines, trigger, span)
                for line in line_sub:
                    if PatternParser.compare_events(line, event[1]):
                        requirements.append(eid)
                        break
            elif event[0] == SCREEN:
                pass
            elif event[0] == SHIP:
                pass
            else:
                raise ValueError("Invalid event type: ", event)
        return True

    @staticmethod
    def compare_events(superset: dict, subset: dict):
        """Compare two line event dictionaries for subset"""
        for key, value in subset.items():
            if key == "source" and (superset["source"] == superset["target"]) is not subset["source"]:
                    return False
            elif superset[key] != subset[key]:
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
        return result

    @staticmethod
    def get_screen_subsection(data: dict, category: str, origin: datetime, span: tuple):
        """Get a subsection of the screen data dictionary of a match"""
        sub = data[category]
        low, high = origin + timedelta(seconds=span[0]), origin + timedelta(seconds=span[1])
        results = dict()
        for time, data in sub.items():
            if low <= time <= high:
                results[time] = data
        return results

    @staticmethod
    def get_ship_from_screen_data(data: dict):
        """Return the Ship object contained in the spawn data"""
        if "ship" not in data:  # Older versions
            return None
        ship = data["ship"]
        if not isinstance(ship, Ship):
            print("[PatternParser] Unexpected data type found for ship key: {}".format(ship))
        return ship

    @staticmethod
    def get_component_in_ship(ship: Ship, component: (str, Component)):
        """Return whether a component is found within a Ship instance"""
        if ship is None:
            return False  # Ship option not available at parsing time
        if isinstance(component, Component):
            name, category = component.name, component.category
        else:  # str
            name = component
            category = PatternParser.get_component_category(component)
        if category not in ship.components:
            return False  # Configured improperly at parsing time
        categories = (category,)
        if "Weapon" in category:  # Extend to double primaries/secondaries
            categories += (category[0] + "2",)
        # Loop over categories
        result = False
        for category in categories:
            if category not in ship:  # Double primaries/secondaries
                continue
            component = ship.components[category]
            if not isinstance(component, Component):  # Improper config
                print("[PatternParser] Improperly configured Ship instance:", ship, component)
                continue
            if component.name == name:
                result = True
                break
            continue
        return result

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
        raise ValueError("Invalid component type given:", component)
