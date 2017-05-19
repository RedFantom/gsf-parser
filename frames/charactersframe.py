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
        self.servers = {
            "BAS": "The Bastion",
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
            "TRE": "The Red Eclipse"
        }
        if "characters.db" not in os.listdir(self.directory):
            self.new_database()
        with open(os.path.join(self.directory, "characters.db"), "rb") as f:
            self.characters = pickle.load(f)

    def grid_widgets(self):
        pass

    def new_database(self):
        characters = {server: None for server in self.servers}
        with open(os.path.join(self.directory, "characters.db"), "wb") as f:
            pickle.dump(characters, f)
