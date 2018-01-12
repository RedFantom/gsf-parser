"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import configparser
import collections
import os
from tkinter import messagebox
# Custom modules
from utils import directories
from data.colors import default_colors, pastel_colors
from settings.eval import config_eval


class ColorSchemes(object):
    def __init__(self):
        self.current_scheme = collections.OrderedDict()

    def __setitem__(self, key, value):
        self.current_scheme[key] = value

    def __getitem__(self, key):
        try:
            return list(self.current_scheme[key])
        except TypeError:
            messagebox.showerror(
                "Error", "The requested color for %s was could not be "
                         "type changed into a list. Did you alter the "
                         "event_colors.ini file?" % key)
            return ['#ffffff', '#000000']

    def set_scheme(self, name, custom_file=(os.path.join(directories.get_temp_directory(), "events_colors.ini"))):
        name = name.lower()
        if name == "bright":
            self.current_scheme = default_colors
        elif name == "pastel":
            self.current_scheme = pastel_colors
        elif name == "custom":
            cp = configparser.RawConfigParser()
            cp.read(custom_file)
            try:
                current_scheme = dict(cp.items("colors"))
                for key, value in list(current_scheme.items()):
                    self.current_scheme[key] = config_eval(value)
            except configparser.NoSectionError:
                self.current_scheme = default_colors
                messagebox.showinfo(
                    "Info", "Failed to load custom colors, default colors have been loaded as "
                            "custom color scheme.")
        else:
            raise ValueError("Expected default, pastel or custom, got %s" % name)

    def write_custom(self):
        custom_file = os.path.join(directories.get_temp_directory(), "event_colors.ini")
        cp = configparser.RawConfigParser()
        try:
            cp.add_section("colors")
        except configparser.DuplicateSectionError:
            pass
        for key, value in list(self.current_scheme.items()):
            cp.set('colors', key, value)
        with open(custom_file, "w") as file_obj:
            cp.write(file_obj)
