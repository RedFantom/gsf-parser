"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from os import path
import pickle as pickle
# Project Modules
from data import abilities
from data.components import *
from data.ships import ship_names, ships_names_reverse
from utils.directories import get_assets_directory


def get_ship_category(ship_name: str):
    """Return the ship category for a given ship name"""
    with open(path.join(get_assets_directory(), "categories.db"), "rb") as fi:
        categories = pickle.load(fi)
    ship_name = ship_name if ship_name not in ship_names else ship_names[ship_name]
    faction = ship_name.split("_")[0]
    ship_name = ship_name.replace("Imperial_", "").replace("Republic_", "")
    categories = categories[faction]
    for category in categories:
        ships = categories[category]["Ships"]
        for ship in ships:
            if ship["JsonPath"].replace(".json", "") == ship_name:
                return category["CategoryName"]
    return None


def load_ship_data()->dict:
    with open(path.join(get_assets_directory(), "ships.db"), "rb") as f:
        ships_data = pickle.load(f)
    return ships_data


class Ship(object):
    """
    Data class that contains the data required to perform calculations
    for and operations on GSF Ships. For every Ship, the components and
    selected crew members are selected.

    :attribute name: Simple ship name
    :attribute ship_name: Fully-Qualified Ship name
    """

    def __init__(self, ship_name: str, ships_data: dict = None):
        """
        :param ship_name: FQ or Simple ship name
        """
        if ships_data is None:
            ships_data = load_ship_data()
        # Find FQN and simple ship name
        self.ship_name = ship_name if ship_name in ships_data else ship_names[ship_name]  # FQN
        self.faction = self.ship_name.split("_")[0]
        self.name = ship_name if ship_name in ship_names else ships_names_reverse[self.ship_name]
        # Initialize attributes
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

    def __setitem__(self, item: str, value):
        """
        Update a given Component or Crew
        :param item: Component or Crew category
        :param value: Component instance or Crew member name
        """
        item = self.process_key(item)
        if item in self.components:
            self.components[item] = value
        elif item in self.crew:
            self.crew[item] = value
        else:
            raise ValueError("Invalid key for Ship: '{}'".format(item))

    def __getitem__(self, item):
        """Returns a Component instance or Crew member name"""
        item = self.process_key(item)
        if item in self.components:
            return self.components[item]
        elif item in self.crew:
            return self.crew[item]
        raise KeyError("Invalid key for [Ship] instance: {}".format(item))

    def __iter__(self):
        for key, value in self.data.items():
            yield (key, value)

    def __contains__(self, item):
        return item in self.components or item in self.crew

    def process_key(self, item):
        """
        Not all keys may be appropriate for usage in components
        dictionary. The categories used in the data dictionary differ
        from those used in this Ship.components dictionary, and thus,
        must be translated appropriately.
        """
        if item in COMP_TYPES_REVERSE:
            return COMP_TYPES_REVERSE[item]
        elif item.lower() in self.components:
            item = item.lower()
        if item not in self.components and item not in self.crew:
            return None
        return item

    def update(self, dictionary):
        for key, value in dictionary.items():
            self[key] = value

    def iter_components(self):
        for key, value in self.components.items():
            yield (key, value)

    @property
    def ship_class(self):
        ident = self.ship_name.split("_")[1]
        if "B" in ident or "M" in ident:
            return "Bomber"
        elif "G" in ident:
            return "Gunship"
        elif "S" in ident:
            return "Scout"
        elif "F" in ident:
            return "Strike Fighter"
        else:
            return None


class Component(object):
    """
    The Component class supports the storage of attributes for
    Components in a Ship.

    :attribute index: Index in ships.db[ship_name][category][index]
        is the component data dictionary
    :attribute category: Component category
    :attribute name: Component name
    :attribute upgrades: Upgrade dictionary
    """

    def __init__(self, data, index, category):
        """
        :param data: Component data dictionary
        :param index: Component index in this category
        :param category: Component category
        """
        self.index = index
        self.category = category
        self.name = data["Name"]
        self.upgrades = {
            (0, 0): False,
            (1, 0): False,
            (2, 0): False,
            (2, 1): False,
            (3, 0): False,
            (3, 1): False,
            (4, 0): False,
            (4, 1): False
        }
        for category in COMPONENT_TYPES.keys():
            category = category.replace("2", str())
            if self.name in getattr(abilities, category).values():
                for type in ["majors", "middle", "minors"]:
                    if category in getattr(abilities, type):
                        self.type = type.replace("s", str())
                        break
                if hasattr(self, "type"):
                    break
        if not hasattr(self, "type"):
            raise ValueError("Invalid component: {}".format(self.name))

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
