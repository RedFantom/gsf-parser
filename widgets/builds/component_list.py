"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import textwrap
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
from ttkwidgets.frames import Balloon
# Project Modules
from widgets import ToggledFrame
from data.components import component_strings
from utils.utilities import open_icon


class ComponentListFrame(ttk.Frame):
    """
    Frame to contain a list of all components found for a certain ship in a
    given category. Contains a ToggledFrame to support wrapping the different
    Buttes for each of the components in a single, expandable Frame.
    """
    def __init__(self, parent, category, data_list, callback, toggle_callback):
        """
        :param parent: master widget
        :param category: category to create Widgets for
        :param data_list: ships_db[ship_name][category_name] list of components
        :param callback: callback to call when a component is selected
        :param toggle_callback: callback to call when ToggledFrame is toggled
        """
        ttk.Frame.__init__(self, parent)
        self.category = category
        self.callback = callback
        self.toggled_frame = ToggledFrame(
            self, text=component_strings[category], callback=toggle_callback)
        self.frame = self.toggled_frame.sub_frame
        self.icons = {}
        self.buttons = {}
        self.hover_infos = {}
        self.variable = tk.IntVar()
        self.variable.set(-1)
        for component_dictionary in data_list:
            name = component_dictionary["Name"]
            self.icons[name] = open_icon(component_dictionary["Icon"])
            name = textwrap.fill(component_dictionary["Name"], 16)
            self.buttons[component_dictionary["Name"]] = ttk.Radiobutton(
                self.frame, image=self.icons[component_dictionary["Name"]], text=name, compound=tk.LEFT, width=12,
                command=lambda name=component_dictionary["Name"]: self.set_component(name), variable=self.variable,
                value=data_list.index(component_dictionary))
            self.hover_infos[component_dictionary["Name"]] = Balloon(
                self.buttons[component_dictionary["Name"]],
                headertext="Tooltip", width=350,
                text=str(component_dictionary["Name"]) + "\n\n" + str(component_dictionary["Description"]))
        self.data = data_list

    def set_component(self, component):
        """Callback for Component Button pressed"""
        self.callback(self.category, component)

    def grid_widgets(self):
        """Put the component Buttons in place"""
        self.toggled_frame.grid(row=0, column=0, sticky="nswe")
        set_row = 0
        for button in self.buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe")
            set_row += 1
