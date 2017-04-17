# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import Tkinter as tk
import ttk
from os import path
import cPickle as pickle
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from widgets import HoverInfo, ToggledFrame, vertical_scroll_frame


class ComponentListFrame(ttk.Frame):
    def __init__(self, parent, category, data_dictionary, callback):
        ttk.Frame.__init__(self, parent)
        # if not callable(callback):
        #     raise ValueError("Callback passed is not callable")
        self.names = {"PrimaryWeapon": "Primary Weapon",
                      "PrimaryWeapon2": "Primary Weapon",
                      "SecondaryWeapon": "Secondary Weapon",
                      "SecondaryWeapon2": "Secondary Weapon",
                      "Engine": "Engine",
                      "Systems": "Systems",
                      "Shield": "Shields",
                      "Magazine": "Magazine",
                      "Capacitor": "Capacitor",
                      "Reactor": "Reactor",
                      "Armor": "Armor",
                      "Sensor": "Sensors"
                      }
        self.category = category
        self.callback = callback
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        self.toggled_frame = ToggledFrame(self, text=self.names[category], labelwidth=28)
        self.frame = self.toggled_frame.sub_frame
        self.icons = {}
        self.buttons = {}
        self.hover_infos = {}
        for component in data_dictionary:
            self.icons[component["Name"]] = photo(img.open(path.join(self.icons_path, component["Icon"] + ".jpg")))
            self.buttons[component["Name"]] = ttk.Button(self.frame, image=self.icons[component["Name"]],
                                                         text=component["Name"],
                                                         command=lambda: self.set_component(component["Name"]),
                                                         compound=tk.LEFT, width=21)
            self.hover_infos[component["Name"]] = HoverInfo(self.buttons[component["Name"]],
                                                            text=str(component["Name"]) + "\n\n" +
                                                                 str(component["Description"]))
        self.data = data_dictionary

    def set_component(self, component):
        self.callback(self.category, component)

    def grid_widgets(self):
        self.toggled_frame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
        set_row = 0
        for button in self.buttons.itervalues():
            button.grid(row=set_row, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
            set_row += 1


class ShipSelectFrame(ttk.Frame):
    def __init__(self, parent, callback):
        ttk.Frame.__init__(self, parent)
        self.faction = "Imperial"
        self.ship = "Bloodmark",
        self.component = "Light Laser Cannon"
        self.scroll_frame = vertical_scroll_frame(self, canvaswidth=240, canvasheight=345, width=240, height=345)
        self.frame = self.scroll_frame.interior
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "ships", "categories.db"))) as db:
            self.data = pickle.load(db)
        self.callback = callback
        self.faction_frames = {}
        self.faction_buttons = {}
        self.ship_frames = {}
        self.ship_photos = {}
        self.ship_buttons = {}
        self.category_frames = {faction: {} for faction in self.data}
        self.faction_photos = {}
        toggled = False
        for faction in self.data:
            self.faction_frames[faction] = ttk.Frame(self.frame)
            self.faction_photos[faction] = photo(img.open(path.join(self.icons_path, faction.lower() + ".png")))
            self.faction_buttons[faction] = ttk.Button(self, text=faction, width=8,
                                                       command=lambda faction=faction: self.set_faction(faction),
                                                       image=self.faction_photos[faction], compound=tk.LEFT)
            for category in self.data[faction]:
                self.category_frames[faction][category["CategoryName"]] = ToggledFrame(self.frame, text=category["CategoryName"],
                                                                              labelwidth=27)
                if category["CategoryName"] == "Scout" and not toggled:
                    self.category_frames[faction][category["CategoryName"]].toggle()
                    toggled = True
                for ship_dict in category["Ships"]:
                    try:
                        image = img.open(path.join(self.icons_path, ship_dict["Icon"] + ".jpg"))
                        image = image.resize((52, 52))
                        self.ship_photos[ship_dict["Name"]] = photo(image)
                    except IOError:
                        self.ship_photos[ship_dict["Name"]] = photo(img.open(path.join(self.icons_path,
                                                                                       "imperial.png")))
                    self.ship_buttons[ship_dict["Name"]] = \
                        ttk.Button(self.category_frames[faction][category["CategoryName"]].sub_frame, text=ship_dict["Name"],
                                   image=self.ship_photos[ship_dict["Name"]], compound=tk.LEFT,
                                   command=lambda faction=faction, category=category, ship_dict=ship_dict:
                                   self.set_ship(faction, category["CategoryName"], ship_dict["Name"]),
                                   width=20)

    def grid_widgets(self):
        self.scroll_frame.grid(row=1, columnspan=2, sticky=tk.N+tk.S+tk.W+tk.E, pady=2)
        set_row = 0
        set_column = 0
        for button in self.faction_buttons.itervalues():
            button.grid(row=set_row, column=set_column, sticky=tk.N + tk.W + tk.E, padx=1)
            set_column += 1
        set_row = 20
        for faction in self.category_frames:
            if faction == self.faction:
                for frame in self.category_frames[faction].itervalues():
                    frame.grid(row=set_row, column=0, sticky=tk.N+tk.S+tk.W+tk.E, columnspan=2)
                    set_row += 1
            else:
                for frame in self.category_frames[faction].itervalues():
                    frame.grid_forget()
        set_row = 40
        for button in self.ship_buttons.itervalues():
            button.grid(row=set_row, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
            set_row += 1

    def set_ship(self, faction, category, shipname):
        print "Faction: %s\nCategory: %s\nShipname: %s" % (faction, category, shipname)
        self.callback(faction, category, shipname)

    def set_faction(self, faction):
        self.faction = faction
        self.grid_widgets()


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
        self.description = data_dictionary["Description"]
        self.description_label = ttk.Label(self, text=self.description, justify=tk.LEFT, wraplength=300)
        self.icon = data_dictionary["Icon"] + ".jpg"
        self.icon_image = img.open(path.join(self.icons_path, self.icon))
        self.icon_photo = photo(self.icon_image)
        self.icon_label = ttk.Label(self, image=self.icon_photo)
        self.upgrade_buttons = []
        self.hover_infos = []
        self.photos = []
        for i in range(5):
            if i >= 3:
                self.photos.append([photo(img.open(path.join(self.icons_path,
                                                             data_dictionary["TalentTree"][i][0]["Icon"] + ".jpg"))),
                                    photo(img.open(path.join(self.icons_path,
                                                             data_dictionary["TalentTree"][i][1]["Icon"] + ".jpg")))])
                self.upgrade_buttons.append([ttk.Button(self, image=self.photos[i][0],
                                                        command=lambda: press_button(self.upgrade_buttons[i][0],
                                                                                     self.set_level, i)),
                                             ttk.Button(self, image=self.photos[i][1],
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
                                                       command=lambda: press_button(self.upgrade_buttons[i][0],
                                                                                    self.set_level, i)))
                self.hover_infos.append(HoverInfo(self.upgrade_buttons[i],
                                                  text=str(data_dictionary["TalentTree"][i][0]["Name"]) + "\n\n" +
                                                       str(data_dictionary["TalentTree"][i][0]["Description"])))

    def grid_widgets(self):
        self.description_label.grid(row=0, column=0, columnspan=2, pady=2, padx=10)
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
        self.description_label.grid(row=0, column=0, columnspan=2, pady=2)
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
        self.description_label.grid(row=0, column=0, pady=2)
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
