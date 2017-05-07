# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from os import path
import pickle as pickle

ships = {
    "Decimus": "Imperial_B-5_Decimus",
    "Quell": "Imperial_F-T2_Quell",
    "Imperium": "Imperial_FT-3C_Imperium",
    "Rycer": "Imperial_F-T6_Rycer",
    "Mangler": "Imperial_GSS-3_Mangler",
    "Jurgoran": "Imperial_GSS-4Y_Jurogran",
    "Dustmaker": "Imperial_GSS-5C_Dustmaker",
    "Onslaught": "Imperial_G-X1_Onslaught",
    "Frostburn": "Imperial_ICA-2B_Frostburn",
    "Sable Claw": "Imperial_ICA-3A_-_Sable_Claw",
    "Tormentor": "Imperial_ICA-X_Tormentor",
    "Ocula": "Imperial_IL-5_Ocula",
    "Demolisher": "Imperial_K-52_Demolisher",
    "Razorwire": "Imperial_M-7_Razorwire",
    "Blackbolt": "Imperial_S-12_Blackbolt",
    "Sting": "Imperial_S-13_Sting",
    "Bloodmark": "Imperial_S-SC4_Bloodmark",
    "Gladiator": "Imperial_TZ-24_Gladiator",
    "Mailoc": "Imperial_VX-9_Mailoc",
    "Banshee": "Republic_Banshee",
    "Flashfire": "Republic_Flashfire",
    "Pike": "Republic_FT-6_Pike",
    "Clarion": "Republic_FT-7B_Clarion",
    "Star Guard": "Republic_FT-8_Star_Guard",
    "Firehauler": "Republic_G-X1_Firehauler",
    "Skybolt": "Republic_IL-5_Skybolt",
    "Strongarm": "Republic_K-52_Strongarm",
    "Novadive": "Republic_NovaDive",
    "Rampart Mark Four": "Republic_Rampart_Mark_Four",
    "Comet Breaker": "Republic_SGS-41B_Comet_Breaker",
    "Quarrel": "Republic_SGS-45_Quarrel",
    "Condor": "Republic_SGS-S1_Condor",
    "Sledgehammer": "Republic_Sledgehammer",
    "Spearpoint": "Republic_Spearpoint",
    "Enforcer": "Republic_TZ-24_Enforcer",
    "Redeemer": "Republic_VX-9_Redeemer",
    "Warcarrier": "Republic_Warcarrier",
    "Whisper": 'Republic_X5-Whisper',
    "Mirage": "Republic_X7-Mirage",
    "Legion": "Imperial_B-4D_Legion"
}


class Ship(object):
    def __init__(self, ship_name):
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "ships.db")), "rb") as f:
            self.ships_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "categories.db")),
                  "rb") as f:
            self.categories_data = pickle.load(f)
        if ship_name not in self.ships_data:
            self.ship_name = ships[ship_name]
        else:
            self.ship_name = ship_name
        self.data = self.ships_data[self.ship_name]
        self.components = {
            "primary": None,
            "primary2": None,
            "secondary": None,
            "secondary2": None,
            "engine": None,
            "shields": None,
            "systems": None,
            "armor": None,
            "reactor": None,
            "magazine": None,
            "sensors": None,
            "thrusters": None,
            "capacitor": None
        }

    def __setitem__(self, item, value):
        if item in self.components:
            self.components[item] = value
        else:
            self.ships_data[item] = value

    def __getitem__(self, item):
        if item in self.components:
            return self.components[item]
        else:
            return self.ships_data[item]

    def __iter__(self):
        for key, value in self.ships_data.items():
            yield (key, value)

    def update(self, dictionary):
        for key, value in dictionary.items():
            self[key] = value

    def iter_components(self):
        for key, value in self.components.items():
            yield (key, value)


class Component(object):
    def __init__(self, modifiers):
        self.modifiers = modifiers

    def __setitem__(self, key, value):
        self.modifiers[key] = value

    def __getitem__(self, key):
        if key not in self.modifiers:
            self.modifiers[key] = 1.0
        return self.modifiers[key]

    def __iter__(self):
        for key, value in self.modifiers:
            yield (key, value)
