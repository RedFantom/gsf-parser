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
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from widgets import HoverInfo, VerticalScrollFrame
from parsing import abilities
import variables


def open_image(image_name):
    """
    Open an image from the assets folder
    """
    # Type check for PyCharm completion
    if not isinstance(image_name, str):
        raise ValueError()
    icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
    if not image_name.endswith(".jpg"):
        image_name += ".jpg"
    filename = path.join(icons_path, image_name)
    if not path.exists(filename):
        messagebox.showinfo("Error", "A non-critical error occurred. The GSF Parser is missing an icon "
                                     "with the name {}. Please report this error if you did not modify the "
                                     "assets folder.".format(image_name))
        filename = path.join(icons_path, "imperial.png")
    return photo(img.open(filename))


class ComponentWidget(ttk.Frame):
    def __init__(self, parent, data_dictionary, ship, category):
        ttk.Frame.__init__(self, parent)
        self.data_dictionary = data_dictionary
        self.boolvars = []
        self.ship = ship
        self.name = self.data_dictionary["Name"]
        self.window = variables.main_window
        self.category = category

    def __getitem__(self, key):
        return self.data_dictionary[key]

    def __setitem__(self, key, value):
        self.data_dictionary[key] = value

    def set_level(self, index):
        if isinstance(index, tuple):
            index, value = index[0], index[1]
            item = self.boolvars[index][value]
            if value == 1 and self.boolvars[index][0].get() == 1:
                self.boolvars[index][0].set(False)
            elif value == 0 and self.boolvars[index][1].get() == 1:
                self.boolvars[index][1].set(False)
            self.ship[self.category][(index, value)] = item.get()
        else:
            item = self.boolvars[index]
            self.ship[self.category][index] = item.get()
        self.window.characters_frame.characters[self.window.builds_frame.character]["Ship Objects"][
            self.ship.name] = self.ship
        self.window.characters_frame.save_button.invoke()

    def grid_widgets(self):
        raise NotImplementedError


