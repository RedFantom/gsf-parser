# -*- coding: utf-8 -*-

"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import messagebox as mb
import tkinter.ttk as ttk
from os import path
import pickle as pickle
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from widgets import ToggledFrame, VerticalScrollFrame
from widgets.hoverinfo import HoverInfo
import variables
from parsing import ships
from collections import OrderedDict


class ShipSelectFrame(ttk.Frame):
    def __init__(self, parent, callback, faction_callback):
        ttk.Frame.__init__(self, parent)
        self.window = variables.main_window
        self.faction = "Imperial"
        self.ship = "Bloodmark"
        self.component = "Light Laser Cannon"
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=222, canvasheight=315, width=240, height=315)
        self.frame = self.scroll_frame.interior
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "categories.db")),
                  "rb") as db:
            self.data = pickle.load(db)
        self.callback = callback
        self.faction_callback = faction_callback
        self.faction_frames = OrderedDict()
        self.faction_buttons = OrderedDict()
        self.ship_frames = OrderedDict()
        self.ship_photos = OrderedDict()
        self.ship_buttons = OrderedDict()
        self.category_frames = {faction: {} for faction in self.data}
        self.faction_photos = OrderedDict()
        self.ships = None
        self.character_tuple = (None, None)

        toggled = False

        self.server = tk.StringVar()
        self.server_dropdown = ttk.OptionMenu(self, self.server, *("Choose server",), command=self.update_characters)
        self.character = tk.StringVar()
        self.character_dropdown = ttk.OptionMenu(self, self.character, *("Choose character",),
                                                 command=self.load_character)
        # self.character_update_button = ttk.Button(self, text="Load character", command=self.load_character)

        for faction in self.data:
            self.faction_frames[faction] = ttk.Frame(self.frame)
            for category in self.data[faction]:
                if category["CategoryName"] == "Infiltrator":
                    continue  # pass
                self.category_frames[faction][category["CategoryName"]] = ToggledFrame(self.frame,
                                                                                       text=category["CategoryName"],
                                                                                       labelwidth=27)
                if category["CategoryName"] == "Scout" and not toggled:
                    self.category_frames[faction][category["CategoryName"]].toggle()
                    toggled = True
                for ship_dict in category["Ships"]:
                    try:
                        image = img.open(path.join(self.icons_path, ship_dict["Icon"] + ".jpg"))
                        image = image.resize((52, 52))
                        self.ship_photos[ship_dict["Name"]] = photo(image)
                    except IOError:
                        self.ship_photos[ship_dict["Name"]] = photo(img.open(path.join(self.icons_path,
                                                                                       faction.lower() + "_l.png")))
                    self.ship_buttons[ship_dict["Name"]] = \
                        ttk.Button(self.category_frames[faction][category["CategoryName"]].sub_frame,
                                   text=ship_dict["Name"],
                                   image=self.ship_photos[ship_dict["Name"]], compound=tk.LEFT,
                                   command=lambda faction=faction, category=category, ship_dict=ship_dict:
                                   self.set_ship(faction, category["CategoryName"], ship_dict["Name"]),
                                   width=18)
                    HoverInfo(self.ship_buttons[ship_dict["Name"]], ship_dict["Description"], headertext="Description")
        self.update_servers()

    def grid_widgets(self):
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
        if not self.ships:
            mb.showinfo("Request", "Please choose a character first.")
            return
        ship_name = ships.other_ships[ship_name]
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
        self.faction = faction
        self.faction_callback(faction)
        self.grid_widgets()

    def update_servers(self):
        self.server_dropdown["menu"].delete(0, tk.END)
        self.character_dropdown["menu"].delete(0, tk.END)
        servers = ["Choose server"]
        for data in self.window.characters_frame.characters:
            if data[0] not in self.window.characters_frame.servers:
                return
            server = self.window.characters_frame.servers[data[0]]
            if server in servers:
                continue
            servers.append(server)
        for server in servers:
            self.server_dropdown["menu"].add_command(label=server, command=lambda var=self.server, val=server:
                                                     self.set_server(var, val))

    def update_characters(self):
        self.character_dropdown["menu"].delete(0, tk.END)
        characters = ["Choose character"]
        for data in self.window.characters_frame.characters:
            server = self.window.characters_frame.servers[data[0]]
            if server != self.server.get():
                continue
            characters.append(data[1])
        for character in characters:
            self.character_dropdown["menu"].add_command(label=character,
                                                        command=lambda var=self.character, val=character:
                                                        self.set_character(var, val))
        return

    def load_character(self):
        server = self.window.characters_frame.reverse_servers[self.server.get()]
        self.character_tuple = (server, self.character.get())
        self.set_faction(self.window.characters_frame.characters[(server, self.character.get())]["Faction"])
        self.ships = self.window.characters_frame.characters[(server, self.character.get())]["Ship Objects"]
        self.window.characters_frame.character_data = self.window.characters_frame.characters[self.character_tuple]

    def set_server(self, variable, value):
        variable.set(value)
        self.update_characters()

    def set_character(self, variable, value):
        variable.set(value)
        self.load_character()
