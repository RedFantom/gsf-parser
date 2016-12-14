# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import tkMessageBox
# General imports
import getpass
import os
import cPickle
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
    server = ("thrantasquadron.tk", 83)
    # Automatically upload CombatLogs as they are parsed to the remote server
    auto_upl = str(False)
    # Enable the overlay
    overlay = str(True)
    # Set the overlay opacity, or transparency
    opacity = str(0.7)
    # Set the overlay size
    size = "big"
    # Set the corner the overlay will be displayed in
    pos = "TL"


# Class that loads, stores and saves settings
class settings:
    # Set the file_name for use by other functions
    def __init__(self, file_name = "settings.ini"):
        self.file_name = file_name
        # Set the install path in the vars module
        vars.install_path = os.getcwd()
        # Check for the existence of the specified settings_file
        if self.file_name not in os.listdir(vars.install_path):
            print "[DEBUG] Settings file could not be found. Creating a new file with default settings"
            self.write_def()
        else:
            try:
                self.read_set()
            except:
                tkMessageBox.showerror("Error", "Settings file available, but it could not be read. Writing defaults.")
                self.write_def()

    # Read the settings from a file containing a pickle and store them as class variables
    def read_set(self):
        with open(self.file_name, "r") as settings_file_object:
            settings_dict = cPickle.load(settings_file_object)
        self.version = settings_dict["version"]
        self.cl_path = settings_dict["cl_path"]
        self.auto_ident = settings_dict["auto_ident"]
        self.server = settings_dict["server"]
        self.auto_upl = settings_dict["auto_upl"]
        self.overlay = settings_dict["overlay"]
        self.opacity = settings_dict["opacity"]
        self.size = settings_dict["size"]
        self.pos = settings_dict["pos"]

    # Write the defaults settings found in the class defaults to a pickle in a file
    def write_def(self):
        settings_dict = {"version":defaults.version,
                         "cl_path":defaults.cl_path,
                         "auto_ident":bool(defaults.auto_ident),
                         "server":defaults.server,
                         "auto_upl":bool(defaults.auto_upl),
                         "overlay":bool(defaults.overlay),
                         "opacity":float(defaults.opacity),
                         "size":defaults.size,
                         "pos":defaults.pos
                        }
        with open(self.file_name, "w") as settings_file:
            cPickle.dump(settings_dict, settings_file)

    # Write the settings passed as arguments to a pickle in a file
    # Setting defaults to default if not specified, so all settings are always written
    def write_set(self, version=defaults.version, cl_path=defaults.cl_path,
                  auto_ident=defaults.auto_ident, server=defaults.server,
                  auto_upl=defaults.auto_upl, overlay=defaults.overlay,
                  opacity=defaults.opacity, size=defaults.size, pos=defaults.pos):
        settings_dict = {"version":version,
                         "cl_path":cl_path,
                         "auto_ident":bool(auto_ident),
                         "server":server,
                         "auto_upl":bool(auto_upl),
                         "overlay":bool(overlay),
                         "opacity":float(opacity),
                         "size":str(size),
                         "pos":pos
                        }
        with open(self.file_name, "w") as settings_file_object:
            cPickle.dump(settings_dict, settings_file_object)
        self.read_set()
