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
from widgets import HoverInfo


class ComponentWidget(ttk.Frame):
    def __init__(self, parent, data_dictionary):
        ttk.Frame.__init__(self, parent)
        self.data_dictionary = data_dictionary
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))

    def __getitem__(self, key):
        return self.data_dictionary[key]

    def __setitem__(self, key, value):
        self.data_dictionary[key] = value

    def set_level(self, level):
        raise NotImplementedError

    def grid_widgets(self):
        raise NotImplementedError


class MajorComponentWidget(ComponentWidget):
    def __init__(self, parent, data_dictionary, ship):
        ComponentWidget.__init__(self, parent, data_dictionary)


class MiddleComponentWidget(ComponentWidget):
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
        self.photos = []
        for i in range(3):
            if i == 2:
                self.photos.append(photo(img.open(path.join(self.icons_path,
                                                            data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg"))))
                self.photos.append(photo(img.open(path.join(self.icons_path,
                                                            data_dictionary["TalentTree"][i][1]["Icon"] + ".jpg"))))
                self.upgrade_buttons.append([ttk.Button(self, image=self.photos[i],
                                                        command=lambda: press_button(self.upgrade_buttons[i][0],
                                                                                     self.set_level, i)),
                                             ttk.Button(self, image=self.photos[i + 1],
                                                        command=lambda: press_button(self.upgrade_buttons[i][1],
                                                                                     self.set_level, i + 1))])
                self.hover_infos.append([HoverInfo(self.upgrade_buttons[i][0],
                                                   text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                        str(data_dictionary["TalentTree"][i][0]["Description"]),
                                                   width=50),
                                         HoverInfo(self.upgrade_buttons[i][1],
                                                   text=str(data_dictionary["TalentTree"][i][1]["Name"]) + "\n\n" +
                                                        str(data_dictionary["TalentTree"][i][1]["Description"]),
                                                   width=50)])
            else:
                self.photos.append(photo(img.open(path.join(self.icons_path,
                                                            data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg"))))
                self.upgrade_buttons.append(ttk.Button(self, image=self.photos[i],
                                                       command=lambda: press_button(self.upgrade_buttons[i],
                                                                                    self.set_level, i)))
                self.hover_infos.append(HoverInfo(self.upgrade_buttons[i],
                                                  text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                       str(data_dictionary["TalentTree"][i][0]["Description"])))

    def grid_widgets(self):
        self.description_label.grid(row=0, column=0, columnspan=2)
        set_row = 1
        for widget in self.upgrade_buttons:
            if isinstance(widget, list):
                widget[0].grid(row=set_row, column=0)
                widget[1].grid(row=set_row, column=1)
            else:
                widget.grid(row=set_row, column=0, columnspan=2)
            set_row += 1

    def set_level(self, level):
        pass


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
                                                                                self.set_level, i + 1)))
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

    def set_level(self, level):
        pass


def press_button(button, callback, *args):
    button.config(relief=tk.SUNKEN)
    callback(*args)


def release_button(button, callback, *args):
    button.config(relief=tk.RAISED)
    callback(*args)
