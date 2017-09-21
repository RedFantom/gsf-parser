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
from widgets.verticalscrollframe import VerticalScrollFrame


class CrewAbilitiesFrame(ttk.Frame):
    def __init__(self, parent, data_dictionary):
        ttk.Frame.__init__(self, parent)
        self.frame = VerticalScrollFrame(self)
        self.data = data_dictionary
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        self.description_label = ttk.Label(self.frame.interior, text=self.data["Description"], justify=tk.LEFT,
                                           wraplength=300)
        try:
            self.active_image = photo(img.open(path.join(self.icons_path, self.data["AbilityIcon"] + ".jpg")))
        except FileNotFoundError:
            messagebox.showerror("Error", "The GSF Parser is missing the following icon in the assets folder: {}. "
                                          "Please report this error if you did not modify the assets folder.".
                                          format(self.data["AbilityIcon"]))
        self.passive_one_image = photo(img.open(path.join(self.icons_path, self.data["PassiveIcon"] + ".jpg")))
        self.passive_two_image = photo(img.open(path.join(self.icons_path, self.data["SecondaryPassiveIcon"] + ".jpg")))
        self.active_label = ttk.Label(self.frame.interior,
                                      text=(self.data["AbilityName"] + "\n" + self.data["AbilityDescription"]),
                                      image=self.active_image, compound=tk.LEFT, justify=tk.LEFT, wraplength=250)
        self.passive_one_label = ttk.Label(self.frame.interior, text=(self.data["PassiveName"] + "\n" +
                                                                      self.data["PassiveDescription"]),
                                           image=self.passive_one_image, compound=tk.LEFT, justify=tk.LEFT,
                                           wraplength=250)
        self.passive_two_label = ttk.Label(self.frame.interior, text=(self.data["SecondaryPassiveName"] + "\n" +
                                                                      self.data["SecondaryPassiveDescription"]),
                                           image=self.passive_two_image, compound=tk.LEFT, justify=tk.LEFT,
                                           wraplength=250)

    def grid_widgets(self):
        self.frame.grid()
        self.description_label.grid(column=0, row=0, sticky="we")
        self.active_label.grid(column=0, row=1, sticky="we")
        self.passive_one_label.grid(column=0, row=2, sticky="we")
        self.passive_two_label.grid(column=0, row=3, sticky="we")
