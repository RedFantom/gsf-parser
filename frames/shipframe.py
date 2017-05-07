# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
try:
    import mttkinter.mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import tkMessageBox
import os
from PIL import Image, ImageTk
import variables
from parsing import abilities


class ShipFrame(ttk.Frame):
    """
    Simple frame with a picture and a string containing information about the ships
    used by the player.
    -----------------------------------
    | ------------------------------- |
    | |                             | |
    | | image of ship of player     | |
    | |                             | |
    | ------------------------------- |
    | string                          |
    | of                              |
    | text                            |
    |                                 |
    -----------------------------------
    """

    def __init__(self, root_frame):
        """
        Create all labels and variables
        :param root_frame:
        """
        ttk.Frame.__init__(self, root_frame, width=300, height=410)
        self.ship_label_var = tk.StringVar()
        self.ship_label_var.set("No match or spawn selected yet.")
        self.ship_label = ttk.Label(self, textvariable=self.ship_label_var, justify=tk.LEFT, wraplength=495)
        self.ship_image = ttk.Label(self)

    def grid_widgets(self):
        """
        Put the widgets in the right place
        :return:
        """
        self.ship_image.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.ship_label.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.remove_image()

    def update_ship(self, ships_list):
        """
        Update the picture of the ship by using the ships_list as reference
        If more ships are possible, set the default.
        If zero ships are possible, there must be an error somewhere in the abilities module
        :param ships_list:
        :return:
        """
        if len(ships_list) > 1:
            print "[DEBUG] Ship_list larger than 1, setting default.png"
            try:
                self.set_image(os.path.dirname(__file__).replace("frames", "") + "assets\\img\\default.png".
                               replace("\\", "/"))
            except IOError:
                print "[DEBUG] File not found."
                tkMessageBox.showerror("Error",
                                       "The specified picture can not be found. Is the assets folder copied correctly?")
                return
        elif len(ships_list) == 0:
            raise ValueError("Ships_list == 0")
        else:
            print "[DEBUG]  Ship_list not larger than one, setting appropriate image"
            try:
                if variables.settings_obj.faction == "republic":
                    img = abilities.rep_ships[ships_list[0]]
                else:
                    img = ships_list[0]
                self.set_image(os.path.dirname(__file__).replace("frames", "") +
                               ("\\assets\\img\\" + img + ".png").replace("\\", "/"))
            except IOError:
                tkMessageBox.showerror("Error",
                                       "The specified picture can not be found. Is the assets folder copied correctly?")
                return
        return

    def set_image(self, file):
        """
        Set the image file, unless there is an IOError, because  then the assets folder is not in place
        :param file:
        :return:
        """
        try:
            self.img = Image.open(file)
            self.img = self.img.resize((300, 180), Image.ANTIALIAS)
            self.pic = ImageTk.PhotoImage(self.img)
            self.ship_image.config(image=self.pic)
        except tk.TclError as e:
            print e

    def remove_image(self):
        """
        Set the default image
        :return:
        """
        try:
            self.pic = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.realpath(__file__)).
                                                     replace("frames", "") +
                                                     "assets\\img\\default.png").resize((300, 180), Image.ANTIALIAS))
        except IOError:
            print "[DEBUG] default.png can not be opened."
            return
        try:
            self.ship_image.config(image=self.pic)
        except tk.TclError:
            pass
