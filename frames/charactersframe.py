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
from widgets import VerticalScrollFrame
from PIL import Image, ImageTk
from tools.utilities import get_assets_directory
from parsing.guiparsing import GSFInterface, get_gui_profiles
from toplevels.addcharacter import AddCharacter
import variables
from parsing import abilities
from collections import OrderedDict


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
        try:
            with open(os.path.join(self.directory, "characters.db"), "rb") as f:
                self.characters = pickle.load(f)
        except OSError or EOFError:
            self.new_database()
        self.characters_list = ttk.Treeview(self, columns=("Characters",), displaycolumns=("Characters",))
        self.characters_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.characters_list.yview)
        self.characters_list.configure(yscrollcommand=self.characters_scroll.set, height=14)
        self.characters_list.heading("Characters", text="Characters")
        self.characters_list["show"] = "headings"
        self.characters_list.column("Characters", width=250, stretch=False, anchor=tk.E)
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=450)
        self.options_frame = self.scroll_frame.interior
        self.new_character_button = ttk.Button(self, text="Add character", command=self.new_character)

        self.republic_logo = ImageTk.PhotoImage(
            Image.open(os.path.join(get_assets_directory(), "icons", "republic_s.png")))
        self.imperial_logo = ImageTk.PhotoImage(
            Image.open(os.path.join(get_assets_directory(), "icons", "imperial_s.png")))

        # Character option widgets
        self.character_name_label = ttk.Label(self.options_frame, text="Character name")
        self.character_name_entry = ttk.Entry(self.options_frame, width=35)
        self.legacy_name_label = ttk.Label(self.options_frame, text="Legacy name")
        self.legacy_name_entry = ttk.Entry(self.options_frame, width=35)
        self.faction = tk.StringVar()
        self.faction.set("imperial")
        self.faction_label = ttk.Label(self.options_frame, text="Faction")
        self.faction_republic_radiobutton = ttk.Radiobutton(self.options_frame, text="Republic",
                                                            image=self.republic_logo, compound=tk.LEFT,
                                                            variable=self.faction, value="republic",
                                                            command=lambda: self.set_character_faction("republic"))
        self.faction_imperial_radiobutton = ttk.Radiobutton(self.options_frame, text="Empire", image=self.imperial_logo,
                                                            compound=tk.LEFT, variable=self.faction, value="imperial",
                                                            command=lambda: self.set_character_faction("imperial"))
        self.gui_profile = tk.StringVar()
        self.gui_profile_label = ttk.Label(self.options_frame, text="GUI Profile")
        self.gui_profile_dropdown = ttk.OptionMenu(self.options_frame, self.gui_profile, *tuple(get_gui_profiles()))
        self.gui_profile_detect_button = ttk.Button(self.options_frame, text="Auto detect", command=self.detect_profile)
        self.lineup_label = ttk.Label(self.options_frame, text="Ships line-up")
        self.lineup_frame = ttk.Frame(self.options_frame)

        self.imp_ship_widgets = OrderedDict()
        self.imp_ship_variables = OrderedDict()
        self.rep_ship_widgets = OrderedDict()
        self.rep_ship_variables = OrderedDict()

        for ship_name in abilities.all_ships.keys():
            self.imp_ship_variables[ship_name] = tk.IntVar()
            self.imp_ship_widgets[ship_name] = ttk.Checkbutton(self.lineup_frame, text=ship_name,
                                                               variable=self.imp_ship_variables[ship_name])
        for ship_name in abilities.all_ships.values():
            self.rep_ship_variables[ship_name] = tk.IntVar()
            self.rep_ship_widgets[ship_name] = ttk.Checkbutton(self.lineup_frame, text=ship_name,
                                                               variable=self.rep_ship_variables[ship_name])

    def grid_widgets(self):
        self.widgets_grid_forget()
        self.characters_list.grid(column=0, row=0, sticky="nswe", padx=5, pady=5)
        self.characters_scroll.grid(column=1, row=0, sticky="ns", pady=5)
        self.new_character_button.grid(column=0, row=1, sticky="nswe", pady=5, padx=5)
        self.scroll_frame.grid(column=2, row=0, rowspan=2, sticky="nswe", padx=5)
        self.character_name_label.grid(column=0, row=0, sticky="nsw", padx=5, pady=5)
        self.character_name_entry.grid(column=0, row=1, sticky="nswe", padx=5, pady=5)
        self.legacy_name_label.grid(column=1, row=0, sticky="nsw", padx=5, pady=5)
        self.legacy_name_entry.grid(column=1, row=1, sticky="nswe", padx=5, pady=5)
        self.faction_label.grid(column=0, row=2, sticky="nsw", padx=5, pady=5)
        self.faction_republic_radiobutton.grid(column=0, row=3, sticky="nsw", padx=5, pady=5)
        self.faction_imperial_radiobutton.grid(column=1, row=3, sticky="nsw", padx=5, pady=5)
        self.gui_profile_label.grid(column=0, row=4, sticky="nsw", padx=5, pady=5)
        self.gui_profile_dropdown.grid(column=0, row=5, sticky="nswe", padx=5, pady=5)
        self.gui_profile_detect_button.grid(column=1, row=5, sticky="nswe", padx=5, pady=5)
        self.lineup_label.grid(column=0, row=6, sticky="nsw", padx=5, pady=5)
        self.lineup_frame.grid(column=0, row=7, rowspan=2, columnspan=3, sticky="nswe", padx=5, pady=5)
        set_row = 0
        set_column = 0
        if self.faction.get() == "imperial":
            for item in self.imp_ship_widgets.values():
                item.grid(row=set_row, column=set_column, padx=5, pady=5, sticky="w")
                set_row += 1
                if set_row == 5:
                    set_column += 1
                    set_row = 0
        elif self.faction.get() == "republic":
            for item in self.rep_ship_widgets.values():
                item.grid(row=set_row, column=set_column, pady=5, sticky="w")
                set_row += 1
                if set_row == 5:
                    set_column += 1
                    set_row = 0
        else:
            raise ValueError("Invalid value for faction found: {0}".format(self.faction.get()))

    def widgets_grid_forget(self):
        for item in self.imp_ship_widgets.values():
            item.grid_forget()
        for item in self.rep_ship_widgets.values():
            item.grid_forget()

    def new_database(self):
        characters = {server: None for server in self.servers}
        with open(os.path.join(self.directory, "characters.db"), "wb") as f:
            pickle.dump(characters, f)
        self.characters = {}

    def detect_profile(self):
        pass

    def new_character(self):
        AddCharacter(variables.main_window, tuple(self.servers.values()), self.insert_character)

    def insert_character(self, name, legacy, server, faction):
        pass

    def set_character_faction(self, faction):
        print("Setting faction {0}".format(faction))
        print("self.faction == {0}".format(self.faction.get()))
        self.grid_widgets()
        pass
