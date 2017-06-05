# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from widgets import *
from parsing.ships import Ship, Component
from parsing.abilities import all_ships
import pickle as pickle
from os import path
from collections import OrderedDict
import tkinter as tk
import tkinter.ttk as ttk
from tools.utilities import get_assets_directory


class BuildsFrame(ttk.Frame):
    """
    This file is to use the ships.db file found in the folder ships. This file contains a pickle of a dictionary that
    is explained in the README file. This also includes the not-enabled Infiltrator class ships.
    """

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.working = [
            "PrimaryWeapon", "PrimaryWeapon2", "SecondaryWeapon", "SecondaryWeapon2", "Engine", "Systems",
            "Shield", "Magazine", "Capacitor", "Reactor", "Armor", "Sensor"]
        self.categories = {
            "Bomber": 0,
            "Gunship": 1,
            "Infiltrator": 2,
            "Scout": 3,
            "Strike Fighter": 4
        }
        self.major_components = ["PrimaryWeapon", "PrimaryWeapon2", "SecondaryWeapon", "SecondaryWeapon2", "Systems"]
        self.middle_components = ["Engine", "Shield"]
        self.minor_components = ["Magazine", "Capacitor", "Reactor", "Armor", "Sensor"]
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "ships.db")),
                  "rb") as f:
            self.ships_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "categories.db")),
                  "rb") as f:
            self.categories_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "companions.db")),
                  "rb") as f:
            self.companions_data = pickle.load(f)
        self.components_lists_frame = VerticalScrollFrame(self, canvaswidth=300, canvasheight=315)
        self.ship_select_frame = ShipSelectFrame(self, self.set_ship, self.set_faction)
        self.components_lists = OrderedDict()
        self.faction = "Imperial"
        self.category = "Scout"
        self.ship = Ship("Bloodmark")
        self.components_lists_header_label = ttk.Label(self.components_lists_frame.interior, text="Components",
                                                       justify=tk.LEFT, font=("Calibiri", 12))
        for category in self.working:
            if category not in self.ships_data["Imperial_S-SC4_Bloodmark"]:
                continue
            self.components_lists[category] = \
                ComponentListFrame(self.components_lists_frame.interior, category,
                                   self.ships_data["Imperial_S-SC4_Bloodmark"][category], self.set_component)
        self.component_frame = ttk.Frame(self)
        self.current_component = MajorComponentWidget(self.component_frame,
                                                      self.ships_data["Imperial_S-SC4_Bloodmark"]["PrimaryWeapon"][0],
                                                      self.ship)
        self.crew_select_frame = CrewListFrame(self.components_lists_frame.interior, self.companions_data[self.faction])
        self.ship_stats_image = photo(Image.open(
            os.path.join(get_assets_directory(), "icons", "spvp_targettracker.jpg")).resize((49, 49), Image.ANTIALIAS))
        self.ship_stats_button = ttk.Button(self, text="Show ship statistics", command=self.show_ship_stats,
                                            image=self.ship_stats_image, compound=tk.LEFT)

    def set_ship(self, faction, category, ship):
        if not bool(self.ship_select_frame.category_frames[faction][category].show.get()):
            self.ship_select_frame[faction][category].toggle()
        ship_name = ""
        if faction == "Imperial":
            for key in all_ships.keys():
                if key in ship:
                    ship_name = key
                    break
        elif faction == "Republic":
            for key in all_ships.values():
                if key in ship:
                    ship_name = key
                    break
        else:
            raise ValueError("No valid faction given as argument.")
        if ship_name == "":
            raise ValueError("No valid ship specified.")
        self.ship = Ship(ship_name)
        for widget in self.components_lists_frame.interior.winfo_children():
            widget.grid_forget()
        for category in self.working:
            if category not in self.ship.data:
                continue
            self.components_lists[category] = \
                ComponentListFrame(self.components_lists_frame.interior, category,
                                   self.ship.data[category], self.set_component)
        for button in self.ship_select_frame.ship_buttons.values():
            button.config(state=tk.ACTIVE)
        for key in self.ship_select_frame.ship_buttons.keys():
            if ship in key:
                ship = key
                break
        self.ship_select_frame.ship_buttons[ship].config(state=tk.DISABLED)
        print(ship, "  Style: ", self.ship_select_frame.ship_buttons[ship]["style"])
        self.grid_widgets()

    def set_component(self, category, component):
        self.current_component.grid_forget()
        print("[DEBUG] set_component(%s, %s)" % (category, component))
        index = -1
        for index, dictionary in enumerate(self.ships_data[self.ship.ship_name][category]):
            if component == dictionary["Name"]:
                break
        if index == -1:
            raise ValueError("No components found in self.ships_data[%s][%s]" % (self.ship.ship_name, category))
        if category in self.minor_components:
            self.current_component = MinorComponentWidget(self.component_frame,
                                                          self.ships_data[self.ship.ship_name][category][index],
                                                          self.ship)
        elif category in self.middle_components:
            self.current_component = MiddleComponentWidget(self.component_frame,
                                                           self.ships_data[self.ship.ship_name][category][index],
                                                           self.ship)
        elif category in self.major_components:
            self.current_component = MajorComponentWidget(self.component_frame,
                                                          self.ships_data[self.ship.ship_name][category][index],
                                                          self.ship)
        else:
            raise ValueError("Component category not found: %s" % category)
        self.ship[category] = Component(self.ships_data[self.ship.ship_name][category][index]["Stats"])
        self.current_component.grid_widgets()
        print("[DEBUG] Gridding DEBUG component")
        self.current_component.grid(sticky=tk.N + tk.S + tk.W + tk.E)

    def grid_widgets(self):
        self.ship_select_frame.grid(row=0, column=0, rowspan=20, sticky=tk.N + tk.S + tk.W + tk.E, padx=1, pady=1)
        self.ship_select_frame.grid_widgets()
        self.ship_stats_button.grid(row=0, column=1, rowspan=1, sticky=tk.N + tk.W + tk.E, pady=(6, 5))
        self.components_lists_frame.grid(row=1, column=1, rowspan=1, sticky=tk.N + tk.S + tk.W + tk.E, pady=1)
        self.component_frame.grid(row=0, rowspan=2, column=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.current_component.grid(sticky=tk.N + tk.S + tk.W + tk.E)
        self.current_component.grid_widgets()
        self.components_lists_header_label.grid(row=0, column=0, sticky=tk.W)
        set_row = 1
        for frame in self.components_lists.values():
            frame.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
            frame.grid_widgets()
            set_row += 1
        self.crew_select_frame.destroy()
        self.crew_select_frame = CrewListFrame(self.components_lists_frame.interior, self.companions_data[self.faction])
        self.crew_select_frame.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

    def show_ship_stats(self):
        pass

    def set_faction(self, faction):
        self.faction = faction
        self.grid_widgets()

    def set_character(self, character):
        pass
