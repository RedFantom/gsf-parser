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
    def __init__(self, parent, category, data_list, callback):
        ttk.Frame.__init__(self, parent)
        # if not callable(callback):
        #     raise ValueError("Callback passed is not callable")
        self.names = {
            "PrimaryWeapon": "Primary Weapon",
            "PrimaryWeapon2": "Primary Weapon",
            "SecondaryWeapon": "Secondary Weapon",
            "SecondaryWeapon2": "Secondary Weapon",
            "Engine": "Engine",
            "Systems": "Systems",
            "ShieldProjector": "Shields",
            "Magazine": "Magazine",
            "Capacitor": "Capacitor",
            "Reactor": "Reactor",
            "Armor": "Armor",
            "Sensor": "Sensors",
            "Thruster": "Thrusters"
        }
        self.category = category
        self.callback = callback
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        self.toggled_frame = ToggledFrame(self, text=self.names[category], labelwidth=26)
        self.frame = self.toggled_frame.sub_frame
        self.icons = {}
        self.buttons = {}
        self.hover_infos = {}
        self.variable = tk.IntVar()
        self.variable.set(-1)
        if type(data_list) != list:
            raise ValueError("data_list should be a list, but it is {0}".format(type(data_list)))
        for component in data_list:
            component_dictionary = None
            if isinstance(component, tuple):
                for item in component:
                    if isinstance(item, dict):
                        component_dictionary = item
                        break
                if not component_dictionary:
                    raise ValueError("component_dictionary not set: {0}".format(category))
            else:
                component_dictionary = component
            try:
                name = component_dictionary["Name"]
                icon = component_dictionary["Icon"]
                self.icons[name] = photo(img.open(path.join(self.icons_path, icon + ".jpg")))
            except IOError:
                self.icons[component_dictionary["Name"]] = photo(img.open(path.join(self.icons_path, "imperial_l.png")))
            name = ""
            for word in component_dictionary["Name"].split(" "):
                if len(name + " " + word) > 20:
                    name += "\n " + word
                else:
                    name += " " + word
            self.buttons[component_dictionary["Name"]] = ttk.Radiobutton(self.frame,
                                                                         image=self.icons[component_dictionary["Name"]],
                                                                         text=name,
                                                                         command=lambda
                                                                             name=component_dictionary["Name"]:
                                                                         self.set_component(name),
                                                                         compound=tk.LEFT, width=16,
                                                                         variable=self.variable,
                                                                         value=data_list.index(
                                                                             component_dictionary))
            self.hover_infos[component_dictionary["Name"]] = HoverInfo(self.buttons[component_dictionary["Name"]],
                                                                       text=str(component_dictionary["Name"]) + "\n\n" +
                                                                            str(component_dictionary["Description"]))
        self.data = data_list

    def set_component(self, component):
        self.callback(self.category, component)

    def grid_widgets(self):
        self.toggled_frame.grid(row=0, column=0, sticky="nswe")
        set_row = 0
        for button in self.buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe")
            set_row += 1
