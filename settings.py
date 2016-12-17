# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import tkMessageBox
# General imports
import getpass
import os
import ConfigParser
# Own modules
import vars

# Class with default settings for in the settings file
class defaults:
    # Version to display in settings tab
    version = "2.0.0_alpha"
    # Path to get the CombatLogs from
    cl_path = 'C:/Users/' + getpass.getuser() + "/Documents/Star Wars - The Old Republic/CombatLogs"
    # Automatically send and retrieve names and hashes of ID numbers from the remote server
    auto_ident = str(False)
    # Address and port of the remote server
    server_address = "thrantasquadron.tk"
    server_port = 83
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
    # Set the defaults style
    style = "plastik"

# Class that loads, stores and saves settings
class settings:
    # Set the file_name for use by other functions
    def __init__(self, file_name = "settings.ini"):
        self.file_name = file_name
        # Set the install path in the vars module
        vars.install_path = os.getcwd()
        self.conf = ConfigParser.RawConfigParser()
        if self.file_name in os.listdir(vars.install_path):
            self.read_set()
        else:
            self.write_def()
            self.read_set()
        vars.path = self.cl_path

    # Read the settings from a file containing a pickle and store them as class variables
    def read_set(self):
        self.conf.read(self.file_name)
        self.version = self.conf.get("misc", "version")
        self.cl_path = self.conf.get("parsing", "cl_path")
        self.auto_ident = self.conf.get("parsing", "auto_ident")
        self.server_address = self.conf.get("sharing", "server_address")
        self.server_port = self.conf.get("sharing", "server_port")
        self.auto_upl = self.conf.get("sharing", "auto_upl")
        self.overlay = self.conf.get("realtime", "overlay")
        self.opacity = self.conf.get("realtime", "opacity")
        self.size = self.conf.get("realtime", "size")
        self.pos = self.conf.get("realtime", "pos")
        self.style = self.conf.get("gui", "style")
        print "[DEBUG] self.pos: ", self.pos
        print "[DEBUG] Settings read"

    # Write the defaults settings found in the class defaults to a pickle in a file
    def write_def(self):
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
        self.conf.set("gui", "style", defaults.style)
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)
        print "[DEBUG] Defaults written"

        # Write the settings passed as arguments to a pickle in a file
    # Setting defaults to default if not specified, so all settings are always written
    def write_set(self, version=defaults.version, cl_path=defaults.cl_path,
                  auto_ident=defaults.auto_ident, server_address=defaults.server_address,
                  server_port=defaults.server_port,
                  auto_upl=defaults.auto_upl, overlay=defaults.overlay,
                  opacity=defaults.opacity, size=defaults.size, pos=defaults.pos,
                  style=defaults.style):
        try:
            self.conf.add_section("misc")
            self.conf.add_section("parsing")
            self.conf.add_section("sharing")
            self.conf.add_section("realtime")
            self.conf.add_section("gui")
        except:
            pass
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
        self.conf.set("gui", "style", style)
        with open(self.file_name, "w") as settings_file_object:
            self.conf.write(settings_file_object)
        self.read_set()
        print "[DEBUG] Settings written"
