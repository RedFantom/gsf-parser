"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
from ttkwidgets.frames import Balloon
# Project Modules
from variables import main_window
from widgets import VerticalScrollFrame
from utils.utilities import open_icon


class ComponentWidget(ttk.Frame):
    """
    The ComponentWidget class is the parent class to Minor-, Middle-
    and MajorComponentWidget. It consists of a Frame containing the
    Checkbutton widgets for selecting upgrades for a specific component.
    It is displayed on the far right of the BuildsFrame.
    """

    def __init__(self, parent, data_dictionary, ship, category):
        """
        :param parent: BuildsFrame instance
        :param data_dictionary: The data dictionary of this component.
            Specifically: ships.db[faction][ship][type][index] -> this
        :param ship: parsing.ships.Ship instance to modify upgrades in
        :param category: Component category name
        """
        ttk.Frame.__init__(self, parent)
        self.vars = list()  # Contains upgrades
        self.ship = ship
        self.name = data_dictionary["Name"]
        self.window = main_window
        self.category = category

        """
        Interior Frame
        
        Major components require a VerticalScrollFrame due to the 
        vertical space required for the widgets of five upgrade levels.
        """
        if len(data_dictionary["TalentTree"]) == 5:
            self.wrapper_frame = VerticalScrollFrame(self, canvaswidth=300)
            self.interior = self.wrapper_frame.interior
        else:
            self.interior = self.wrapper_frame = ttk.Frame(self)

        """Static Widget Creation"""
        self.description_label = ttk.Label(
            self.interior, text=data_dictionary["Description"], justify=tk.LEFT, wraplength=300)
        self.icon_label = ttk.Label(self, image=open_icon(data_dictionary["Icon"]))

        """Procedural Widget Creation"""
        self.upgrade_buttons, self.photos, self.balloons, self.vars = \
            self.build_widgets(data_dictionary)
        self.update_widgets()

    def set_level(self, index):
        """
        Callback for Checkbutton upgrade Button widgets

        Changes the upgrade status for a given upgrade level
        (index + 1). Toggles the Boolean variable for that level.

        Major and Middle Components feature two-choice upgrades. In
        this case, index is given as a tuple of (level - 1, choice),
        choice being an int 0 or 1. If the other choice was already
        selected for this level, it is unselected and the new choice is
        enabled.

        Saves the database to prevent data loss.
        """
        # Two-choice upgrade level
        if isinstance(index, tuple):
            # index = level - 1
            index, choice = index[0], index[1]
            item = self.vars[index][choice]  # item: tk.BooleanVar
            # Disable other choice if it was selected
            if choice == 0 and self.vars[index][0].get() is True:
                self.vars[index][0].set(False)
            elif choice == 0 and self.vars[index][1].get() is True:
                self.vars[index][1].set(False)
            # Update Ship instance with new upgrade
            self.ship[self.category][(index, choice)] = item.get()
        # Simple upgrade level
        else:
            item = self.vars[index]
            self.ship[self.category][index] = item.get()
        # Access CharacterDatabase managed by CharactersFrame
        self.window.characters_frame.characters[self.window.builds_frame.character]["Ship Objects"][
            self.ship.name] = self.ship
        self.window.characters_frame.save_button.invoke()

    def build_widgets(self, data: dict):
        """
        Build the upgrade level widgets, regardless of Component type
        for a given Component. Return the icons (to prevent garbage
        collection), Checkbutton widgets and Balloon widgets in lists.
        """
        buttons, photos, balloons, bools = list(), list(), list(), list()
        # data["TalentTree"] contains component upgrades
        for index in range(len(data["TalentTree"])):
            button, photo, balloon, var = list(), list(), list(), list()
            for choice in range(len(data["TalentTree"][index])):
                upgrade = data["TalentTree"][index][choice]
                elements = self.build_upgrade_widgets(upgrade, (index, choice))
                for elem, lst in zip(elements, (button, photo, balloon, var)):
                    lst.append(elem)
            for master, child in zip((buttons, photos, balloons, bools), (button, photo, balloon, var)):
                master.append(child)
        return buttons, photos, balloons, bools

    def build_upgrade_widgets(self, upgrade: dict, index: (int, tuple)):
        """Create the widgets for a given upgrade dictionary"""
        photo = open_icon(upgrade["Icon"])
        var = tk.BooleanVar(self, value=False)
        button = ttk.Checkbutton(
            self.interior, image=photo, variable=var,
            command=lambda i=index: self.set_level(i))
        balloon = Balloon(
            button, width=250, headertext=upgrade["Name"], text=upgrade["Description"])
        return button, photo, balloon, var

    def update_widgets(self):
        """Update widget Checkbutton (BooleanVar) state"""
        if self.ship[self.category] is None:
            return
        for index in range(len(self.vars)):
            if isinstance(self.vars[index], list):
                for choice in range(2):
                    self.vars[index][choice].set(self.ship[self.category][index][choice])
                continue
            self.vars[index].set(self.ship[self.category][index])

    def grid_widgets(self):
        """
        Configure wigets in grid geometry manager

        Two columns. Each of the simple upgrade buttons is put in the
        middle (half in both rows), each of the two-choice upgrade
        buttons is put in either the left or right row.
        """
        self.wrapper_frame.grid(sticky="nswe")
        self.description_label.grid(row=0, column=0, columnspan=2, pady=2, padx=5, sticky="nswe")
        set_row = 1
        for pair in self.upgrade_buttons:
            for i in range(len(pair)):
                kwargs = {"row": set_row, "column": i}
                if len(pair) == 1:
                    kwargs["columnspan"] = 2
                pair[i].grid(**kwargs)
            set_row += 1

