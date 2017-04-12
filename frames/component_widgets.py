# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import Tkinter as tk
import ttk
from os import path
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from variables import settings_obj as settings
from widgets import HoverInfo


class ComponentWidget(ttk.Frame):
    def __init__(self, parent, data_dictionary):
        ttk.Frame.__init__(self, parent)
        self.data_dictionary = data_dictionary
        if settings.faction == "imperial":
            self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons",
                                                     "imperial"))
        elif settings.faction == "republic":
            self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons",
                                                     "republic"))
        else:
            raise ValueError("Unexpected value for faction found.")

    def __getitem__(self, key):
        return self.data_dictionary[key]

    def __setitem__(self, key, value):
        self.data_dictionary[key] = value


class MajorComponentWidget(ComponentWidget):
    def __init__(self, parent, data_dictionary, ship):
        ComponentWidget.__init__(self, parent, data_dictionary)


class MiddleComponentFrame(ComponentWidget):
    def __init__(self, parent, data_dictionary, ship):
        ComponentWidget.__init__(self, parent, data_dictionary)


class MinorComponentWidget(ComponentWidget):
    """
    Description
    Button 1
    Button 2
    Button 3

    Levels: 0, 1, 2, 3
    """
    def __init__(self, parent, data_dictionary, ship):
        ComponentWidget.__init__(self, parent, data_dictionary)
        self.description = data_dictionary["Description"]
        self.description_label = ttk.Label(self, text=self.description, justify=tk.LEFT, wraplength=200)
        self.icon = data_dictionary["Icon"] + ".jpg"
        self.icon_image = img.open(path.join(self.icons_path, self.icon))
        self.icon_photo = photo(self.icon_image)
        self.icon_label = ttk.Label(self, image=self.icon_photo)
        self.upgrade_buttons = []
        self.hover_infos = []
        for i in range(3):
            self.upgrade_buttons.append(ttk.Button(self, image=self.icon_photo,
                                                   command=lambda: press_button(self.upgrade_buttons[i],
                                                                                self.enable_level, i+1)))
            self.hover_infos.append(HoverInfo(self.upgrade_buttons[i], str(data_dictionary["TalentTree"][i][0]["Name"])
                                              + "\n\n" + str(data_dictionary["TalentTree"][i][0]["Description"]),
                                              width=50))
        self.level = 0
        self.name = data_dictionary["Name"]

    def grid_widgets(self):
        self.description_label.grid(row=0, column=0)
        set_row = 1
        for widget in self.upgrade_buttons:
            widget.grid(row=set_row, column=0, pady=5)
            set_row += 1

    def enable_level(self, level):
        pass


def press_button(button, callback, *args):
    button.config(relief=tk.SUNKEN)
    callback(*args)


def release_button(button, callback, *args):
    button.config(relief=tk.RAISED)
    callback(*args)
