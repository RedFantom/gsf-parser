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
    "Jurgoran": "Imperial_GSS-4Y_Jurgoran",
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

reverse_ships = {value.replace("Republic_", "").replace("Imperial_", "").replace("_", " "): key for key, value in
                 ships.items()}
other_ships = {value.replace("Imperial_", "").replace("Republic_", "").replace("_", " "): key for key, value in
               ships.items()}

companions_db_categories = {
    "Engineering": 0,
    "Offensive": 1,
    "Tactical": 2,
    "Defensive": 3,
    "CoPilot": 4
}


class Ship(object):
    def __init__(self, ship_name):
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "ships.db")),
                  "rb") as f:
            ships_data = pickle.load(f)
        if ship_name not in ships_data:
            self.ship_name = ships[ship_name]
        else:
            self.ship_name = ship_name
        self.name = ship_name
        self.data = ships_data[self.ship_name]
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
        self.crew = {
            "Engineering": None,
            "Offensive": None,
            "Tactical": None,
            "Defensive": None,
            "CoPilot": None
        }

    def __setitem__(self, item, value):
        print("Setting item...")
        item = self.process_key(item)
        if item in self.components:
            self.components[item] = value
        elif item in self.crew:
            self.crew[item] = value
        else:
            self.data[item] = value

    def __getitem__(self, item):
        item = self.process_key(item)
        if item in self.components:
            return self.components[item]
        elif item in self.crew:
            return self.crew[item]
        else:
            print("Key not component or crew: '{}'".format(item))
            return self.data[item]

    def __iter__(self):
        for key, value in self.data.items():
            yield (key, value)

    def process_key(self, item):
        if item == "PrimaryWeapon":
            item = "primary"
        elif item == "PrimaryWeapon2":
            item = "primary2"
        elif item == "SecondaryWeapon":
            item = "secondary"
        elif item == "SecondaryWeapon2":
            item = "secondary2"
        elif item == "ShieldProjector":
            item = "shields"
        elif item == "Sensor":
            item = "sensors"
        elif item == "Thruster":
            item = "thrusters"
        elif item.lower() in self.components:
            item = item.lower()
        return item

    def update(self, dictionary):
        for key, value in dictionary.items():
            self[key] = value

    def iter_components(self):
        for key, value in self.components.items():
            yield (key, value)


class Component(object):
    def __init__(self, data, index, category):
        """
        :param data:
        """
        self.index = index
        self.category = category
        self.name = data["Name"]
        self.upgrades = {
            0: False,
            1: False,
            2: False,
            (2, 0): False,
            (2, 1): False,
            (3, 0): False,
            (3, 1): False,
            (4, 0): False,
            (4, 1): False
        }

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            tier, upgrade = key
            if upgrade is 0:
                if self[(tier, 1)]:
                    self.upgrades[(tier, 1)] = False
                elif self[(tier, 0)]:
                    return
                else:
                    pass
            elif upgrade is 1:
                if self[(tier, 0)]:
                    self.upgrades[(tier, 1)] = False
                elif self[(tier, 1)]:
                    return
                else:
                    pass
            else:
                raise ValueError("Invalid value passed in tuple key: {0}".format(key))
        self.upgrades[key] = value

    def __getitem__(self, key):
        return self.upgrades[key]

    def __iter__(self):
        for key, value in self.upgrades.items():
            yield key, value


class ShipStats(object):
    def __init__(self, ship):
        self.stats = ship.data["Stats"]
        self.components = {}
        for category, component in ship.components.items():
            pass

    def __getitem__(self, item):
        return self.stats[item]

    def __setitem__(self, item, value):
        self.stats[item] = value

    def __iter__(self):
        for key, value in self.stats.items():
            yield key, value

