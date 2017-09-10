# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import _pickle as pickle
from tools.utilities import get_temp_directory
import os


class StrategyDatabase(object):
    """
    A data class storing Strategy objects and making them accessible in a dictionary like manner. Also allows saving
    itself to a file and reloading it from a default path.
    """
    def __init__(self, **kwargs):
        """
        :param file_name: Path (absolute or relative) to the file where the strategy database should be saved. If not
                          set, then the default is used in a temporary directory.
        """
        self._file_name = kwargs.pop("file_name", os.path.join(get_temp_directory(), "strategies.db"))
        self.data = {}
        if not os.path.exists(self._file_name):
            self.save_database()
        self.load_database()

    """
    These functions are similar to dictionary functionality
    """

    def __delitem__(self, key):
        del self.data[key]
        self.save_database()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if not isinstance(value, Strategy):
            raise ValueError("Incompatible data type for StrategyDatabase: {0}".format(value))
        self.data[key] = value
        self.save_database()

    def __iter__(self):
        for key, value in self.data.items():
            yield key, value

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def load_database(self):
        """
        Attempt to load the database from the path set in __init__ . Creates a new database if the database is either
        not available or corrupted.
        """
        try:
            with open(self._file_name, "rb") as fi:
                self.data = pickle.load(fi)
        except (OSError, EOFError, ImportError, AttributeError) as e:
            print("Creating new database as the result of ", e)
            self.new_database()

    def save_database(self):
        """
        Save the database to the file in the path set in __init__
        """
        with open(self._file_name, "wb") as fo:
            pickle.dump(self.data, fo)

    def save_database_as(self, file_name):
        """
        Save the database to a file in a different path than the one set in __init__ .
        :param file_name: Custom path to save database to
        :return: None
        """
        with open(file_name, "wb") as fo:
            pickle.dump(self.data, fo)

    def merge_database(self, other_database):
        """
        Function to merge in another StrategyDatabase object. Data in the existing database is overwritten if the keys
        in the dictionaries are the same.
        """
        # TODO: Improve database importing to a non-destructive method
        self.data.update(other_database.data)
        self.save_database()

    def new_database(self):
        """
        For whatever reason reset the data in the current database and then save the database before loading it in order
        to create the file and eliminate any errors that may have occurred while loading. Resets the full
        StrategyDatabase contents, thus discarding any Strategies, Phases and Items.
        """
        self.data = {}
        self.save_database()
        self.load_database()


class Strategy(object):
    """
    Simple data class to store the phases of a strategy and properties such as description and map
    """
    def __init__(self, name, map):
        """
        :param name: name of the Strategy
        :param map: map tuple (match_type, location)
        """
        self.name = name
        self.map = map
        self.phases = {}
        self.description = ""

    """
    These functions are similar to dictionary functionality
    """

    def __getitem__(self, item):
        if item is None:
            return self
        return self.phases[item]

    def __setitem__(self, key, value):
        if not isinstance(value, Phase):
            raise ValueError("Incompatible data type for Strategy: {0}".format(value))
        self.phases[key] = value

    def __iter__(self):
        for key, value in self.phases.items():
            yield key, value

    def __delitem__(self, key):
        del self.phases[key]

    def __contains__(self, item):
        return item in self.phases


class Phase(object):
    """
    Simple data class to store the Items of a Phase of a Strategy
    """
    def __init__(self, name, map):
        """
        :param name: Phase name
        :param map: map tuple (match_type, location)
        """
        self.items = {}
        self.name = name
        self.map = map
        self.description = ""

    """
    These functions are similar to dictionary functionality
    """

    def __setitem__(self, key, value):
        if not isinstance(value, Item):
            raise ValueError("Incompatible data type for Phase: {0}".format(value))
        self.items[key] = value

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        for key, value in self.items.items():
            yield key, value

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __delitem__(self, item):
        del self.items[item]


class Item(object):
    """
    Simple data class that provides a dictionary like interface with a limited functionality and a limited number of
    keys that can be used, so it does not store any more data than is required for an Item.
    """
    def __init__(self, name, x, y, color, font):
        """
        :param name: Item name
        :param x: Item location x coordinate
        :param y: Item location y coordinate
        :param color: HTML-color value
        :param font: font tuple (family, size, *options)
        """
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
