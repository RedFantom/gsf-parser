"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""


class Patterns:
    """
    Data class that contains all the patterns that can be parsed by
    parsing/patterns.py/PatternParser. Pattern dictionary description:

    {
        "name": pattern name,
        "description": str description,
        "trigger": event descriptor (only CombatLog lines!),
        "events": [((start, end), event descriptor, id),]
    }
    The 'start' and 'end' values are relative
    The PatternParser requires a single event for each ID to be present
    within the time range described.

    Event descriptor:
    ("file", {all keys and values are required to match for CombatLog})
    ("screen", category, expected data)
    ("ship", type, *args)
        type:
            ability available: A certain ability must be available
            component: Component that must be equipped
            crew: Crew member must be selected
        args:
            ability available: (ability_name, ability_bool)
            component: (component_name)
            crew: (crew_name)
    """
    pass
