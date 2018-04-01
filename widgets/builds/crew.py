"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
# Project Modules
from utils.utilities import open_icon
from widgets.verticalscrollframe import VerticalScrollFrame


class CrewAbilitiesFrame(ttk.Frame):
    """
    Frame containing widgets describing the capabilities of a given
    Crew member. Shows the single active and both passive abilities
    with their icons and their descriptions, as well as the description
    provided for the crew member itself.
    """

    def __init__(self, parent: tk.Widget, data_dictionary: dict):
        """
        :param parent: Parent Widget, BuildsFrame
        :param data_dictionary: dictionary for this crew member.
            Specifically: companions.db[faction][category][index]
        """
        ttk.Frame.__init__(self, parent)
        self.frame = VerticalScrollFrame(self)
        self.interior = self.frame.interior
        self.data = data_dictionary
        self.description_label = ttk.Label(
            self.interior, text=self.data["Description"], justify=tk.LEFT, wraplength=300)
        self.images, self.widgets = list(), list()
        # Procedurally generate widgets
        for index, ability in enumerate(("Ability", "Passive", "SecondaryPassive")):
            icon = self.data["{}Icon".format(ability)]
            name = self.data["{}Name".format(ability)]
            dscr = self.data["{}Description".format(ability)]
            self.images.append(open_icon(icon))
            self.widgets.append(ttk.Label(
                self.interior, text=name + "\n" + dscr, image=self.images[index],
                compound=tk.LEFT, justify=tk.LEFT, wraplength=240)
            )
        self.grid_widgets()

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
        self.frame.grid()
        self.description_label.grid(column=0, row=0, sticky="we", padx=5, pady=5)
        for row, widget in enumerate(self.widgets):
            widget.grid(row=row + 1, column=0, sticky="nsw", padx=5, pady=(0, 5))
