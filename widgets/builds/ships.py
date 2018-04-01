"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import messagebox as mb
import tkinter.ttk as ttk
# Standard Library
from os import path
import pickle as pickle
from collections import OrderedDict
# Packages
from PIL.ImageTk import PhotoImage
from ttkwidgets.frames import Balloon
# Project Modules
import variables
from widgets import ToggledFrame, VerticalScrollFrame
from parsing import ships
from data.ships import ships_other
from utils.utilities import open_icon_pil
from utils.directories import get_assets_directory


class ShipSelectFrame(ttk.Frame):
    """
    Frame for four ToggledFrames, one for each ship category. Each of the
    ToggledFrames contains Buttons to select a ship. Supports setting different
    Factions, in order to allow selecting republic and imperial ship names and
    images.
    """

    def __init__(self, parent, callback, faction_callback):
        """
        :param parent: parent Widget
        :param callback: Callback called when a Ship is selected
        :param faction_callback:
        """
        ttk.Frame.__init__(self, parent)
        self.window = variables.main_window
        # Ship properties
        self.faction = "Imperial"
        self.ship = "Bloodmark"
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=222, canvasheight=315, width=240, height=315)
        self.frame = self.scroll_frame.interior
        with open(path.join(get_assets_directory(), "categories.db"), "rb") as db:
            self.data = pickle.load(db)
        self.callback = callback
        self.faction_callback = faction_callback
        self.faction_frames = OrderedDict()
        self.faction_buttons = OrderedDict()
        self.ship_frames = OrderedDict()
        self.ship_photos = dict()
        self.ship_buttons = OrderedDict()
        self.category_frames = {faction: {} for faction in self.data}
        self.faction_photos = OrderedDict()
        self.ships = None
        self.character_tuple = (None, None)
        self.server = tk.StringVar()
        self.server_dropdown = ttk.OptionMenu(self, self.server, *("Choose network",), command=self.update_characters)
        self.character = tk.StringVar()
        self.character_dropdown = ttk.OptionMenu(
            self, self.character, *("Choose character",), command=self.load_character)
        # Buttons are created for both factions at start-up
        for faction in self.data:
            self.faction_frames[faction] = ttk.Frame(self.frame)
            for category in self.data[faction]:
                self.category_frames[faction][category["CategoryName"]] = ToggledFrame(
                    self.frame, text=category["CategoryName"], labelwidth=27)
                for ship_dict in category["Ships"]:
                    self.ship_photos[ship_dict["Name"]] = PhotoImage(
                        open_icon_pil(ship_dict["Icon"]).resize((52, 52)), master=self)
                    self.ship_buttons[ship_dict["Name"]] = ttk.Button(
                        self.category_frames[faction][category["CategoryName"]].sub_frame,
                        text=ship_dict["Name"],
                        image=self.ship_photos[ship_dict["Name"]],
                        compound=tk.LEFT,
                        command=lambda faction=faction, category=category, ship_dict=ship_dict:
                        self.set_ship(faction, category["CategoryName"], ship_dict["Name"]),
                        width=18)
                    Balloon(self.ship_buttons[ship_dict["Name"]],
                            text=ship_dict["Description"],
                            headertext="Description")
        self.update_servers()

    def grid_widgets(self):
        """Put the widgets in the correct place"""
        self.server_dropdown.grid(row=0, column=0, columnspan=2, sticky="nswe", pady=(5, 0))
        self.character_dropdown.grid(row=1, column=0, columnspan=2, sticky="nswe", pady=(5, 5))
        self.scroll_frame.grid(row=3, rowspan=2, columnspan=2, sticky="nswe", pady=2)
        set_row = 20
        for faction in self.category_frames:
            if faction == self.faction:
                for category, frame in self.category_frames[faction].items():
                    frame.grid(row=set_row, column=0, sticky="nswe", columnspan=2)
                    set_row += 1
            else:
                for frame in self.category_frames[faction].values():
                    frame.grid_forget()
        set_row = 40
        for button in self.ship_buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe", padx=2, pady=2)
            set_row += 1

    def set_ship(self, faction, category, ship_name):
        """
        Callback for the Ship selection buttons.
        :param faction: Faction to set the ship for
        :param category: Ship category name
        :param ship_name: Full ship name provided by ship database
        """
        if not self.ships:
            mb.showinfo("Request", "Please choose a character first.")
            return
        ship_name = ships_other[ship_name]
        if self.window.characters_frame.characters[self.character_tuple]["Ship Objects"][ship_name]:
            ship_object = self.window.characters_frame.characters[self.character_tuple]["Ship Objects"][ship_name]
        else:
            ship_object = ships.Ship(ship_name)
        for item, frame in self.window.builds_frame.components_lists.items():
            if item not in ship_object:
                frame.toggled_frame.toggle_button.config(state=tk.DISABLED)
                continue
            frame.toggled_frame.toggle_button.config(state=tk.NORMAL)
        for frame in self.window.builds_frame.crew_select_frame.category_frames.values():
            frame.toggle_button.config(state=tk.NORMAL)
        self.callback(faction, category, ship_name, ship_object)

    def set_faction(self, faction):
        """Change the faction of the ships to param faction"""
        self.faction = faction
        self.faction_callback(faction)
        self.grid_widgets()

    def update_servers(self):
        """
        Update the server list in the OptionMenu based on the server there are
        characters for in the CharacterDatabase.
        """
        self.server_dropdown["menu"].delete(0, tk.END)
        self.character_dropdown["menu"].delete(0, tk.END)
        servers = ["Choose network"]
        for data in self.window.characters_frame.characters:
            if data[0] not in self.window.characters_frame.servers:
                return
            server = self.window.characters_frame.servers[data[0]]
            if server in servers:
                continue
            servers.append(server)
        for server in servers:
            self.server_dropdown["menu"].add_command(
                label=server, command=lambda var=self.server, val=server: self.set_server(var, val))
        return

    def update_characters(self):
        """
        Update the list of characters in the OptionMenu based on the characters
        found in the CharacterDatabase.
        """
        self.character_dropdown["menu"].delete(0, tk.END)
        characters = ["Choose character"]
        for data in self.window.characters_frame.characters:
            server = self.window.characters_frame.servers[data[0]]
            if server != self.server.get():
                continue
            characters.append(data[1])
        for character in characters:
            self.character_dropdown["menu"].add_command(
                label=character, command=lambda var=self.character, val=character: self.set_character(var, val))
        return

    def load_character(self):
        """
        Callback called upon selecting a character in the OptionMenu. Loads
        the character data from the CharacterDatabase and the ship objects, so
        the other Widgets of the BuildFrame can manipulate the data.
        """
        server = self.window.characters_frame.reverse_servers[self.server.get()]
        self.character_tuple = (server, self.character.get())
        self.set_faction(self.window.characters_frame.characters[(server, self.character.get())]["Faction"])
        self.ships = self.window.characters_frame.characters[(server, self.character.get())]["Ship Objects"]
        self.window.characters_frame.character_data = self.window.characters_frame.characters[self.character_tuple]

    def set_server(self, variable, value):
        """Callback callced upon selecting a server in the OptionMenu"""
        variable.set(value)
        self.update_characters()

    def set_character(self, variable, value):
        """Callback called upon selecting a character in the OptionMenu"""
        variable.set(value)
        self.load_character()
