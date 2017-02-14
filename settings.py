# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkMessageBox
# General imports
import os
import ConfigParser
import tempfile
import collections
import ast


# Own modules
# import variables

# Class with default settings for in the settings file
class defaults:
    # Version to display in settings tab
    version = "2.2.1"
    # Path to get the CombatLogs from
    cl_path = os.path.expanduser("~") + \
              "\\Documents\\Star Wars - The Old Republic\\CombatLogs"
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
    color = "#236ab2"
    logo_color = "green"
    overlay_bg_color = "white"
    overlay_tr_color = "white"
    overlay_tx_color = "yellow"
    overlay_tx_font = "Calibri"
    overlay_tx_size = "12"
    overlay_when_gsf = str(False)
    event_colors = "basic"
    event_scheme = "default"
    date_format = "ymd"


# Class that loads, stores and saves settings
class settings:
    # Set the file_name for use by other functions
    def __init__(self, file_name="settings.ini",
                 directory=tempfile.gettempdir()):
        try:
            os.makedirs(directory.replace("\\temp", "") + "\\GSF Parser", True)
        except WindowsError:
            pass
        self.directory = directory.replace("\\temp", "") + "\\GSF Parser"
        self.file_name = directory.replace("\\temp", "") + \
                         "\\GSF Parser\\" + file_name
        self.conf = ConfigParser.RawConfigParser()
        # variables.install_path = os.getcwd()
        if file_name in os.listdir(self.directory):
            try:
                self.read_set()
            except ConfigParser.NoOptionError:
                self.write_def()
        else:
            self.write_def()
            self.read_set()
            # variables.path = self.cl_path

    # Read the settings from a file containing a pickle and store them as class variables
    def read_set(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.conf.read(self.file_name)
        self.version = self.conf.get("misc", "version")
        self.cl_path = self.conf.get("parsing", "cl_path")
        if self.conf.get("parsing", "auto_ident") == "True":
            self.auto_ident = True
        else:
            self.auto_ident = False
        self.server_address = self.conf.get("sharing", "server_address")
        self.server_port = int(self.conf.get("sharing", "server_port"))
        if self.conf.get("sharing", "auto_upl") == "True":
            self.auto_upl = True
        else:
            self.auto_upl = False
        if self.conf.get("realtime", "overlay") == "True":
            self.overlay = True
        else:
            self.overlay = False
        self.overlay_bg_color = self.conf.get("realtime", "overlay_bg_color")
        self.overlay_tr_color = self.conf.get("realtime", "overlay_tr_color")
        self.overlay_tx_color = self.conf.get("realtime", "overlay_tx_color")
        self.opacity = float(self.conf.get("realtime", "opacity"))
        self.size = self.conf.get("realtime", "size")
        self.pos = self.conf.get("realtime", "pos")
        self.color = self.conf.get("gui", "color")
        self.event_colors = self.conf.get("gui", "event_colors")
        self.event_scheme = self.conf.get("gui", "event_scheme")
        self.logo_color = self.conf.get("gui", "logo_color")
        self.date_format = self.conf.get("gui", "date_format")
        self.overlay_tx_font = self.conf.get("realtime", "overlay_tx_font")
        self.overlay_tx_size = self.conf.get("realtime", "overlay_tx_size")
        if self.conf.get("realtime", "overlay_when_gsf") == "True":
            self.overlay_when_gsf = True
        else:
            self.overlay_when_gsf = False
        print "[DEBUG] Settings read"
        try:
            os.chdir(self.cl_path)
        except WindowsError:
            tkMessageBox.showerror("Error", "An error occurred while changing "
                                            "the directory to the specified "
                                            "CombatLogs directory. Please "
                                            "check if this folder exists: %s"
                                   % self.cl_path)

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
        except:
            pass
        self.conf.set("misc", "version", defaults.version)
        self.conf.set("parsing", "cl_path", defaults.cl_path)
        self.conf.set("parsing", "auto_ident", defaults.auto_ident)
        self.conf.set("sharing", "server_address", defaults.server_address)
        self.conf.set("sharing", "server_port", defaults.server_port)
        self.conf.set("sharing", "auto_upl", defaults.auto_upl)
        self.conf.set("realtime", "overlay", defaults.overlay)
        self.conf.set("realtime", "opacity", defaults.opacity)
        self.conf.set("realtime", "size", defaults.size)
        self.conf.set("realtime", "pos", defaults.pos)
        self.conf.set("realtime", "overlay_bg_color", defaults.overlay_bg_color)
        self.conf.set("realtime", "overlay_tx_color", defaults.overlay_tx_color)
        self.conf.set("realtime", "overlay_tr_color", defaults.overlay_tr_color)
        self.conf.set("gui", "color", defaults.color)
        self.conf.set("gui", "logo_color", defaults.logo_color)
        self.conf.set("gui", "event_colors", defaults.event_colors)
        self.conf.set("gui", "event_scheme", defaults.event_scheme)
        self.conf.set("gui", "date_format", defaults.date_format)
        self.conf.set("realtime", "overlay_tx_font", defaults.overlay_tx_font)
        self.conf.set("realtime", "overlay_tx_size", defaults.overlay_tx_size)
        self.conf.set("realtime", "overlay_when_gsf", defaults.overlay_when_gsf)
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)
        print "[DEBUG] Defaults written"
        self.read_set()
        try:
            os.chdir(self.cl_path)
        except WindowsError:
            tkMessageBox.showerror("Error", "An error occurred while changing "
                                            "the directory to the specified "
                                            "CombatLogs directory. Please "
                                            "check if this folder exists: %s"
                                   % self.cl_path)

    # Write the settings passed as arguments to a pickle in a file
    # Setting defaults to default if not specified, so all settings are always
    # written
    def write_set(self, version=defaults.version,
                  cl_path=defaults.cl_path,
                  auto_ident=defaults.auto_ident,
                  server_address=defaults.server_address,
                  server_port=defaults.server_port,
                  auto_upl=defaults.auto_upl,
                  overlay=defaults.overlay,
                  opacity=defaults.opacity,
                  size=defaults.size,
                  pos=defaults.pos,
                  color=defaults.color,
                  logo_color=defaults.logo_color,
                  bg_color=defaults.overlay_bg_color,
                  tx_color=defaults.overlay_tx_color,
                  tr_color=defaults.overlay_tr_color,
                  tx_font=defaults.overlay_tx_font,
                  tx_size=defaults.overlay_tx_size,
                  overlay_when_gsf=defaults.overlay_when_gsf,
                  event_colors=defaults.event_colors,
                  event_scheme=defaults.event_scheme,
                  date_format=defaults.date_format):
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
            tkMessageBox.showinfo("Notice", "In order to change the setting for "
                                            "auto uploading CombatLogs, the "
                                            "parser must be restarted.")
        if str(auto_ident) != self.conf.get("parsing", "auto_ident"):
            tkMessageBox.showinfo("Notice", "In order to change the setting "
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
        self.conf.set("gui", "color", color)
        self.conf.set("gui", "logo_color", logo_color)
        self.conf.set("gui", "event_colors", event_colors)
        self.conf.set("gui", "event_scheme", event_scheme)
        self.conf.set("gui", "date_format", date_format)
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)
        self.read_set()
        print "[DEBUG] Settings written"
        try:
            os.chdir(self.cl_path)
        except WindowsError:
            tkMessageBox.showerror("Error", "An error occurred while changing "
                                            "the directory to the specified "
                                            "CombatLogs directory. Please "
                                            "check if this folder exists: %s"
                                   % self.cl_path)


