# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

try:
    import mttkinter.mtTkinter as tk
except ImportError:
    print "mtTkinter not found, please use 'pip install mttkinter'"
    import Tkinter as tk
import ttk
import cPickle as pickle
import os
import tempfile


class CharactersFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        directory = tempfile.gettempdir()
        self.directory = directory.replace("\\temp", "") + "\\GSF Parser"
        if "characters.db" not in os.listdir(self.directory):
            servers = ["BAS", "BEG", "HAR", "SHA", "JUN", "EBH", "PRF", "JCV", "T3M", "NIH", "TFN", "JKS",
                       "PRG", "VCH", "BMD", "MFR", "TRE"]
            characters = {server: None for server in servers}
            with open(os.path.join(self.directory, "characters.db"), "w") as f:
                pickle.dump(characters, f)
        with open(os.path.join(self.directory, "characters.db")) as f:
            self.characters = pickle.load(f)

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
