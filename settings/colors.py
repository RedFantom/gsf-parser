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


class ColorScheme(object):
    """
    This class provides an interface to a ConfigParser that stores the
    colors used in the EventsView in a .ini file in the temporary
    files directory. The colors are stored in memory in an Ordered
    Dictionary in order to allow for looping over them in the correct
    order for the user interface.
    """
    def __init__(self):
        self.current_scheme = collections.OrderedDict()

    def __setitem__(self, key, value):
        self.current_scheme[key] = value

    def __getitem__(self, key):
        """
        Retrieves a color for a certain category and provides error
        handling for when the color is not available. The color may not
        be found if the colors.ini file was modified by the user.
        """
        try:
            return list(self.current_scheme[key])
        except (TypeError, KeyError, ValueError):
            messagebox.showerror(
                "Error", "The requested color for %s was could not be "
                         "type changed into a list. Did you alter the "
                         "event_colors.ini file?" % key)
            return ['#ffffff', '#000000']

    def set_scheme(self, name, custom_file=(os.path.join(directories.get_temp_directory(), "events_colors.ini"))):
        """
        Set the scheme to either the bright scheme, pastel scheme or
        the custom scheme. If the scheme is set to custom, then the
        configuration file is read from event_colors.ini.
        """
        name = name.lower()
        if name == "bright":
            self.current_scheme = default_colors
        elif name == "pastel":
            self.current_scheme = pastel_colors
        elif name == "custom":
            # Read the custom color scheme file
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
        """
        Writes the current_scheme instance attribute to the
        configuration file in the temporary directory.
        """
        custom_file = os.path.join(directories.get_temp_directory(), "event_colors.ini")
        cp = configparser.RawConfigParser()
        cp.add_section("colors")
        for key, value in list(self.current_scheme.items()):
            cp.set('colors', key, value)
        with open(custom_file, "w") as file_obj:
            cp.write(file_obj)
