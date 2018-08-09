"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from collections import OrderedDict
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
# Project Modules
import variables
from widgets.toggledframe import ToggledFrame
from utils.utilities import open_icon


class CrewListFrame(ttk.Frame):
    """
    A Frame containing a ToggledFrame for each companion category, of
    which each in turn contains a list of Radiobuttons for each of the
    companions in that category
    """

    def __init__(self, parent: tk.Widget, faction: str, data_dictionary: dict, callback: callable):
        """
        :param parent: parent widget
        :param faction: faction
        :param data_dictionary: companion data dictionary
            (companions.db) with *the correct faction*, so
            companions_db[faction] (is a dictionary)
        :param callback: Callback for when a new crew member is selected
        """
        ttk.Frame.__init__(self, parent)
        self.callback = callback
        self.window = variables.main_window
        self.data = data_dictionary
        self.faction_data = data_dictionary[faction]
        self.roles = ["CoPilot", "Engineering", "Defensive", "Offensive", "Tactical"]
        self.header_label = ttk.Label(self, text="Crew", font=("default", 12), justify=tk.LEFT)

        # Attributes
        self.category_frames = OrderedDict()
        self.member_buttons, self.member_icons = OrderedDict(), OrderedDict()
        self.copilots, self.copilot_dicts = dict(), dict()
        self.copilot_icons, self.copilot_buttons = dict(), dict()
        self.category_variables = dict()
        self.copilot_variable = tk.StringVar()
        self.faction = faction

        self.build_widgets()

    def set_faction(self, faction):
        """Update the faction of the widgets in this list"""
        self.faction = faction
        for member, button in self.member_buttons.items():
            button.grid_forget()
            button.destroy()
        for widget in self.copilot_buttons.values():
            widget.grid_forget()
            widget.destroy()
        for frame in self.category_frames.values():
            frame.grid_forget()
            frame.destroy()
        self.category_frames.clear()
        self.member_buttons.clear()
        self.copilot_buttons.clear()
        self.faction_data: dict = self.data[faction]
        self.build_widgets()
        self.grid_widgets()

    def build_widgets(self):
        """Build widgets for the Crew Members"""
        for category in self.faction_data:  # {crew_role: [dict, dict, ...]}
            crew_role, = category.keys()  # CoPilot, Engineering, etc...
            category,  = category.values()  # [dict, dict, ...]
            # The CoPilot is selected from selected crew members
            if crew_role == "CoPilot":
                for member in category:
                    self.category_frames[crew_role] = ToggledFrame(self, text=crew_role)
                    self.copilot_dicts[member["Name"]] = member
                continue
            # Build Crew widgets for this category: Frame, Radiobuttons
            self.category_frames[crew_role] = ToggledFrame(self, text=crew_role, callback=self.toggle_callback)
            # Stores name of selected crew member in this crew role
            self.category_variables[crew_role] = tk.StringVar()
            # Build Radiobutton widget for each Crew member option
            for member in category:  # {Name, Icon, etc...}
                self.member_icons[member["Name"]] = open_icon(member["Icon"].lower())
                self.member_buttons[member["Name"]] = ttk.Radiobutton(
                    self.category_frames[crew_role].sub_frame, text=member["Name"], compound=tk.LEFT, width=10,
                    image=self.member_icons[member["Name"]], variable=self.category_variables[crew_role],
                    value=member["Name"],
                    command=lambda i=(self.faction, crew_role, member["Name"]): self.set_crew_member(i))
                if member["IsDefaultCompanion"]:
                    self.copilots[crew_role] = member["Name"]
        self.update_copilots()

    def set_crew_member(self, member: tuple):
        """
        Callback for Radiobuttons for the crew members.
        member: (faction: str, crew_role: str, crew_name: str)
        """
        faction, role, name = member
        print("[CrewListFrame] Setting {} in category {}".format(name, role))
        self.copilots[role] = name
        self.callback(member)
        self.update_copilots()

    def update_copilots(self):
        """
        Update the CoPilot widgets in the CoPilot ToggledFrame. The
        CoPilot is selected from the crew members selected in the other
        crew member roles and thus in the CoPilot Frame only the crew
        members selected in the other roles should be displayed here.
        """
        # Clear the currently existing widgets
        for widget in self.copilot_buttons.values():
            widget.grid_forget()
        self.copilot_buttons.clear()
        self.copilot_icons.clear()
        for index, (category, name) in enumerate(self.copilots.items()):
            self.copilot_icons[name] = open_icon(self.copilot_dicts[name]["Icon"].lower())
            self.copilot_buttons[name] = ttk.Radiobutton(
                self.category_frames["CoPilot"].sub_frame, width=10, variable=self.copilot_variable,
                value=name, text=name, compound=tk.LEFT, image=self.member_icons[name],
                command=lambda name=name: self.set_crew_member((self.faction, "CoPilot", name)))
        self.grid_widgets()

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
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

    def toggle_callback(self, frame: ttk.Frame, open: bool):
        """
        Callback for the ToggledFrames so only one of them is open at a
        time. This is to prevent the clogging up of the relatively small
        CrewListFrame.
        """
        if open is False:
            return
        iterator = list(self.category_frames.values())
        iterator.remove(frame)
        # Close the open ToggledFrames
        for toggled_frame in iterator:
            if bool(toggled_frame.show.get()) is True:
                toggled_frame.close()
