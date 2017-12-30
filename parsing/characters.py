# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from variables import settings_obj
from .ships import Ship
from . import abilities


class CharacterDatabase(dict):
    """
    Dictionary like object with more attributes to allow for management of the character database. Built for 5.5 update,
    as updating the ships database requires the clearing of all data in the characters database.
    """

    def __init__(self):
        dict.__init__(self)
        self.version = settings_obj["misc"]["patch_level"]
        self[("TRE", "Example")] = {"Server": "DM",
                                    "Faction": "Imperial",
                                    "Name": "Example",
                                    "Legacy": "E_Legacy",
                                    "Ships": ("Blackbolt", "Rycer"),
                                    "Ship Objects": {name: Ship(name) for name in abilities.sorted_ships.keys()},
                                    "GUI": "Default"}

    def update_servers(self, trans):
        """
        Update the character database to a new set of servers
        """
        updated = {}
        for character, data in self.items():
            character = list(character)
            character[0] = trans[character[0]]
            data["Server"] = character[0]
            character = tuple(character)
            updated[character] = data
        self.clear()
        self.update(updated)

