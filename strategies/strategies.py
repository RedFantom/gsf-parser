# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import _pickle as pickle
from strategies.tools import get_temp_directory
import os


class StrategyDatabase(object):
    def __init__(self, **kwargs):
        self._file_name = kwargs.pop("file_name", os.path.join(get_temp_directory(), "strategies.db"))
        self.data = {}
        if not os.path.exists(self._file_name):
            self.save_database()
        self.load_database()

    def __delitem__(self, key):
        del self.data[key]
        self.save_database()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save_database()

    def __iter__(self):
        for key, value in self.data.items():
            yield key, value

    def __len__(self):
        return len(self.data)

    def load_database(self):
        print("Loading database")
        try:
            with open(self._file_name, "rb") as fi:
                self.data = pickle.load(fi)
        except EOFError:
            print("Creating new database because of EOFError")
            self.save_database()
            self.load_database()
        except ImportError as e:
            print("Creating new database because of ImportError: ", e)
            self.save_database()
            self.load_database()
        except AttributeError as e:
            print("Creating new database because of AttributeError: ", e)
            self.save_database()
            self.load_database()

    def save_database(self):
        print("Saving database")
        with open(self._file_name, "wb") as fo:
            pickle.dump(self.data, fo)

    def save_database_as(self, file_name):
        with open(file_name, "wb") as fo:
            pickle.dump(self.data, fo)

    def merge_database(self, other_database):
        self.data.update(other_database.data)
        self.save_database()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()


class Strategy(object):
    def __init__(self, name, map):
        self.name = name
        self.map = map
        self.phases = {}
        self.description = ""

    def __getitem__(self, item):
        return self.phases[item]

    def __setitem__(self, key, value):
        self.phases[key] = value

    def __iter__(self):
        for key, value in self.phases.items():
            yield key, value

    def __del__(self, key):
        del self.phases[key]


class Phase(object):
    def __init__(self, name, map):
        self.items = {}
        self.name = name
        self.map = map
        self.description = ""

    def __setitem__(self, key, value):
        self.items[key] = value

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        for key, value in self.items.items():
            yield key, value

    def __len__(self):
        return len(self.items)


class Item(object):
    def __init__(self, name, x, y, color, font):
        self.data = {
            "name": name,
            "x": x,
            "y": y,
            "color": color,
            "font": font
        }

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        if key not in self.data:
            raise ValueError("Invalid key: ", key)
        self.data[key] = value