class color_schemes:
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
            tkMessageBox.showerror("Error", "The requested color for %s was not found, " \
                                            "did you alter the event_colors.ini file?" % key)
            return ['#ffffff', '#000000']
        except TypeError:
            tkMessageBox.showerror("Error", "The requested color for %s was could not be " \
                                            "type changed into a list. Did you alter the " \
                                            "event_colors.ini file?" % key)
            return ['#ffffff', '#000000']

    def set_scheme(self, name, custom_file=tempfile.gettempdir().replace("temp", "GSF Parser") + "\\event_colors.ini"):
        if name == "default":
            self.current_scheme = self.default_colors
        elif name == "pastel":
            self.current_scheme = self.pastel_colors
        elif name == "custom":
            cp = ConfigParser.RawConfigParser()
            cp.read(custom_file)
            current_scheme = dict(cp.items("colors"))
            for key, value in current_scheme.iteritems():
                self.current_scheme[key] = ast.literal_eval(value)
        else:
            raise ValueError("Expected default, pastel or custom, got %s" % name)

    def write_custom(self, custom_file=tempfile.gettempdir().replace("temp", "GSF Parser") + "\\event_colors.ini"):
        cp = ConfigParser.RawConfigParser()
        try:
            cp.add_section("colors")
        except ConfigParser.DuplicateSectionError:
            pass
        for key, value in self.current_scheme.iteritems():
            cp.set('colors', key, value)
        with open(custom_file, "w") as file_obj:
            cp.write(file_obj)