class MajorComponentWidget(ComponentWidget):
    def __init__(self, parent, data_dictionary, ship, category):
        ComponentWidget.__init__(self, parent, data_dictionary, ship, category)
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=300)
        self.interior = self.scroll_frame.interior
        self.description = data_dictionary["Description"]
        self.description_label = ttk.Label(self.interior, text=self.description, justify=tk.LEFT, wraplength=300)
        self.icon = data_dictionary["Icon"] + ".jpg"
        self.icon_photo = open_image(self.icon)
        self.icon_label = ttk.Label(self, image=self.icon_photo)
        self.upgrade_buttons = []
        self.hover_infos = []
        self.photos = []
        self.boolvars = []
        for i in range(5):
            if i >= 3:
                self.boolvars.append([tk.BooleanVar(), tk.BooleanVar()])
                if self.category in self.ship.components and self.ship[self.category] is not None:
                    self.boolvars[i][0].set(self.ship[self.category][(i, 0)])
                    self.boolvars[i][1].set(self.ship[self.category][(i, 1)])
                else:
                    self.boolvars[i][0].set(False)
                    self.boolvars[i][1].set(False)
                image_left = open_image(data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg")
                image_right = open_image(data_dictionary["TalentTree"][i][1]["Icon"] + ".jpg")
                self.photos.append([image_left, image_right])
                self.upgrade_buttons.append([ttk.Checkbutton(self.interior, image=self.photos[i][0],
                                                             command=lambda index=i: self.set_level((index, 0)),
                                                             # style="TButton",
                                                             variable=self.boolvars[i][0]),
                                             ttk.Checkbutton(self.interior, image=self.photos[i][1],
                                                             command=lambda index=i: self.set_level((index, 1)),
                                                             # style="TButton",
                                                             variable=self.boolvars[i][1])])
                self.hover_infos.append([HoverInfo(self.upgrade_buttons[i][0],
                                                   text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                        str(data_dictionary["TalentTree"][i][0]["Description"]),
                                                   width=50),
                                         HoverInfo(self.upgrade_buttons[i][1],
                                                   text=str(data_dictionary["TalentTree"][i][1]["Name"]) + "\n\n" +
                                                        str(data_dictionary["TalentTree"][i][1]["Description"]),
                                                   width=50)])
            else:
                self.boolvars.append(tk.BooleanVar())
                if self.ship[self.category] is not None:
                    self.boolvars[i].set(self.ship[self.category][i])
                else:
                    self.boolvars[i].set(False)
                self.photos.append(open_image(data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg"))
                self.upgrade_buttons.append(ttk.Checkbutton(self.interior, image=self.photos[i],
                                                            command=lambda index=i: self.set_level(index),
                                                            variable=self.boolvars[i]))  # , style="TButton"))
                self.hover_infos.append(HoverInfo(self.upgrade_buttons[i],
                                                  text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                       str(data_dictionary["TalentTree"][i][0]["Description"])))
        return

    def grid_widgets(self):
        self.scroll_frame.grid(sticky="nswe")
        self.description_label.grid(row=0, column=0, columnspan=2, pady=2, padx=5, sticky="nswe")
        set_row = 1
        for widget in self.upgrade_buttons:
            if isinstance(widget, list):
                widget[0].grid(row=set_row, column=0)
                widget[1].grid(row=set_row, column=1)
            else:
                widget.grid(row=set_row, column=0, columnspan=2)
            set_row += 1


class MiddleComponentWidget(ComponentWidget):
    def __init__(self, parent, data_dictionary, ship, category):
        ComponentWidget.__init__(self, parent, data_dictionary, ship, category)
        self.description = data_dictionary["Description"]
        self.description_label = ttk.Label(self, text=self.description, justify=tk.LEFT, wraplength=300)
        self.icon = data_dictionary["Icon"] + ".jpg"
        self.icon_photo = open_image(self.icon)
        self.icon_label = ttk.Label(self, image=self.icon_photo)
        self.upgrade_buttons = []
        self.hover_infos = []
        self.photos = []
        self.boolvars = []
        for i in range(3):
            if i >= 2:
                self.boolvars.append([tk.BooleanVar(), tk.BooleanVar()])
                if self.ship[self.category] is not None:
                    self.boolvars[i][0].set(self.ship[self.category][(i, 0)])
                    self.boolvars[i][1].set(self.ship[self.category][(i, 1)])
                else:
                    self.boolvars[i][0].set(False)
                    self.boolvars[i][1].set(False)
                icon_left = data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg"
                icon_right = data_dictionary["TalentTree"][i][1]["Icon"] + ".jpg"
                self.photos.append([open_image(icon_left), open_image(icon_right)])
                self.upgrade_buttons.append([ttk.Checkbutton(self, image=self.photos[i][0],
                                                             command=lambda index=i: self.set_level((index, 0)),
                                                             # style="TButton",
                                                             variable=self.boolvars[i][0]),
                                             ttk.Checkbutton(self, image=self.photos[i][1],
                                                             command=lambda index=i: self.set_level((index, 1)),
                                                             variable=self.boolvars[i][1])
                                             ])
                # style="TButton")])
                self.hover_infos.append([HoverInfo(self.upgrade_buttons[i][0],
                                                   text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                        str(data_dictionary["TalentTree"][i][0]["Description"]),
                                                   width=50),
                                         HoverInfo(self.upgrade_buttons[i][1],
                                                   text=str(data_dictionary["TalentTree"][i][1]["Name"]) + "\n\n" +
                                                        str(data_dictionary["TalentTree"][i][1]["Description"]),
                                                   width=50)])
            else:
                self.boolvars.append(tk.BooleanVar())
                if self.ship[self.category] is not None:
                    self.boolvars[i].set(self.ship[self.category][i])
                else:
                    self.boolvars[i].set(False)
                self.photos.append(open_image(data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg"))
                self.upgrade_buttons.append(ttk.Checkbutton(self, image=self.photos[i],
                                                            command=lambda index=i: self.set_level(index),
                                                            variable=self.boolvars[i]))
                # style="TButton"))
                self.hover_infos.append(HoverInfo(self.upgrade_buttons[i],
                                                  text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                       str(data_dictionary["TalentTree"][i][0]["Description"])))
        return

    def grid_widgets(self):
        self.description_label.grid(row=0, column=0, columnspan=2, pady=2, sticky="nswe", padx=5)
        set_row = 1
        for widget in self.upgrade_buttons:
            if isinstance(widget, list):
                widget[0].grid(row=set_row, column=0)
                widget[1].grid(row=set_row, column=1)
            else:
                widget.grid(row=set_row, column=0, columnspan=2)
            set_row += 1


class MinorComponentWidget(ComponentWidget):
    """
    Description
    Button 1
    Button 2
    Button 3

    Levels: 0, 1, 2, 3
    """

    def __init__(self, parent, data_dictionary, ship, category):
        ComponentWidget.__init__(self, parent, data_dictionary, ship, category)
        self.description = data_dictionary["Description"]
        self.description_label = ttk.Label(self, text=self.description, justify=tk.LEFT, wraplength=300)
        self.icon = data_dictionary["Icon"] + ".jpg"
        self.icon_photo = open_image(self.icon)
        self.icon_label = ttk.Label(self, image=self.icon_photo)
        self.upgrade_buttons = []
        self.hover_infos = []
        self.boolvars = []
        for i in range(3):
            self.boolvars.append(tk.BooleanVar())
            if self.ship[self.category] is not None:
                try:
                    self.boolvars[i].set(self.ship[self.category][i])
                except TypeError as e:
                    print(e)
                    print(self.ship[self.category][i])
                    self.boolvars[i].set(False)
            else:
                self.boolvars[i].set(False)
            self.upgrade_buttons.append(ttk.Checkbutton(self, image=self.icon_photo,
                                                        command=lambda index=i: self.set_level(index),
                                                        variable=self.boolvars[i]))
            self.hover_infos.append(HoverInfo(self.upgrade_buttons[i], str(data_dictionary["TalentTree"][i][0]["Name"])
                                              + "\n\n" + str(data_dictionary["TalentTree"][i][0]["Description"]),
                                              width=50))
        self.level = 0
        self.name = data_dictionary["Name"]

    def grid_widgets(self):
        self.description_label.grid(row=0, column=0, pady=2, sticky="nswe", padx=5)
        set_row = 1
        for widget in self.upgrade_buttons:
            widget.grid(row=set_row, column=0, pady=5)
            set_row += 1
