"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from utils import utilities


class ChoiceDialog(tk.Toplevel):
    def __init__(self, options=tuple(), label=""):
        tk.Toplevel.__init__(self)
        options = ("Choose",) + options
        self.ok_button = ttk.Button(self, text="OK", command=self.destroy)
        self.choice = tk.StringVar()
        self.choice_dropdown = ttk.OptionMenu(self, self.choice, *options)
        ttk.Label(self, text=label).grid(row=0, column=1, padx=5, pady=5)
        self.choice_dropdown.grid(row=1, column=1, sticky="nswe", padx=5, pady=(0, 5))
        self.ok_button.grid(row=2, column=1, sticky="nswe", padx=5, pady=(0, 5))
        screen_res = utilities.get_screen_resolution()
        self.update()
        req_size = (self.winfo_width(), self.winfo_height())
        self.wm_geometry("+{0}+{1}".format(
            int((screen_res[0] - req_size[0]) / 2), int((screen_res[1] - req_size[1]) / 2)))


def askoption(options: tuple, label=""):
    while True:
        toplevel = ChoiceDialog(options, label=label)
        toplevel.wait_window()
        value = toplevel.choice.get()
        if value == "Choose" or value not in options:
            mb.showerror("Error", "You must choose an option")
            continue
        return value
