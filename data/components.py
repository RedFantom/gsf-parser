"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

COMPONENT_TYPES = {
    "primary": "PrimaryWeapon",
    "primary2": "PrimaryWeapon2",
    "secondary": "SecondaryWeapon",
    "secondary2": "SecondaryWeapon2",
    "engine": "Engine",
    "shields": "ShieldProjector",
    "systems": "Systems",
    "armor": "Armor",
    "reactor": "Reactor",
    "magazine": "Magazine",
    "sensors": "Sensor",
    "thrusters": "Thruster",
    "capacitor": "Capacitor"
}

COMP_TYPES_REVERSE = {value: key for key, value in COMPONENT_TYPES.items()}

COMPONENT_STRINGS = {
    "PrimaryWeapon": "Primary Weapon",
    "PrimaryWeapon2": "Primary Weapon II",
    "SecondaryWeapon": "Secondary Weapon",
    "SecondaryWeapon2": "Secondary Weapon II",
    "ShieldProjector": "Shields",
    "Engine": "Engine",
    "Systems": "Systems",
    "Armor": "Armor",
    "Reactor": "Reactor",
    "Magazine": "Magazine",
    "Sensor": "Sensors",
    "Thruster": "Thrusters",
    "Capacitor": "Capacitor"
}

COMPONENTS = [
    "PrimaryWeapon",
    "PrimaryWeapon2",
    "SecondaryWeapon",
    "SecondaryWeapon2",
    "Systems",
    "Engine",
    "Armor",
    "Capacitor",
    "Magazine",
    "Reactor",
    "Sensor",
    "Thruster",
]

PLURAL_TO_SINGULAR = {
    "primaries": "primary",
    "secondaries": "secondary",
    "engines": "engine",
    "systems": "systems",
    "shields": "shields"
}

SINGULAR_TO_PLURAL = {v: k for k, v in PLURAL_TO_SINGULAR.items()}
