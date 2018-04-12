"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from data import ships
from variables import settings
from .ships import Ship


class CharacterDatabase(dict):
    """
    Dictionary like object with more attributes to allow for management
    of the character database. Built for 5.5 update, as updating the
    ships database requires the clearing of all data in the characters
    database.
    """

    def __init__(self):
        dict.__init__(self)
        self.version = settings["misc"]["patch_level"]
        self[("TRE", "Example")] = {
            "Server": "DM",
            "Faction": "Imperial",
            "Name": "Example",
            "Legacy": "E_Legacy",
            "Ships": ("Blackbolt", "Rycer"),
            "Ship Objects": {name: Ship(name) for name in ships.sorted_ships.keys()},
            "GUI": "Default"
        }

    def update_servers(self, trans: dict):
        """Update the character database to a new set of servers"""
        updated = {}
        for character, data in self.items():
            character = list(character)
            character[0] = trans[character[0]]
            data["Server"] = character[0]
            character = tuple(character)
            updated[character] = data
        self.clear()
        self.update(updated)

    def get_player_servers(self):
        """Get a dictionary of player_name: network"""
        character_names = {}
        names = []
        for server, name in self.keys():
            if name in names:
                if name in character_names:
                    del character_names[name]
                continue
            print("[CharacterDatabase] Found character:", server, name)
            character_names[name] = server
            names.append(name)
        return character_names

    def get_player_legacies(self):
        """Get a dictionary player_name: legacy_name"""
        character_legacies = {}
        names = []
        for server, name in self.keys():
            legacy = self[(server, name)]["Legacy"]
            if name in names:
                if name in character_legacies:
                    del character_legacies[name]
                continue
            character_legacies[name] = legacy
            names.append(name)
        return character_legacies
