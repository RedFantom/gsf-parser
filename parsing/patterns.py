"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard library
from datetime import timedelta
# Project modules
from data.patterns import Patterns
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
