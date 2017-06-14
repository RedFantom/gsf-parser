# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

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
    literal = literal_eval(value)
    if literal == 1:
        return True
    elif literal == 0:
        return False
    else:
        return literal


# Class with default settings for in the settings file
class Defaults(object):
    # Version to display in settings tab
    version = "v3.0.0"
    # Path to get the CombatLogs from
    cl_path = (os.path.expanduser("~") + "\\Documents\\Star Wars - The Old Republic\\CombatLogs").replace("\\", "/")
    # Automatically send and retrieve names and hashes of ID numbers from the remote server
    auto_ident = str(False)
    # Address and port of the remote server
    server_address = "parser.thrantasquadron.tk"
    server_port = str(83)
    # Automatically upload CombatLogs as they are parsed to the remote server
    auto_upl = str(False)
    # Enable the overlay
    overlay = str(True)
    # Set the overlay opacity, or transparency
    opacity = str(1.0)
    # Set the overlay size
    size = "big"
    # Set the corner the overlay will be displayed in
    pos = "TR"
    # Set the text color of the parser
    color = "#236ab2"
    # Set the logo color
    logo_color = "Green"
    # Overlay background color
    overlay_bg_color = "White"
    # Overlay color that is displayed as transparent
    overlay_tr_color = "White"
    # Overlay text color
    overlay_tx_color = "Yellow"
    # Overlay text font
    overlay_tx_font = "Calibri"
    # Overlay text size
    overlay_tx_size = "12"
    # Only display overlay when a GSF match is running
    overlay_when_gsf = str(False)
    # Set the timeout for reading from file for realtime
    timeout = 0.2
    # Event color options
    event_colors = "basic"
    # Event color scheme
    event_scheme = "default"
    # The date format for in the files Listbox
    date_format = "ymd"

    faction = "imperial"
    events_overlay = False
    screenparsing = True
    screenparsing_overlay = True
    screenparsing_features = ["Enemy name and ship type", "Tracking penalty", "Ship health",
                              "Power management"]
    autoupdate = True


