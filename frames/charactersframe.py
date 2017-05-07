# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
import pickle as pickle
import os
from tools import utilities


class CharactersFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.directory = utilities.get_temp_directory()
        if "characters.db" not in os.listdir(self.directory):
            servers = {"BAS": "The Bastion",
                       "BEG": "Begeren Colony",
                       "SHA": "The Shadowlands",
                       "JUN": "Jung Ma",
                       "EBH": "The Ebon Hawk",
                       "PRF": "Prophecy of the Five",
                       "T3M": "T3-M4",
                       "NTH": "Darth Nihilus",
                       "TFN": "The Tomb of Freedon Nadd",
                       "JKS": "Jar'kai Sword",
                       "PRG": "The Progenitor",
                       "VCH": "Vanjervalis Chain",
                       "BMD": "Battle Meditation",
                       "MFR": "Mantle of the Force",
                       "TRE": "The Red Eclipse"}
            characters = {server: None for server in servers}
            with open(os.path.join(self.directory, "characters.db"), "wb") as f:
                pickle.dump(characters, f)
        # with open(os.path.join(self.directory, "characters.db"), "wb") as f:
        #    self.characters = pickle.load(f)

    def grid_widgets(self):
        pass


class Character(object):
    def __init__(self, server, faction, name):
        self.ships = {
            "Decimus": None,
            "Quell": None,
            "Imperium": None,
            "Rycer": None,
            "Mangler": None,
            "Jurgoran": None,
            "Dustmaker": None,
            "Onslaught": None,
            "Frostburn": None,
            "Sable Claw": None,
            "Tormentor": None,
            "Ocula": None,
            "Demolisher": None,
            "Razorwire": None,
            "Blackbolt": None,
            "Sting": None,
            "Bloodmark": None,
            "Gladiator": None,
            "Mailoc": None,
            "Banshee": None,
            "Flashfire": None,
            "Pike": None,
            "Clarion": None,
            "Star Guard": None,
            "Firehauler": None,
            "Skybolt": None,
            "Strongarm": None,
            "Novadive": None,
            "Rampart Mark Four": None,
            "Comet Breaker": None,
            "Quarrel": None,
            "Condor": None,
            "Sledgehammer": None,
            "Spearpoint": None,
            "Enforcer": None,
            "Redeemer": None,
            "Warcarrier": None,
            "Whisper": None,
            "Mirage": None
        }
        self.server = server
        self.faction = faction
        self.name = name

    def __setitem__(self, key, value):
        if key not in self.ships:
            if key == "server" or key == "faction" or key == "name":
                raise ValueError("Server, faction and name are not mutable.")
            else:
                raise ValueError("Attempted to set a non-existent ship: %s" % key)
        self.ships[key] = value

    def __getitem__(self, key):
        if key == "server":
            return self.server
        elif key == "faction":
            return self.faction
        elif key == "name":
            return self.name
        else:
            return self.ships[key]
