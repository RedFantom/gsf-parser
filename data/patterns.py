"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from data import abilities


class Patterns:
    """
    Data class that contains all the patterns that can be parsed by
    parsing/patterns.py/PatternParser. Pattern dictionary description:

    {
        "name": pattern name,
        "description": str description,
        "trigger": event descriptor (only CombatLog lines!),
        "events": [((start, end), event descriptor, id),],
        "color": background color for marker
    }
    The 'start' and 'end' values are relative
    The PatternParser requires a single event for each ID to be present
    within the time range described.

    Event descriptor:

    ("file", {all keys and values are required to match for CombatLog})
        Keys suitable for matching: ability, effect, amount, self

    ("screen", category, compare: callable, args)
         compare should be a given function that takes the data found
         in the screen dictionary as the first argument and the args
         tuple as the second argument. It should return True upon a
         a match.

    ("ship", type: str, args: tuple)
        type:
            "ability": A certain ability must be available
            "component": Component that must be equipped
            "crew": Crew member must be selected
            "type": Ship type must be selected
        args:
            ability: (ability_name, ability_bool)
            component: (component_name)
                Note that the ability can only be a PrimaryWeapon,
                SecondaryWeapon, Systems, ShieldProjector or Engine
            crew: (crew_name)
            type: (ship_type: str)
    """

    # Event Descriptor types
    FILE = "file"
    SCREEN = "screen"
    SHIP = "ship"

    # Individual Patterns
    MISTAKE_GUNSHIP_EVASION = {
        "name": "Gunship Evasion",
        "description": "You were hit by a Gunship and did not perform "
                       "an evasive manoeuvre to prevent getting hit "
                       "again, even though one was available.",
        "trigger": (
            {"self": False, "damage": "{} > 0", "enemy": True, "ability": "Slug Railgun"},
            {"self": False, "damage": "{} > 0", "enemy": True, "ability": "Ion Railgun"},
            {"self": False, "damage": "{} > 0", "enemy": True, "ability": "Plasma Railgun"},
        ),
        "events": [
            ((0, 0), (SHIP, "ability", "Running Interference", True), 2),
            ((0, 0), (SHIP, "ability", "Distortion Field", True), 2),
            (FILE, {"self": True, "effect": "AbilityActivate", "ability": "Running Interference"}, 3),
            (FILE, {"self": True, "effect": "AbilityActivate", "ability": "Distortion Field"}, 3),
        ],
        "color": "#4286f4",
        "tag": "mistake_gunship_evasion"
    }

    MISTAKE_MISSILE_HIT = {
        "name": "Missile Hit",
        "description": "You were hit by a missile while your engine "
                       "ability was available. It is advised to work "
                       "on your reflexes.",
        "trigger": tuple(
            {"self": False, "damage": "{} > 0", "enemy": True, "ability": missile}
            for missile in abilities.missiles
        ),
        "events": (
            ((-20, 0), (FILE, {"ability": "engines", "occurred": False}), 1),
            ((0, 0), (SHIP, "ability", "engines", True), 1),
        ),
        "color": "brown",
        "tag": "missile_hit",
    }

    """
    Iteration
    """
    MISTAKES = [
        MISTAKE_GUNSHIP_EVASION,
        MISTAKE_MISSILE_HIT,
    ]
    
    ALL_PATTERNS = [
        MISTAKE_GUNSHIP_EVASION,
        MISTAKE_MISSILE_HIT,
    ]
