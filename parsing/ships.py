"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from os import path
import pickle as pickle
from data.ships import ship_names


class Ship(object):
    def __init__(self, ship_name):
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "ships.db")),
                  "rb") as f:
            ships_data = pickle.load(f)
        if ship_name not in ships_data:
            self.ship_name = ship_names[ship_name]
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
            tier, upgrade = map(int, key)
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
