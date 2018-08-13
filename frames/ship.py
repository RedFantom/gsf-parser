"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard library
import os
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
# Packages
from PIL import Image, ImageTk
# Project Modules
from variables import settings
from utils.directories import get_assets_directory
from data.abilities import rep_ships


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

    def __init__(self, root_frame: tk.Widget):
        """Create all labels and variables"""
        ttk.Frame.__init__(self, root_frame, width=265, height=410)
        self.ship_label_var = tk.StringVar()
        self.ship_label_var.set("No match or spawn selected yet.")
        self.ship_label = ttk.Label(self, textvariable=self.ship_label_var, justify=tk.LEFT, wraplength=495)
        self.ship_image = ttk.Label(self)
        self.img = None  # Variable for the Image
        self.pic = None  # Variable for the PhotoImage

    def grid_widgets(self):
        """Put the widgets in the right place"""
        self.ship_image.grid(column=0, row=0, sticky="nswe")
        self.ship_label.grid(column=0, row=1, sticky="nswe", padx=5)
        self.remove_image()

    def update_ship(self, ships_list: list):
        """
        Update the picture of the ship by using the ships_list as
        reference. If multiple ships are possible, set the default.
        If zero ships are possible, there must be an error somewhere
        in the abilities module.
        """
        if len(ships_list) > 1:
            self.set_image("default")
            return
        elif len(ships_list) == 0:
            self.set_image("default")
            print("[ShipFrame] Invalid ships list retrieved.")
            return
        name = ships_list[0] if settings["gui"]["faction"] != "republic" else rep_ships[ships_list[0]]
        self.set_image(name)

    def set_image(self, file: str):
        """
        Set the image file, unless there is an IOError, because  then
        the assets folder is not in place
        """
        if not file.endswith(".png"):
            file += ".png"
        path = os.path.join(get_assets_directory(), "img", file)
        if not os.path.exists(path):
            print("[ShipFrame] File not found:", path)
            return
        self.img = Image.open(path)
        self.img = self.img.resize((260, 156), Image.ANTIALIAS)
        self.pic = ImageTk.PhotoImage(self.img)
        self.ship_image.config(image=self.pic)

    def remove_image(self):
        """Set the default image"""
        self.set_image("default")

    def config_size(self, width: int, height: int):
        pass