# Class that loads, stores and saves settings
class Settings(object):
    # Set the file_name for use by other functions
    def __init__(self, file_name="settings.ini", directory=utilities.get_temp_directory()):
        self.directory = directory
        self.file_name = os.path.join(directory, file_name)
        self.conf = configparser.RawConfigParser()
        # variables.install_path = os.getcwd()
        if file_name in os.listdir(self.directory):
            try:
                self.read_set()
            except configparser.NoOptionError:
                self.write_def()
                self.read_set()
        else:
            self.write_def()
            self.read_set()

    # Read the settings from a file containing a pickle and store them as class variables
    def read_set(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.conf.read(self.file_name)
        self.version = self.conf.get("misc", "version")
        self.cl_path = self.conf.get("parsing", "cl_path")
        self.auto_ident = eval(self.conf.get("parsing", "auto_ident"))
        self.server_address = self.conf.get("sharing", "server_address")
        self.server_port = int(self.conf.get("sharing", "server_port"))
        self.auto_upl = eval(self.conf.get("sharing", "auto_upl"))
        self.overlay = eval(self.conf.get("realtime", "overlay"))
        self.overlay_bg_color = self.conf.get("realtime", "overlay_bg_color")
        self.overlay_tr_color = self.conf.get("realtime", "overlay_tr_color")
        self.overlay_tx_color = self.conf.get("realtime", "overlay_tx_color")
        self.opacity = float(self.conf.get("realtime", "opacity"))
        self.size = self.conf.get("realtime", "size")
        self.pos = self.conf.get("realtime", "pos")
        self.timeout = float(self.conf.get("realtime", "timeout"))
        self.color = self.conf.get("gui", "color")
        self.event_colors = self.conf.get("gui", "event_colors")
        self.event_scheme = self.conf.get("gui", "event_scheme")
        self.logo_color = self.conf.get("gui", "logo_color")
        self.date_format = self.conf.get("gui", "date_format")
        self.overlay_tx_font = self.conf.get("realtime", "overlay_tx_font")
        self.overlay_tx_size = self.conf.get("realtime", "overlay_tx_size")
        self.faction = self.conf.get("gui", "faction")
        self.overlay_when_gsf = eval(self.conf.get("realtime", "overlay_when_gsf"))
        self.events_overlay = eval(self.conf.get("realtime", "events_overlay"))
        self.screenparsing = eval(self.conf.get("realtime", "screenparsing"))
        self.screenparsing_features = eval(self.conf.get("realtime", "screenparsing_features"))
        self.screenparsing_overlay = eval(self.conf.get("realtime", "screenparsing_overlay"))
        self.autoupdate = eval(self.conf.get("misc", "autoupdate"))
        print("[DEBUG] Settings read")

    # Write the defaults settings found in the class defaults to a pickle in a
    # file
    def write_def(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        try:
            self.conf.add_section("misc")
            self.conf.add_section("parsing")
            self.conf.add_section("sharing")
            self.conf.add_section("realtime")
            self.conf.add_section("gui")
        except configparser.DuplicateSectionError:
            pass
        self.conf.set("misc", "version", Defaults.version)
        self.conf.set("parsing", "cl_path", Defaults.cl_path)
        self.conf.set("parsing", "auto_ident", Defaults.auto_ident)
        self.conf.set("sharing", "server_address", Defaults.server_address)
        self.conf.set("sharing", "server_port", Defaults.server_port)
        self.conf.set("sharing", "auto_upl", Defaults.auto_upl)
        self.conf.set("realtime", "overlay", Defaults.overlay)
        self.conf.set("realtime", "opacity", Defaults.opacity)
        self.conf.set("realtime", "size", Defaults.size)
        self.conf.set("realtime", "pos", Defaults.pos)
        self.conf.set("realtime", "overlay_bg_color", Defaults.overlay_bg_color)
        self.conf.set("realtime", "overlay_tx_color", Defaults.overlay_tx_color)
        self.conf.set("realtime", "overlay_tr_color", Defaults.overlay_tr_color)
        self.conf.set("gui", "color", Defaults.color)
        self.conf.set("gui", "logo_color", Defaults.logo_color)
        self.conf.set("gui", "event_colors", Defaults.event_colors)
        self.conf.set("gui", "event_scheme", Defaults.event_scheme)
        self.conf.set("gui", "date_format", Defaults.date_format)
        self.conf.set("realtime", "overlay_tx_font", Defaults.overlay_tx_font)
        self.conf.set("realtime", "overlay_tx_size", Defaults.overlay_tx_size)
        self.conf.set("realtime", "overlay_when_gsf", Defaults.overlay_when_gsf)
        self.conf.set("realtime", "timeout", Defaults.timeout)
        self.conf.set("gui", "faction", Defaults.faction)
        self.conf.set("realtime", "events_overlay", Defaults.events_overlay)
        self.conf.set("realtime", "screenparsing", Defaults.screenparsing)
        self.conf.set("realtime", "screenparsing_overlay", Defaults.screenparsing_overlay)
        self.conf.set("realtime", "screenparsing_features", Defaults.screenparsing_features)
        self.conf.set("misc", "autoupdate", Defaults.autoupdate)
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)
        print("[DEBUG] Defaults written")
        self.read_set()

    # Write the settings passed as arguments to a pickle in a file
    # Setting defaults to default if not specified, so all settings are always
    # written
    def write_set(self,
                  version=Defaults.version,
                  cl_path=Defaults.cl_path,
                  auto_ident=Defaults.auto_ident,
                  server_address=Defaults.server_address,
                  server_port=Defaults.server_port,
                  auto_upl=Defaults.auto_upl,
                  overlay=Defaults.overlay,
                  opacity=Defaults.opacity,
                  size=Defaults.size,
                  pos=Defaults.pos,
                  color=Defaults.color,
                  logo_color=Defaults.logo_color,
                  bg_color=Defaults.overlay_bg_color,
                  tx_color=Defaults.overlay_tx_color,
                  tr_color=Defaults.overlay_tr_color,
                  tx_font=Defaults.overlay_tx_font,
                  tx_size=Defaults.overlay_tx_size,
                  overlay_when_gsf=Defaults.overlay_when_gsf,
                  timeout=Defaults.timeout,
                  event_colors=Defaults.event_colors,
                  event_scheme=Defaults.event_scheme,
                  date_format=Defaults.date_format,
                  faction=Defaults.faction,
                  events_overlay=Defaults.events_overlay,
                  screenparsing=Defaults.screenparsing,
                  screenparsing_overlay=Defaults.screenparsing_overlay,
                  screenparsing_features=Defaults.screenparsing_features,
                  autoupdate=Defaults.autoupdate):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        try:
            self.conf.add_section("misc")
            self.conf.add_section("parsing")
            self.conf.add_section("sharing")
            self.conf.add_section("realtime")
            self.conf.add_section("gui")
        except:
            pass
        # TODO Make this setting changeable without restarting
        if str(auto_upl) != self.conf.get("sharing", "auto_upl"):
            tkinter.messagebox.showinfo("Notice", "In order to change the setting for "
                                                  "auto uploading CombatLogs, the "
                                                  "parser must be restarted.")
        if str(auto_ident) != self.conf.get("parsing", "auto_ident"):
            tkinter.messagebox.showinfo("Notice", "In order to change the setting "
                                                  "for auto identifying enemies in "
                                                  "CombatLogs, the parser must be "
                                                  "restarted.")
        self.conf.set("misc", "version", version)
        self.conf.set("parsing", "cl_path", cl_path)
        self.conf.set("parsing", "auto_ident", auto_ident)
        self.conf.set("sharing", "server_address", server_address)
        self.conf.set("sharing", "server_port", server_port)
        self.conf.set("sharing", "auto_upl", auto_upl)
        self.conf.set("realtime", "overlay", overlay)
        self.conf.set("realtime", "opacity", opacity)
        self.conf.set("realtime", "size", size)
        self.conf.set("realtime", "pos", pos)
        self.conf.set("realtime", "overlay_bg_color", bg_color)
        self.conf.set("realtime", "overlay_tx_color", tx_color)
        self.conf.set("realtime", "overlay_tr_color", tr_color)
        self.conf.set("realtime", "overlay_tx_font", tx_font)
        self.conf.set("realtime", "overlay_tx_size", tx_size)
        self.conf.set("realtime", "overlay_when_gsf", overlay_when_gsf)
        self.conf.set("realtime", "timeout", timeout)
        self.conf.set("realtime", "events_overlay", events_overlay)
        self.conf.set("realtime", "screenparsing", screenparsing)
        self.conf.set("realtime", "screenparsing_overlay", screenparsing_overlay)
        self.conf.set("realtime", "screenparsing_features", screenparsing_features)
        self.conf.set("gui", "color", color)
        self.conf.set("gui", "logo_color", logo_color)
        self.conf.set("gui", "event_colors", event_colors)
        self.conf.set("gui", "event_scheme", event_scheme)
        self.conf.set("gui", "date_format", date_format)
        self.conf.set("gui", "faction", faction)
        self.conf.set("misc", "autoupdate", autoupdate)
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)
        self.read_set()
        print("[DEBUG] Settings written")

    def write_settings_dict(self, settings_dict):
        """
        :param settings_dict: Dictonary of settings with {cat_set_tuple: value} with
                              cat_set_tuple as (section, setting)
        :return: None
        """
        for cat_set_tuple, value in list(settings_dict.items()):
            try:
                self.conf.set(cat_set_tuple[0], cat_set_tuple[1], value)
            except configparser.NoSectionError:
                tkinter.messagebox.showerror("Error", "This section does not exist: {0}".format(cat_set_tuple[0]))
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)

    def get_settings_dict(self):
        return self.conf


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
        except KeyError:
            tkinter.messagebox.showerror("Error", "The requested color for %s was not found, "
                                                  "did you alter the event_colors.ini file?" % key)
            return ['#ffffff', '#000000']
        except TypeError:
            tkinter.messagebox.showerror("Error", "The requested color for %s was could not be "
                                                  "type changed into a list. Did you alter the "
                                                  "event_colors.ini file?" % key)
            return ['#ffffff', '#000000']

    def set_scheme(self, name, custom_file=(os.path.join(utilities.get_temp_directory(), "events_colors.ini"))):
        if name == "default":
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
