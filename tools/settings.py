"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI imports
import tkinter.messagebox
import tkinter.filedialog
# General imports
import os
import configparser
import collections
import ast
from tools import utilities
from ast import literal_eval


def eval(value):
    try:
        literal = literal_eval(value)
    except ValueError:
        return value
    except SyntaxError:
        return value
    if literal == 1:
        return True
    elif literal == 0:
        return False
    else:
        return literal


# Class that loads, stores and saves settings
class Settings(object):
    defaults = {
        "misc": {
            "version": "v4.0.1",
            "autoupdate": True,
            "patch_level": "5.5",
            "temp_dir": ""
        },
        "gui": {
            "event_colors": True,
            "event_scheme": "pastel",
            "faction": "empire",
            "debug": False
        },
        "parsing": {
            "path": os.path.realpath(
                os.path.join(os.path.expanduser("~"), "Documents", "Star Wars - The Old Republic", "CombatLogs")),
            "address": "parser.thrantasquadron.tk",
            "port": 83
        },
        "realtime": {
            "overlay": True,
            "overlay_text": "Yellow",
            "overlay_position": "x0y0",
            "overlay_when_gsf": True,
            "screenparsing": True,
            "screen_overlay": True,
            "screen_features": ["Tracking penalty", "Ship health", "Power management"],
            "overlay_experimental": False
        },
    }

    # Set the file_name for use by other functions
    def __init__(self, file_name="settings.ini", directory=utilities.get_temp_directory()):
        self.directory = directory
        self.file_name = os.path.join(directory, file_name)
        self.conf = configparser.ConfigParser()
        self.settings = {key: self.SettingsDictionary(key) for key in self.defaults.keys()}
        self.read_settings()
        if self["misc"]["version"] != self.defaults["misc"]["version"]:
            self.write_settings({"misc": {"version": self.defaults["misc"]["version"]}})

    def write_defaults(self):
        conf = configparser.ConfigParser()
        conf.read_dict(self.defaults)
        with open(self.file_name, "w") as fo:
            conf.write(fo)

    def write_settings(self, dictionary):
        dictionary = {str(section): {str(key): str(value) for key, value in dictionary[section].items()}
                      for section in dictionary.keys()}
        conf = configparser.ConfigParser()
        for section in dictionary.keys():
            self.settings[section].update(dictionary[section])
        self.settings["misc"]["version"] = self.defaults["misc"]["version"]
        conf.read_dict(self.settings)
        with open(self.file_name, "w") as fo:
            conf.write(fo)
        self.read_settings()

    def read_settings(self):
        self.settings.clear()
        if os.path.basename(self.file_name) not in os.listdir(self.directory):
            self.write_defaults()
        with open(self.file_name, "r") as fi:
            self.conf.read_file(fi)
        for section, dictionary in self.conf.items():
            self.settings[section] = self.SettingsDictionary(section)
            for item, value in dictionary.items():
                try:
                    self.settings[section][item] = eval(value)
                except ValueError as e:
                    print(e)
                    print("Section: {0}, Item {1}".format(section, item))
        return

    def __getitem__(self, section):
        if section not in self.settings:
            self.write_defaults()
            self.read_settings()
        return self.settings[section]

    def __contains__(self, item):
        return item in self.settings

    class SettingsDictionary(object):
        def __init__(self, section):
            self._section = section
            self._data = {}
            self.items = self._data.items
            self.update = self._data.update

        def __getitem__(self, item):
            if item == 0:
                return None
            if item not in self._data:
                self._data[item] = Settings.defaults[self._section][item]
            return self._data[item]

        def __contains__(self, item):
            return item in self._data

        def __setitem__(self, key, value):
            if isinstance(value, str) and not os.path.exists(value):
                value = value.lower()
            self._data[key] = value


class ColorSchemes(object):
    def __init__(self):
        self.default_colors = collections.OrderedDict()
        self.default_colors['dmgd_pri'] = ['#ffd11a', '#000000']
        self.default_colors['dmgt_pri'] = ['#ff0000', '#000000']
        self.default_colors['dmgd_sec'] = ['#e6b800', '#000000']
        self.default_colors['dmgt_sec'] = ['#cc0000', '#000000']
        self.default_colors['selfdmg'] = ['#990000', '#000000']
        self.default_colors['healing'] = ['#00b300', '#000000']
        self.default_colors['selfheal'] = ['#008000', '#000000']
        self.default_colors['engine'] = ['#8533ff', '#ffffff']
        self.default_colors['shield'] = ['#004d00', '#ffffff']
        self.default_colors['system'] = ['#002db3', '#ffffff']
        self.default_colors['other'] = ['#33adff', '#000000']
        self.default_colors['spawn'] = ['#000000', '#ffffff']
        self.default_colors['match'] = ['#000000', '#ffffff']
        self.default_colors['default'] = ['#ffffff', '#000000']
        self.pastel_colors = collections.OrderedDict()
        self.pastel_colors['dmgd_pri'] = ['#ffe066', '#000000']
        self.pastel_colors['dmgt_pri'] = ['#ff6666', '#000000']
        self.pastel_colors['dmgd_sec'] = ['#ffd633', '#000000']
        self.pastel_colors['dmgt_sec'] = ['#ff3333', '#000000']
        self.pastel_colors['selfdmg'] = ['#b30000', '#000000']
        self.pastel_colors['healing'] = ['#80ff80', '#000000']
        self.pastel_colors['selfheal'] = ['#66ff8c', '#000000']
        self.pastel_colors['engine'] = ['#b380ff', '#000000']
        self.pastel_colors['shield'] = ['#ccffcc', '#000000']
        self.pastel_colors['system'] = ['#668cff', '#000000']
        self.pastel_colors['other'] = ['#80ccff', '#000000']
        self.pastel_colors['spawn'] = ['#b3b3b3', '#000000']
        self.pastel_colors['match'] = ['#b3b3b3', '#000000']
        self.pastel_colors['default'] = ['#ffffff', '#000000']
        self.current_scheme = collections.OrderedDict()

    def __setitem__(self, key, value):
        self.current_scheme[key] = value

    def __getitem__(self, key):
        try:
            return list(self.current_scheme[key])
        except TypeError:
            tkinter.messagebox.showerror("Error", "The requested color for %s was could not be "
                                                  "type changed into a list. Did you alter the "
                                                  "event_colors.ini file?" % key)
            return ['#ffffff', '#000000']

    def set_scheme(self, name, custom_file=(os.path.join(utilities.get_temp_directory(), "events_colors.ini"))):
        name = name.lower()
        if name == "bright":
            self.current_scheme = self.default_colors
        elif name == "pastel":
            self.current_scheme = self.pastel_colors
        elif name == "custom":
            cp = configparser.RawConfigParser()
            cp.read(custom_file)
            try:
                current_scheme = dict(cp.items("colors"))
                for key, value in list(current_scheme.items()):
                    self.current_scheme[key] = ast.literal_eval(value)
            except configparser.NoSectionError:
                self.current_scheme = self.default_colors
                tkinter.messagebox.showinfo("Info", "Failed to load custom colors, default colors have been loaded as "
                                                    "custom color scheme.")
        else:
            raise ValueError("Expected default, pastel or custom, got %s" % name)

    def write_custom(self):
        custom_file = os.path.join(utilities.get_temp_directory(), "event_colors.ini")
        cp = configparser.RawConfigParser()
        try:
            cp.add_section("colors")
        except configparser.DuplicateSectionError:
            pass
        for key, value in list(self.current_scheme.items()):
            cp.set('colors', key, value)
        with open(custom_file, "w") as file_obj:
            cp.write(file_obj)
