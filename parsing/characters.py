"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
# UI Libraries
from toplevels.choice import askoption
# Packages
from semantic_version import Version
# Project Modules
from data import ships, servers
from variables import settings
from parsing.ships import Ship, Component
from data import ships as ships_data
from utils.swtor import get_swtor_directory


class CharacterDatabase(dict):
    """
    Dictionary like object with more attributes to allow for management
    of the character database. Built for 5.5 update, as updating the
    ships database requires the clearing of all data in the characters
    database.
    """

    # Provides a translation dictionary for updating old character
    # databases to the SWTOR United Forces server merges
    UNITED_FORCES = {
        "TRE": "DM",
        "PRG": "DM",
        "TFN": "DM",
        "JCO": "SF",
        "SHA": "SF",
        "EBH": "SF",
        "PRF": "SF",
        "JUN": "SF",
        "MFR": "TL",
        "BMD": "TL",
        "NTH": "TL",
        "T3M": "TH",
        "VCH": "TH",
        "JKS": "TH"
    }

    def __init__(self):
        dict.__init__(self)
        self.version = settings["misc"]["patch_level"]
        self[("DM", "Example")] = {
            "Server": "DM",
            "Faction": "Imperial",
            "Name": "Example",
            "Legacy": "E_Legacy",
            "Ships": ("Blackbolt", "Rycer"),
            "Ship Objects": {name: Ship(name) for name in ships.sorted_ships.keys()},
            "GUI": "Default",
            "Discord": False,
        }

    def update_database(self):
        """Update the database by checking version numbers"""
        self.version = str(self.version)
        if not self.version.endswith(".0"):
            self.version += ".0"
        version = Version(self.version)
        print("[CharacterDatabase] This version: ", version)
        if version < Version("5.6.0"):
            print("[CharacterDatabase] Updating database for Discord Bot")
            for character, data in self.items():
                data.update({"Discord": False})
                self[character] = data
            settings["misc"]["patch_level"] = "5.6.0"
            settings.save_settings()
        if version < Version("5.9.2"):
            print("[CharacterDatabase] Updating database for new upgrade indices")
            for character, data in self.items():
                for ship, ship_obj in data["Ship Objects"].items():
                    if ship_obj is None:
                        continue
                    for ctg, comp in ship_obj.components.items():
                        if comp is None:
                            continue
                        for upgrade, state in comp.upgrades.copy().items():
                            if not isinstance(upgrade, int):
                                continue
                            del self[character]["Ship Objects"][ship].components[ctg].upgrades[upgrade]
                            self[character]["Ship Objects"][ship].components[ctg].upgrades[(upgrade, 0)] = state
        self.version = settings["misc"]["patch_level"]
        self.update_characters()

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

    def get_server_for_character(self, character: str):
        """Return the server name for a character"""
        servers = list()
        for server, name in self.keys():
            if character == name:
                servers.append(server)
        if len(servers) == 0:
            return None
        if len(servers) > 1:
            return None
        return servers[0]

    def update_characters(self):
        """Insert all the characters ever played into the database"""
        print("[CharacterDatabase] Updating characters")
        path = os.path.join(get_swtor_directory(), "swtor", "settings")
        gui_state_files = os.listdir(path)
        for file in gui_state_files:
            if not file.endswith("PlayerGUIState.ini"):
                continue
            elements = file.split("_")
            if len(elements) == 3:
                server, player_name, _ = elements
            else:
                server, first, last, _ = elements
                player_name = "{} {}".format(first, last)
            if server not in servers.server_keys:
                print("[CharacterDatabase] Ignored GUIState file: {}".format(file))
                continue
            server = servers.server_keys[server]
            if (server, player_name) in self:
                continue
            name = servers.servers[server]
            faction = askoption(("Republic", "Imperial"), label="Faction for {} on {}".format(player_name, name))
            ships_dict = {name: Ship(name) for name in ships_data.sorted_ships.values()}
            ships_list = list()
            print("[CharacterDatabase] Inserting previously unknown character: {}".format((server, player_name)))
            self[(server, player_name)] = {
                "Server": server,
                "Faction": faction,
                "Name": player_name,
                "Legacy": player_name,
                "Ships": ships_list,
                "Ship Objects": ships_dict,
                "GUI": "Default",
                "Discord": False
            }
