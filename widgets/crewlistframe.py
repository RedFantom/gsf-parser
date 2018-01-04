# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from os import path
from collections import OrderedDict
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from .toggledframe import ToggledFrame
import variables


class CrewListFrame(ttk.Frame):
    """
    A Frame containing a ToggledFrame for each companion category, of which each in turn contains a list of Radiobuttons
    for each of the companions in that category
    """

    def __init__(self, parent, faction, data_dictionary, callback):
        """
        :param parent: parent widget
        :param faction: faction
        :param data_dictionary: companion data dictionary (companions.db) with *the correct faction*, so
                                companions_db[faction] (is a dictionary)
        :param callback: Callback for when a new crew member is selected
        """
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
        self.copilots = {}
        self.copilot_dicts = {}
        self.copilot_icons = {}
        self.copilot_buttons = {}
        self.category_variables = {}
        self.copilot_variable = tk.StringVar()
        self.faction = faction
        for category in self.data:
            # Category is a dictionary (weirdly): {crole: [{}, {}]}
            # The dictionaries in the list contain the companion data
            # No other keys are in the dictionary
            crole = ""
            for role in self.roles:
                # Attempt to match the category to a known category name
                if role not in category:
                    continue
                # ATTENTION: Category is now the [{}, {}] from before
                category = category[role]
                # crole is the role of the companions in this dict (str type)
                crole = role
                break
            # If, for some reason, there is a discrepancy in the database and the loop before did not get a valid
            # result, then skip this category, after showing a message
            if not isinstance(category, list):
                messagebox.showinfo("Info", "A non-critical error occurred. The GSF Parser had an unexpected result "
                                            "while going over the data in companions.db, please report this with the "
                                            "output below.\n\n{}".format(category))
                continue
            # The CoPilot role is a special case
            if crole == "CoPilot":
                for member_dict in category:
                    self.category_frames[crole] = ToggledFrame(self, text=crole, labelwidth=26)
                    self.copilot_dicts[member_dict["Name"]] = member_dict
                continue
            elif crole == "":
                raise ValueError("Invalid role detected.")
            self.category_frames[crole] = ToggledFrame(self, text=crole, callback=self.toggle_callback)
            self.category_variables[crole] = tk.StringVar()
            for member_dict in category:
                icon_name = member_dict["Icon"].lower().replace("Crew", "crew")
                self.member_icons[member_dict["Name"]] = \
                    photo(img.open(path.join(self.icons_path, icon_name + ".jpg")))
                self.member_buttons[member_dict["Name"]] = ttk.Radiobutton(
                    self.category_frames[crole].sub_frame, text=member_dict["Name"], compound=tk.LEFT, width=16,
                    image=self.member_icons[member_dict["Name"]], variable=self.category_variables[crole],
                    value=member_dict["Name"],
                    command=lambda i=(faction, crole, member_dict["Name"]): self.set_crew_member(i))
                if member_dict["IsDefaultCompanion"]:
                    self.copilots[crole] = member_dict["Name"]
        self.update_copilots()

    def set_crew_member(self, member):
        faction, crole, name = member
        print("Setting {} in category {}".format(name, crole))
        self.copilots[crole] = name
        self.callback(member)
        self.update_copilots()

    def update_copilots(self):
        for widget in self.copilot_buttons.values():
            widget.grid_forget()
        self.copilot_buttons.clear()
        self.copilot_icons.clear()
        index = 0
        for category, name in self.copilots.items():
            self.copilot_icons[name] = \
                photo(img.open(path.join(self.icons_path, self.copilot_dicts[name]["Icon"].lower() + ".jpg")))
            self.copilot_buttons[name] = ttk.Radiobutton(
                self.category_frames["CoPilot"].sub_frame, width=16, variable=self.copilot_variable, value=name,
                text=name, compound=tk.LEFT, image=self.member_icons[name],
                command=lambda faction=self.faction, name=name: self.set_crew_member((faction, "CoPilot", name)))
            index += 1
        self.grid_widgets()

    def grid_widgets(self):
        self.header_label.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        set_row = 1
        for frame in self.category_frames.values():
            frame.grid(row=set_row, column=0, sticky="nswe", padx=5, pady=(0, 5))
            set_row += 1
        for button in self.member_buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe", padx=5, pady=(0, 5))
            set_row += 1
        for button in self.copilot_buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe", padx=5, pady=(0, 5))
            set_row += 1
        for button in self.copilot_buttons.values():
            button.grid(row=set_row, column=0, sticky="nswe")
            set_row += 1
        for frame in self.category_frames.values():
            if frame.show.get():
                frame.toggle()

    def toggle_callback(self, frame, open):
        """
        Callback for the ToggledFrames so only one of them is openat a time.
        """
        if open is False:
            return
        iterator = list(self.category_frames.values())
        iterator.remove(frame)
        # Close the open ToggledFrames
        for toggled_frame in iterator:
            if bool(toggled_frame.show.get()) is True:
                toggled_frame.close()
