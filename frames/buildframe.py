# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

try:
    import mttkinter.mtTkinter as tk
except ImportError:
    print "mtTkinter not found, please use 'pip install mttkinter'"
    import Tkinter as tk
from collections import OrderedDict
from os import path
import cPickle as pickle
import ttk
from shipswidgets import *
from widgets import vertical_scroll_frame
from parsing.ships import Ship, Component, ships
from parsing.abilities import all_ships
import variables


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
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "ships.db"))) as f:
            self.ships_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "categories.db"))) as f:
            self.categories_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "companions.db"))) as f:
            self.companions_data = pickle.load(f)
        self.components_lists_frame = vertical_scroll_frame(self, canvaswidth=300, canvasheight=345)
        self.ship_select_frame = ShipSelectFrame(self, self.set_ship)
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
                                   self.ships_data["Imperial_S-SC4_Bloodmark"][category], None)
        self.component_frame = ttk.Frame(self)
        self.current_component = MajorComponentWidget(self.component_frame,
                                                      self.ships_data["Imperial_S-SC4_Bloodmark"]["PrimaryWeapon"][0],
                                                      self.ship)
        self.ship_stats_image = photo(img.open(path.join(self.icons_path, "spvp_targettracker.jpg")).resize((39, 39)))
        self.ship_stats_button = ttk.Button(self, text="Show ship statistics", command=self.show_ship_stats,
                                            image=self.ship_stats_image, compound=tk.LEFT)

    def set_ship(self, faction, category, ship):
        if not bool(self.ship_select_frame.category_frames[faction][category].show.get()):
            self.ship_select_frame[faction][category].toggle()
        ship_name = ""
        if faction == "Imperial":
            for key in all_ships.iterkeys():
                if key in ship:
                    ship_name = key
                    break
        elif faction == "Republic":
            for key in all_ships.itervalues():
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
                                   self.ship.data[category], None)
        for button in self.ship_select_frame.ship_buttons.itervalues():
            button.config(state=tk.ACTIVE)
        for key in self.ship_select_frame.ship_buttons.iterkeys():
            if ship in key:
                ship = key
                break
        self.ship_select_frame.ship_buttons[ship].config(state=tk.DISABLED)
        print ship, "  Style: ", self.ship_select_frame.ship_buttons[ship]["style"]
        self.grid_widgets()

    def set_component(self, *args):
        pass

    def grid_widgets(self):
        self.ship_select_frame.grid(row=0, column=0, rowspan=2, sticky=tk.N + tk.S + tk.W + tk.E, padx=1, pady=1)
        self.ship_select_frame.grid_widgets()
        self.ship_stats_button.grid(row=0, column=1, rowspan=1, sticky=tk.N + tk.S + tk.W + tk.E, pady=1)
        self.components_lists_frame.grid(row=1, column=1, rowspan=1, sticky=tk.N + tk.S + tk.W + tk.E, pady=1)
        self.component_frame.grid(row=0, rowspan=2, column=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.current_component.grid(sticky=tk.N + tk.S + tk.W + tk.E)
        self.current_component.grid_widgets()
        self.components_lists_header_label.grid(row=0, column=0, sticky=tk.W)
        set_row = 1
        for frame in self.components_lists.itervalues():
            frame.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
            frame.grid_widgets()
            set_row += 1
        self.crew_select_frame = CrewListFrame(self.components_lists_frame.interior, self.companions_data[self.faction])
        self.crew_select_frame.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

    def show_ship_stats(self):
        pass
