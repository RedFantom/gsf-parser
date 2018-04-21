"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
import sys
import pickle as pickle
from collections import OrderedDict
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb
# Project Modules
from data import ships as ships_data
from utils import directories
from utils import utilities
from widgets import VerticalScrollFrame
from parsing.guiparsing import get_gui_profiles, get_player_guiname
from parsing.ships import Ship
from parsing.characters import CharacterDatabase
from toplevels.addcharacter import AddCharacter
from network.sharing.data import servers
from variables import settings


class CharactersFrame(ttk.Frame):
    """
    A frame in which the user can enter his characters in a simple,
    organized manner. Characters have the following attributes that can
    be entered:
    - Character name
    - Legacy name (Sharing identifying name)
    - Faction
    - Ships line-up
    - GUI Profile name
    """

    def __init__(self, parent, main_window):
        """
        Initializes the class instance and sets up all instance variables
        :param parent: tkinter parent
        :param main_window: GSF Parser MainWindow
            This parameter is used to access the BuildsFrame. The
            BuildsFrame depends on character information from the
            CharacterDatabase and UI updates are provided from this
            Frame if the user changes something
        """
        ttk.Frame.__init__(self, parent)
        self.window = main_window
        self.directory = directories.get_temp_directory()
        # Lists of servers and abbreviations
        self.servers = servers
        # Create a dictionary that is the reverse of self.servers
        self.reverse_servers = {value: key for key, value in self.servers.items()}
        self.characters = {}
        self.load_character_database()
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
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=self.window.width-100-250, canvasheight=350)
        self.options_frame = self.scroll_frame.interior
        self.new_character_button = ttk.Button(self, text="Add character", command=self.new_character)

        self.save_button = ttk.Button(self, text="Save", command=self.save_character_data)
        self.discard_button = ttk.Button(self, text="Discard", command=self.discard_character_data)
        self.delete_button = ttk.Button(self, text="Delete", command=self.delete_character)

        self.republic_logo = utilities.open_icon("republic_s", ext=".png")
        self.imperial_logo = utilities.open_icon("imperial_s", ext=".png")

        width = 35 if sys.platform != "linux" else 27
        """
        Character Option Widgets
        """
        self.character_name_label = ttk.Label(self.options_frame, text="Character name")
        self.character_name_entry = ttk.Entry(self.options_frame, width=width, state="readonly")
        self.legacy_name_label = ttk.Label(self.options_frame, text="Legacy name")
        self.legacy_name_entry = ttk.Entry(self.options_frame, width=width, state="readonly")

        self.discord_sharing = tk.BooleanVar()
        self.discord_sharing_label = ttk.Label(self.options_frame, text="Discord Sharing")
        self.discord_sharing_checkbox = ttk.Checkbutton(
            self.options_frame, text="Enable Discord Sharing for this character", variable=self.discord_sharing,
            command=self.save_character_data)

        self.faction = tk.StringVar()
        self.faction.set("Imperial")
        self.faction_label = ttk.Label(self.options_frame, text="Faction")
        self.faction_republic_radiobutton = ttk.Radiobutton(
            self.options_frame, text="Republic", image=self.republic_logo, compound=tk.LEFT,
            variable=self.faction, value="Republic", command=lambda: self.set_character_faction("Republic"))
        self.faction_imperial_radiobutton = ttk.Radiobutton(
            self.options_frame, text="Empire", image=self.imperial_logo, compound=tk.LEFT,
            variable=self.faction, value="Imperial", command=lambda: self.set_character_faction("Imperial"))

        self.gui_profile = tk.StringVar()
        self.gui_profile_label = ttk.Label(self.options_frame, text="GUI Profile")
        self.gui_profile_dropdown = ttk.OptionMenu(
            self.options_frame, self.gui_profile, *tuple(("Select", "Default") + tuple(get_gui_profiles())))
        self.gui_profile_detect_button = ttk.Button(self.options_frame, text="Auto detect", command=self.detect_profile)

        self.lineup_label = ttk.Label(self.options_frame, text="Ships line-up")
        self.lineup_frame = ttk.Frame(self.options_frame)

        self.imp_ship_widgets = OrderedDict()
        self.imp_ship_variables = OrderedDict()
        self.rep_ship_widgets = OrderedDict()
        self.rep_ship_variables = OrderedDict()

        for ship_name in ships_data.sorted_ships.keys():
            self.imp_ship_variables[ship_name] = tk.IntVar()
            self.imp_ship_widgets[ship_name] = ttk.Checkbutton(
                self.lineup_frame, text=ship_name, variable=self.imp_ship_variables[ship_name],
                command=self.update_ships)
        for ship_name in ships_data.sorted_ships.values():
            self.rep_ship_variables[ship_name] = tk.IntVar()
            self.rep_ship_widgets[ship_name] = ttk.Checkbutton(
                self.lineup_frame, text=ship_name, variable=self.rep_ship_variables[ship_name],
                command=self.update_ships)

        self.characters_list.bind("<Double-1>", self.set_character)
        self.character_data = None

        self.update_tree()

    def update_ships(self):
        """Update the ships in the character_data and save the database"""
        if not self.character_data:
            mb.showinfo("Demand", "Select a character before performing this operation.")
            return
        if self.character_data["Faction"] == "Imperial":
            ships = tuple(ship for ship, intvar in self.imp_ship_variables.items() if intvar.get() == 1)
        elif self.character_data["Faction"] == "Republic":
            ships = tuple(ship for ship, intvar in self.rep_ship_variables.items() if intvar.get() == 1)
        else:
            raise ValueError("Unknown value for faction found: {0}".format(self.character_data["Faction"]))
        self.character_data["Ships"] = ships
        self.save_button.invoke()

    def grid_widgets(self):
        """Add all the widgets to the UIt"""
        self.widgets_grid_forget()
        self.characters_list.grid(column=0, row=0, sticky="nswe", padx=5, pady=5)
        self.characters_scroll.grid(column=1, row=0, sticky="ns", pady=5)
        self.new_character_button.grid(column=0, row=1, sticky="nswe", pady=5, padx=5)
        self.scroll_frame.grid(column=2, row=0, rowspan=2, columnspan=4, sticky="nswe", padx=5)

        self.character_name_label.grid(column=0, row=0, sticky="nsw", padx=5, pady=5)
        self.character_name_entry.grid(column=0, row=1, sticky="nswe", padx=5, pady=5)
        self.legacy_name_label.grid(column=1, row=0, sticky="nsw", padx=5, pady=5)
        self.legacy_name_entry.grid(column=1, row=1, sticky="nswe", padx=5, pady=5)

        self.discord_sharing_label.grid(column=0, row=2, sticky="nswe", padx=5, pady=5)
        self.discord_sharing_checkbox.grid(column=0, row=3, sticky="nswe", padx=5, pady=5, columnspan=2)

        self.faction_label.grid(column=0, row=4, sticky="nsw", padx=5, pady=5)
        self.faction_republic_radiobutton.grid(column=0, row=5, sticky="nsw", padx=5, pady=5)
        self.faction_imperial_radiobutton.grid(column=1, row=5, sticky="nsw", padx=5, pady=5)
        self.gui_profile_label.grid(column=0, row=6, sticky="nsw", padx=5, pady=5)
        self.gui_profile_dropdown.grid(column=0, row=7, sticky="nswe", padx=5, pady=5)
        self.gui_profile_detect_button.grid(column=1, row=7, sticky="nswe", padx=5, pady=5)
        self.lineup_label.grid(column=0, row=8, sticky="nsw", padx=5, pady=5)
        self.lineup_frame.grid(column=0, row=9, rowspan=1, columnspan=3, sticky="nswe", padx=5, pady=5)

        self.delete_button.grid(column=2, row=1, sticky="nswe", pady=5, padx=5)
        self.discard_button.grid(column=3, row=1, sticky="nswe", pady=5, padx=5)
        self.save_button.grid(column=4, row=1, sticky="nswe", pady=5, padx=5)

        set_row = 0
        set_column = 0
        iterator = self.imp_ship_widgets if self.faction.get() == "Imperial" else self.rep_ship_widgets
        for item in iterator.values():
            item.grid(row=set_row, column=set_column, padx=5, pady=5, sticky="w")
            set_row += 1
            if set_row == 5:
                set_column += 1
                set_row = 0

    def update_tree(self):
        """
        Update the Treeview self.characters_list with all the characters
        found in the character database

        Updates with format "character name (server)"
        """
        if not isinstance(self.characters, CharacterDatabase):
            raise TypeError("Invalid character database type")

        self.characters_list.delete(*self.characters_list.get_children())

        for character, data in sorted(self.characters.items()):
            if data["Server"] not in self.servers or character[0] not in self.servers:
                mb.showinfo(
                    "United Forces Notification",
                    "Since the United Forces update of SWTOR, the network names have changed and thus the character "
                    "database must be updated. This process is non-destructive, meaning you should be able to keep "
                    "all your characters, as long as the names do not conflict."
                )
                self.characters.update_servers(CharacterDatabase.UNITED_FORCES)
                self.save_character_data()
            try:
                self.characters_list.insert(
                    "", tk.END, iid="{};{}".format(data["Server"], data["Name"]),
                    text="{} ({})".format(data["Name"], self.servers[data["Server"]])
                )
            except TypeError:
                self.new_database()
                self.update_tree()

    def widgets_grid_forget(self):
        """
        Remove *just* the ship Checkbuttons (faction-specific) from the
        grid geometry manager. Other widgets are not affected.
        """
        for item in self.imp_ship_widgets.values():
            item.grid_forget()
        for item in self.rep_ship_widgets.values():
            item.grid_forget()

    def new_database(self):
        """
        Create a new character database, overwriting the current one

        Provides a notification to notify the user that all character
        data is lost. This function is only appropriate when first using
        the GSF Parser or if through some error the database has become
        corrupted (like unexpected shutdown without emptying writing
        buffers).
        """
        mb.showinfo("Notification", "The GSF Parser is creating a new characters database, discarding all your "
                                    "character data, if you had any, and ship builds. If you did not expect this, "
                                    "please file an issue report in the GitHub repository.")
        characters = CharacterDatabase()
        with open(os.path.join(self.directory, "characters.db"), "wb") as f:
            pickle.dump(characters, f)
        self.characters = characters

    def detect_profile(self):
        """
        Callback for the Auto-detect button, sets the GUI profile
        according to the result of get_player_guiname or display a
        message that the profile cannot be determined reliably
        (because of the same character name on different servers)
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
        Callback for the self.new_character_button Button widget.

        Opens an AddCharacter Toplevel window that provides widgets for
        inserting a new character into the database.

        Passes self.insert_character as callback argument to
        AddCharacter. This insert_character callback actually creates
        the new character in the database.
        """
        AddCharacter(self.window, tuple(self.servers.values()), self.insert_character)

    def insert_character(self, name: str, legacy: str, server: str, faction: str):
        """
        Create a new character in the CharacterDatabase with the given
        specifications. Uses start ships as default line-up for the
        new character.

        Performs UI updates.
        """
        if faction == "Imperial":
            ships = ("Blackbolt", "Rycer")
        else:  # faction == "Republic":
            ships = ("Novadive", "Star Guard")
        ships_dict = {name: Ship(name) for name in ships_data.sorted_ships.values()}
        server = self.reverse_servers[server]
        self.characters[(server, name)] = {
            "Server": server,
            "Faction": faction,
            "Name": name,
            "Legacy": legacy,
            "Ships": ships,
            "Ship Objects": ships_dict,
            "GUI": "Default",
            "Discord": True
        }
        self.character_data = self.characters[(server, name)]
        self.clear_character_data()
        self.set_character(set=False)
        self.save_button.invoke()
        self.window.realtime_frame.update_characters()
        self.update_tree()
        self.window.builds_frame.ship_select_frame.update_characters()
        self.window.realtime_frame.update_characters()

    def set_character_faction(self, faction: str):
        """
        Callback for the faction Radiobuttons.

        Changes faction of a given character. Updates UI and
        CharacterDatabase. Translates ship names in line-up to the
        other faction before saving.
        """
        if not self.character_data:
            mb.showinfo("Demand", "Select a character before performing this operation.")
            return
        self.grid_widgets()
        if not mb.askyesno("Warning", "Changing the faction of a character removes "
                                      "all specified builds for this character. "
                                      "Are you sure you want to change the faction?"):
            return
        if faction == "Imperial":
            ships = ("Blackbolt", "Rycer")
            ships_dict = {name: None for name in ships_data.sorted_ships.keys()}
        elif faction == "Republic":
            ships = ("Novadive", "Star Guard")
            ships_dict = {name: None for name in ships_data.sorted_ships.values()}
        else:
            raise ValueError("Unknown value for faction found: {0}".format(faction))
        self.character_data["Faction"] = faction
        self.character_data["Ship Objects"] = ships_dict
        self.character_data["Ships"] = ships
        self.save_character_data()
        self.update_tree()

    def save_character_data(self):
        """Save CharacterDatabase to a file in the temporary dir"""
        print("[CharactersFrame] Saving character database")
        if self.character_data is not None:
            self.character_data["GUI"] = self.gui_profile.get()
            server = self.character_data["Server"]
            name = self.character_data["Name"]
            self.character_data["Discord"] = self.discord_sharing.get()
            self.characters[(server, name)] = self.character_data
        with open(os.path.join(self.directory, "characters.db"), "wb") as f:
            pickle.dump(self.characters, f)

    def load_character_database(self):
        """
        Loads the character database file in temporary dir

        Detects older versions of the character database (then not yet
        CharacterDatabase) used in older versions of the GSF Parser and
        informs the user if the current database is deprecated.
        """
        if "characters.db" not in os.listdir(self.directory):
            self.new_database()
        try:
            with open(os.path.join(self.directory, "characters.db"), "rb") as f:
                self.characters = pickle.load(f)
        except OSError:
            mb.showerror("Error", "The Character Database location is not accessible.")
            self.new_database()
        except EOFError:
            mb.showerror("Error", "The Character Database has been corrupted.")
            self.new_database()
        if not isinstance(self.characters, CharacterDatabase) or\
                self.characters.version != settings["misc"]["patch_level"]:
            mb.showinfo("GSF Update", "Galactic StarFighter has received an update! Because of this, the internal GSF "
                                      "Parser database has been updated, and your character database must be updated "
                                      "as well to match the data. Currently, this process is destructive, and "
                                      "all your character data, including builds, will be deleted.\n\nThe screen "
                                      "parsing results are not affected.")
            self.new_database()
        self.characters.update_database()

    def discard_character_data(self):
        """
        Discard any changes to the character data that have not yet
        been saved. Most changes also trigger CharacterDatabase saves.
        # TODO: Deprecate this feature and UI elements
        """
        self.clear_character_data()
        self.set_character()

    def delete_character(self):
        """
        Callback for self.delete_button Button widget.

        Deletes the character selected in the Treeview from the
        CharacterDatabase and saves the database. Deleting a character
        from the Database is final.
        """
        self.set_character()
        del self.characters[(self.character_data["Server"], self.character_data["Name"])]
        self.clear_character_data()
        self.save_button.invoke()
        self.update_tree()

    def get_character_data(self, character: tuple=None):
        """
        Return data for a given character. If the parameter character is
        given, it should consist of a tuple (server_code, name). If it
        is not given, data for the currently in the Treeview selected
        character is returned. If there is no character in the Treeview
        selected, None is returned.
        """
        if character is None:
            character = self.characters_list.selection()
            if character == ():
                return
            character = tuple(character[0].split(";"))
        self.clear_character_data()
        if character not in self.characters:
            mb.showerror("Error", "The character {0} was not found in the internal character database. Please report "
                                  "this error with debug output in the GitHub repository.".format(character))
            raise ValueError("Character not found {0} in {1}".format(character, self.characters))
        return self.characters[character]

    def set_character(self, set=True, *args):
        """
        Callback for Treeview DoubleClick

        Updates the UI elements to represent the data for the selected
        character.
        """
        if not set:
            character_data = self.character_data
        else:
            character_data = self.get_character_data()
            if not character_data:
                return
        if character_data is None:
            return
        self.insert_into_entries(character_data["Name"], character_data["Legacy"])
        self.faction.set(character_data["Faction"])
        self.gui_profile.set(character_data["GUI"])
        iterator = self.imp_ship_variables if character_data["Faction"] == "Imperial" else self.rep_ship_variables
        for name, intvar in iterator.items():
            intvar.set(name in character_data["Ships"])
        self.discord_sharing.set(character_data["Discord"])
        self.character_data = character_data
        self.window.builds_frame.reset()

    def clear_character_data(self):
        """Clear the character data property widgets"""
        self.character_name_entry.delete(0, tk.END)
        self.legacy_name_entry.delete(0, tk.END)
        self.faction.set("Republic")
        self.gui_profile.set("Select")
        for intvar in self.imp_ship_variables.values():
            intvar.set(0)
        for intvar in self.rep_ship_variables.values():
            intvar.set(0)
        self.character_data = None

    def insert_into_entries(self, name: str, legacy: str):
        """Update character name and legacy name Entry widgets"""
        self.character_name_entry.config(state=tk.NORMAL)
        self.legacy_name_entry.config(state=tk.NORMAL)
        self.character_name_entry.delete(0, tk.END)
        self.legacy_name_entry.delete(0, tk.END)
        self.character_name_entry.insert(tk.END, name)
        self.legacy_name_entry.insert(tk.END, legacy)
        self.character_name_entry.config(state="readonly")
        self.legacy_name_entry.config(state="readonly")
