# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from os import path
from collections import OrderedDict
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from .toggledframe import ToggledFrame
import variables


class CrewListFrame(ttk.Frame):
    def __init__(self, parent, data_dictionary, callback):
        ttk.Frame.__init__(self, parent)
        self.callback = callback
        self.window = variables.main_window
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        self.data = data_dictionary
        self.roles = ["CoPilot", "Engineering", "Defensive", "Offensive", "Tactical"]
        self.header_label = ttk.Label(self, text="Crew", font=("Calibiri", 12), justify=tk.LEFT)
        self.category_frames = OrderedDict()
        self.member_buttons = OrderedDict()
        self.member_icons = OrderedDict()
        self.copilots = []
        self.copilot_dicts = {}
        self.copilot_icons = {}
        self.copilot_buttons = {}
        self.category_variables = {}
        self.copilot_variable = tk.IntVar()
        for category in self.data:
            crole = ""
            for role in self.roles:
                try:
                    category = category[role]
                    crole = role
                    break
                except KeyError:
                    continue
            if crole == "CoPilot":
                for member_dict in category:
                    self.category_frames[crole] = ToggledFrame(self, text=crole, labelwidth=29)
                    self.copilot_dicts[member_dict["Name"]] = member_dict
                continue
            elif crole == "":
                raise ValueError("Invalid role detected.")
            self.category_frames[crole] = ToggledFrame(self, text=crole)
            self.category_variables[crole] = tk.IntVar()
            print("crole is ", crole)
            for member_dict in category:
                self.member_icons[member_dict["Name"]] = photo(img.open(path.join(self.icons_path,
                                                                                  member_dict["Icon"] + ".jpg")))
                self.member_buttons[member_dict["Name"]] = ttk.Radiobutton(self.category_frames[crole].sub_frame,
                                                                           text=member_dict["Name"], compound=tk.LEFT,
                                                                           image=self.member_icons[member_dict["Name"]],
                                                                           command=lambda i=member_dict:
                                                                           self.set_crew_members(member_dict),
                                                                           width=19,
                                                                           variable=self.category_variables[crole],
                                                                           value=category.index(member_dict))
                if member_dict["IsDefaultCompanion"]:
                    self.copilots.append(member_dict["Name"])
        self.update_copilots()

    def set_crew_members(self, member_dict):
        self.callback(member_dict)
        for name, variable in self.category_variables.items():
            self.window.builds_frame.ship[name] = variable.get()

    def update_copilots(self):
        self.copilot_buttons.clear()
        self.copilot_icons.clear()
        for name in self.copilots:
            self.member_icons[name] = photo(img.open(path.join(self.icons_path,
                                                               self.copilot_dicts[name]["Icon"] + ".jpg")))
            self.member_buttons[name] = ttk.Radiobutton(self.category_frames["CoPilot"].sub_frame,
                                                        text=name, compound=tk.LEFT,
                                                        image=self.member_icons[name],
                                                        command=self.set_crew_members,
                                                        width=21,
                                                        variable=self.copilot_variable, value=self.copilots.index(name))
        self.grid_widgets()

    def grid_widgets(self):
        self.header_label.grid(row=0, column=0, sticky="nswe")
        set_row = 1
        for frame in self.category_frames.values():
            frame.grid(row=set_row, column=0, sticky="nswe")
            set_row += 1
        for button in self.member_buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe")
            set_row += 1
