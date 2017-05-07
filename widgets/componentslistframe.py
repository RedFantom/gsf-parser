# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from os import path
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from widgets import HoverInfo, ToggledFrame


class ComponentListFrame(ttk.Frame):
    def __init__(self, parent, category, data_dictionary, callback):
        ttk.Frame.__init__(self, parent)
        # if not callable(callback):
        #     raise ValueError("Callback passed is not callable")
        self.names = {"PrimaryWeapon": "Primary Weapon",
                      "PrimaryWeapon2": "Primary Weapon",
                      "SecondaryWeapon": "Secondary Weapon",
                      "SecondaryWeapon2": "Secondary Weapon",
                      "Engine": "Engine",
                      "Systems": "Systems",
                      "Shield": "Shields",
                      "Magazine": "Magazine",
                      "Capacitor": "Capacitor",
                      "Reactor": "Reactor",
                      "Armor": "Armor",
                      "Sensor": "Sensors"
                      }
        self.category = category
        self.callback = callback
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        self.toggled_frame = ToggledFrame(self, text=self.names[category], labelwidth=28)
        self.frame = self.toggled_frame.sub_frame
        self.icons = {}
        self.buttons = {}
        self.hover_infos = {}
        for component in data_dictionary:
            try:
                self.icons[component["Name"]] = photo(img.open(path.join(self.icons_path, component["Icon"] + ".jpg")))
            except IOError:
                self.icons[component["Name"]] = photo(img.open(path.join(self.icons_path, "imperial_l.png")))
            self.buttons[component["Name"]] = ttk.Button(self.frame, image=self.icons[component["Name"]],
                                                         text=component["Name"],
                                                         command=lambda name=component["Name"]:
                                                         self.set_component(name),
                                                         compound=tk.LEFT, width=19)
            self.hover_infos[component["Name"]] = HoverInfo(self.buttons[component["Name"]],
                                                            text=str(component["Name"]) + "\n\n" +
                                                                 str(component["Description"]))
        self.data = data_dictionary

    def set_component(self, component):
        self.callback(self.category, component)

    def grid_widgets(self):
        self.toggled_frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        set_row = 0
        for button in self.buttons.values():
            button.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
            set_row += 1
