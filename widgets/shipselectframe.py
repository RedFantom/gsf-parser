# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from os import path
import pickle as pickle
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from widgets import ToggledFrame, VerticalScrollFrame


class ShipSelectFrame(ttk.Frame):
    def __init__(self, parent, callback, faction_callback):
        ttk.Frame.__init__(self, parent)
        self.faction = "Imperial"
        self.ship = "Bloodmark",
        self.component = "Light Laser Cannon"
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=240, canvasheight=345, width=240, height=345)
        self.frame = self.scroll_frame.interior
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "categories.db")),
                  "rb") as db:
            self.data = pickle.load(db)
        self.callback = callback
        self.faction_callback = faction_callback
        self.faction_frames = {}
        self.faction_buttons = {}
        self.ship_frames = {}
        self.ship_photos = {}
        self.ship_buttons = {}
        self.category_frames = {faction: {} for faction in self.data}
        self.faction_photos = {}
        toggled = False
        for faction in self.data:
            self.faction_frames[faction] = ttk.Frame(self.frame)
            self.faction_photos[faction] = photo(img.open(path.join(self.icons_path, faction.lower() + ".png")).
                                                 resize((25, 25), img.ANTIALIAS))
            self.faction_buttons[faction] = ttk.Button(self, text=faction, width=8,
                                                       command=lambda faction=faction: self.set_faction(faction),
                                                       image=self.faction_photos[faction], compound=tk.LEFT)
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

    def grid_widgets(self):
        self.scroll_frame.grid(row=1, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E, pady=2)
        set_row = 0
        set_column = 0
        for button in self.faction_buttons.values():
            button.grid(row=set_row, column=set_column, sticky=tk.N + tk.W + tk.E, padx=1)
            set_column += 1
        set_row = 20
        for faction in self.category_frames:
            if faction == self.faction:
                for frame in self.category_frames[faction].values():
                    frame.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E, columnspan=2)
                    set_row += 1
            else:
                for frame in self.category_frames[faction].values():
                    frame.grid_forget()
        set_row = 40
        for button in self.ship_buttons.values():
            button.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
            set_row += 1

    def set_ship(self, faction, category, shipname):
        print("Faction: %s\nCategory: %s\nShipname: %s" % (faction, category, shipname))
        self.callback(faction, category, shipname)

    def set_faction(self, faction):
        self.faction = faction
        self.faction_callback(faction)
        self.grid_widgets()
