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
from parsing.guiparsing import get_gui_profiles, get_player_guiname
from toplevels.addcharacter import AddCharacter
import variables
from parsing import abilities
from collections import OrderedDict
from tkinter import messagebox as mb


class CharactersFrame(ttk.Frame):
    """
    A frame in which the user can enter his characters in simple, organized manner, so the GSF Parser can make good use
    of this data in
    """

    def __init__(self, parent):
        """
        Initializes the class instance and sets up all instance variables
        :param parent: tkinter parent
        """
        ttk.Frame.__init__(self, parent)
        self.directory = utilities.get_temp_directory()
        # Lists of servers and abbreviations
        self.servers = {
            "BAS": "The Bastion",
            "BEG": "Begeren Colony",
            "HAR": "The Harbinger",
            "SHA": "The Shadowlands",
            "JUN": "Jung Ma",
            "EBH": "The Ebon Hawk",
            "PRF": "Prophecy of the Five",
            "JCO": "Jedi Covenant",
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
        self.zones = OrderedDict()
        self.zones["USE"] = "US East Coast"
        self.zones["USW"] = "US West Coast"
        self.zones["EUR"] = "Europe"

        self.regions = {
            "USE": ["SHA", "JUN", "EBH", "PRF", "JCO"],
            "USW": ["BAS", "BEG", "HAR"],
            "EUR": ["T3M", "NTH", "TFN", "JKS", "PRG", "VCH", "BMD", "MFR", "TRE"]
        }
        # Create a dictionary that is the reverse of self.servers
        self.reverse_servers = {value: key for key, value in self.servers.items()}
        # Try to load the character database
        if "characters.db" not in os.listdir(self.directory):
            self.new_database()
        try:
            with open(os.path.join(self.directory, "characters.db"), "rb") as f:
                self.characters = pickle.load(f)
        except OSError:
            self.new_database()
        except EOFError:
            self.new_database()
        # Set up the characters list
        self.characters_list = ttk.Treeview(self)
        self.characters_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.characters_list.yview)
        self.characters_list.configure(yscrollcommand=self.characters_scroll.set, height=14)
        self.characters_list.heading("#0", text="Characters")
        # self.characters_list.column("", width=0)
        self.characters_list.column("#0", width=250)
        self.characters_list["show"] = ("tree", "headings")
        self.characters_list.columnconfigure(0, minsize=50)
        # Create all the widgets for the character properties
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=450, canvasheight=350)
        self.options_frame = self.scroll_frame.interior
        self.new_character_button = ttk.Button(self, text="Add character", command=self.new_character)

        self.save_button = ttk.Button(self, text="Save", command=self.save_character_data)
        self.discard_button = ttk.Button(self, text="Discard", command=self.discard_character_data)
        self.delete_button = ttk.Button(self, text="Delete", command=self.delete_character)

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
        self.faction.set("Imperial")
        self.faction_label = ttk.Label(self.options_frame, text="Faction")
        self.faction_republic_radiobutton = ttk.Radiobutton(self.options_frame, text="Republic",
                                                            image=self.republic_logo, compound=tk.LEFT,
                                                            variable=self.faction, value="Republic",
                                                            command=lambda: self.set_character_faction("Republic"))
        self.faction_imperial_radiobutton = ttk.Radiobutton(self.options_frame, text="Empire", image=self.imperial_logo,
                                                            compound=tk.LEFT, variable=self.faction, value="Imperial",
                                                            command=lambda: self.set_character_faction("Imperial"))
        self.gui_profile = tk.StringVar()
        self.gui_profile_label = ttk.Label(self.options_frame, text="GUI Profile")
        self.gui_profile_dropdown = ttk.OptionMenu(self.options_frame, self.gui_profile,
                                                   *tuple(("Select", "Default") + tuple(get_gui_profiles())))
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
                                                               variable=self.imp_ship_variables[ship_name],
                                                               command=self.update_ships)
        for ship_name in abilities.all_ships.values():
            self.rep_ship_variables[ship_name] = tk.IntVar()
            self.rep_ship_widgets[ship_name] = ttk.Checkbutton(self.lineup_frame, text=ship_name,
                                                               variable=self.rep_ship_variables[ship_name],
                                                               command=self.update_ships)

        self.characters_list.bind("<Double-1>", self.set_character)
        self.character_data = None

        self.update_tree()

    def update_ships(self):
        """
        Update the ships in the character_data and save the database instantly
        :return: None
        """
        if self.character_data["Faction"] == "Imperial":
            ships = tuple(ship for ship, intvar in self.imp_ship_variables.items() if intvar.get() == 1)
        elif self.character_data["Faction"] == "Republic":
            ships = tuple(ship for ship, intvar in self.rep_ship_variables.items() if intvar.get() == 1)
        else:
            raise ValueError("Unknown value for faction found: {0}".format(self.character_data["Faction"]))
        self.character_data["Ships"] = ships
        self.save_button.invoke()

    def grid_widgets(self):
        """
        Add all the widgets to the UI, after clearing the frame first
        :return: None
        """
        self.widgets_grid_forget()
        self.characters_list.grid(column=0, row=0, sticky="nswe", padx=5, pady=5)
        self.characters_scroll.grid(column=1, row=0, sticky="ns", pady=5)
        self.new_character_button.grid(column=0, row=1, sticky="nswe", pady=5, padx=5)
        self.scroll_frame.grid(column=2, row=0, rowspan=2, columnspan=4, sticky="nswe", padx=5)

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
        self.lineup_frame.grid(column=0, row=7, rowspan=1, columnspan=3, sticky="nswe", padx=5, pady=5)

        self.delete_button.grid(column=2, row=1, sticky="nswe", pady=5, padx=5)
        self.discard_button.grid(column=3, row=1, sticky="nswe", pady=5, padx=5)
        self.save_button.grid(column=4, row=1, sticky="nswe", pady=5, padx=5)

        set_row = 0
        set_column = 0
        if self.faction.get() == "Imperial":
            for item in self.imp_ship_widgets.values():
                item.grid(row=set_row, column=set_column, padx=5, pady=5, sticky="w")
                set_row += 1
                if set_row == 5:
                    set_column += 1
                    set_row = 0
        elif self.faction.get() == "Republic":
            for item in self.rep_ship_widgets.values():
                item.grid(row=set_row, column=set_column, pady=5, sticky="w")
                set_row += 1
                if set_row == 5:
                    set_column += 1
                    set_row = 0
        else:
            raise ValueError("Invalid value for faction found: {0}".format(self.faction.get()))

    def update_tree(self):
        """
        Update the Treeview self.characters_list with all the characters found in the character database
        :return:
        """
        self.characters_list.delete(*self.characters_list.get_children())

        for identifier, region in self.zones.items():
            self.characters_list.insert("", tk.END, iid=identifier, text=region)
            for server in self.regions[identifier]:
                self.characters_list.insert(identifier, tk.END, iid=server, text=self.servers[server])

        for character, data in self.characters.items():
            self.characters_list.insert(data["Server"], tk.END, iid=(data["Server"], data["Name"]), text=data["Name"])

    def widgets_grid_forget(self):
        """
        Clear the ship Checkbutton widgets
        :return: None
        """
        for item in self.imp_ship_widgets.values():
            item.grid_forget()
        for item in self.rep_ship_widgets.values():
            item.grid_forget()

    def new_database(self):
        """
        Create a new character database with a default entry
        :return: None
        """
        mb.showinfo("Info", "The GSF Parser is creating a new characters database, discarding all your character data, "
                            "if you had any, and ship builds. If you did not expect this, please file an issue report "
                            "in the GitHub repository.")
        characters = {("TRE", "Example"): {"Server": "TRE",
                                           "Faction": "Imperial",
                                           "Name": "Example",
                                           "Legacy": "E_Legacy",
                                           "Ships": ("Blackbolt", "Rycer"),
                                           "Ship Objects": {name: None for name in abilities.all_ships.keys()},
                                           "GUI": "Default"}}
        with open(os.path.join(self.directory, "characters.db"), "wb") as f:
            pickle.dump(characters, f)
        self.characters = {}

    def detect_profile(self):
        """
        Callback for the Auto-detect button, sets the GUI profile according to the result of get_player_guiname or
        display a message that the profile cannot be determined reliably (because of the same name of different servers)
        :return:
        """
        if not self.character_data:
            mb.showinfo("Info", "Please select a character from the list first.")
            return
        try:
            gui_name = get_player_guiname(self.character_data["Name"])
        except ValueError:
            mb.showinfo("Info", "Could not reliably determine the GUI profile used by this character. Please select it "
                                "manually.")
            return
        self.gui_profile.set(gui_name)
        self.character_data["GUI"] = gui_name
        self.save_button.invoke()

    def new_character(self):
        """
        Open the AddCharacter Toplevel to add a character to the database
        :return: None
        """
        AddCharacter(variables.main_window, tuple(self.servers.values()), self.insert_character)

    def insert_character(self, name, legacy, server, faction):
        """
        Callback for the AddCharacter Toplevel
        :param name: character name entered
        :param legacy: legacy name entered
        :param server: server name entered (full name)
        :param faction: faction entered
        :return: None
        """
        if len(server) is not 3:
            pass
        if faction == "Imperial":
            ships = ("Blackbolt", "Rycer")
            ships_dict = {name: None for name in abilities.all_ships.keys()}
        elif faction == "Republic":
            ships = ("Novadive", "Star Guard")
            ships_dict = {name: None for name in abilities.all_ships.values()}
        else:
            raise ValueError("Unknown value for faction found: {0}".format(faction))
        server = self.reverse_servers[server]
        self.characters[(server, name)] = {
            "Server": server,
            "Faction": faction,
            "Name": name,
            "Legacy": legacy,
            "Ships": ships,
            "Ship Objects": ships_dict,
            "GUI": "Default"
        }
        self.character_data = self.characters[(server, name)]
        self.clear_character_data()
        self.set_character(set=False)
        self.save_button.invoke()
        self.update_tree()

    def set_character_faction(self, faction):
        """
        Callback for the faction Radiobuttons, updating the UI and the database
        :param faction: faction name
        :return: None
        """
        self.grid_widgets()
        if not mb.askyesno("Warning", "Changing the faction of a character removes "
                                      "all specified builds for this character. "
                                      "Are you sure you want to change the faction?"):
            return
        if faction == "Imperial":
            ships = ("Blackbolt", "Rycer")
            ships_dict = {name: None for name in abilities.all_ships.keys()}
        elif faction == "Republic":
            ships = ("Novadive", "Star Guard")
            ships_dict = {name: None for name in abilities.all_ships.values()}
        else:
            raise ValueError("Unknown value for faction found: {0}".format(faction))
        self.character_data["Faction"] = faction
        self.character_data["Ship Objects"] = ships_dict
        self.character_data["Ships"] = ships
        self.save_character_data()
        self.update_tree()

    def save_character_data(self):
        """
        General function to save the character database to the file
        :return: None
        """
        self.characters[(self.character_data["Server"], self.character_data["Name"])] = self.character_data
        with open(os.path.join(self.directory, "characters.db"), "wb") as f:
            pickle.dump(self.characters, f)

    def discard_character_data(self):
        """
        Clear the changes to the character data as far as that is possible, as most functions immediately save the data
        entered through a callback that calls save_character_data
        :return: None
        """
        self.clear_character_data()
        self.set_character()

    def delete_character(self):
        """
        Delete a character for the database, callback for the delete_button
        :return: None
        """
        del self.characters[(self.character_data["Server"], self.character_data["Name"])]
        self.characters_list.delete(*((self.character_data["Server"] + " " + self.character_data["Name"]),))
        self.clear_character_data()
        self.save_button.invoke()
        self.update_tree()

    def get_character_data(self):
        """
        Get a character_data dictionary from the selected character in the Treeview
        :return: None
        """
        character = self.characters_list.selection()
        if len(character[0]) < 4:
            return
        server = character[0][:3]
        name = character[0][4:]
        if not server:
            raise ValueError("Server not found: {0}".format(character[0]))
        self.clear_character_data()
        try:
            return self.characters[(server, name)]
        except KeyError:
            mb.showerror("Error", "The character {0} was not found in the internal character database. Please report "
                                  "this error with debug output in the GitHub repository.".format((server, name)))
            raise ValueError("Character not found {0} in {1}".format((server, name), self.characters))

    def set_character(self, set=True, *args):
        """
        Callback for the Treeview to set the character property widgets
        :param set: if False, then it's just the current data that has to be updated
        :param args: for tkinter, not used
        :return: None
        """
        if not set:
            character_data = self.character_data
        else:
            character_data = self.get_character_data()
            if not character_data:
                return
        self.character_name_entry.insert(tk.END, character_data["Name"])
        self.legacy_name_entry.insert(tk.END, character_data["Legacy"])
        self.faction.set(character_data["Faction"])
        self.gui_profile.set(character_data["GUI"])
        if character_data["Faction"] == "Imperial":
            for name, intvar in self.imp_ship_variables.items():
                if name in character_data["Ships"]:
                    intvar.set(1)
                else:
                    intvar.set(0)
        elif character_data["Faction"] == "Republic":
            for name, intvar in self.rep_ship_variables.items():
                if name in character_data["Ships"]:
                    intvar.set(1)
                else:
                    intvar.set(0)
        else:
            raise ValueError("Unknown faction value found: {0}".format(character_data["Faction"]))
        self.character_data = character_data

    def clear_character_data(self):
        """
        Clear the character data property widgets
        :return: None
        """
        self.character_name_entry.delete(0, tk.END)
        self.legacy_name_entry.delete(0, tk.END)
        self.faction.set("Republic")
        self.gui_profile.set("Select")
        for intvar in self.imp_ship_variables.values():
            intvar.set(0)
        for intvar in self.rep_ship_variables.values():
            intvar.set(0)
