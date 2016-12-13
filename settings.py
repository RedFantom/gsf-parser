# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import vars
import tkMessageBox
import frames
import gui
import parse
import stalking
import getpass
import os
import pickle

class defaults:
    version = "2.0.0_alpha"
    cl_path = 'C:/Users/' + getpass.getuser() + "/Documents/Star Wars - The Old Republic/CombatLogs"
    auto_ident = str(False)
    server = ("thrantasquadron.tk", 83)
    auto_upl = str(False)
    overlay = str(True)
    opacity = str(0.7)
    size = "big"
    pos = "TL"

class settings:
    def __init__(self, file_name = "settings.ini"):
        self.file_name = file_name
        vars.install_path = os.getcwd()
        if self.file_name not in os.listdir(vars.install_path):
            print "[DEBUG] Settings file could not be found. Creating a new file with default settings"
            self.settings_file_object = open(self.file_name, "w")
            self.write_def()
            self.settings_file_object.close()

    def read_set(self):
        settings_file_object = open(self.file_name, "r")
        settings_dict = pickle.load(settings_file_object)
        settings_file_object.close()
        self.version = settings_dict["version"]
        self.cl_path = settings_dict["cl_path"]
        self.auto_ident = settings_dict["auto_ident"]
        self.server = settings_dict["server"]
        self.auto_upl = settings_dict["auto_upl"]
        self.overlay = settings_dict["overlay"]
        self.opacity = settings_dict["opacity"]
        self.size = settings_dict["size"]
        self.pos = settings_dict["pos"]

    def write_def(self):
        settings_file = open(self.file_name, "w")
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
        pickle.dump(settings_dict, settings_file)
        settings_file.close()

    def write_set(self, version=defaults.version, cl_path=defaults.cl_path,
                  auto_ident=defaults.auto_ident, server=defaults.server,
                  auto_upl=defaults.auto_upl, overlay=defaults.overlay,
                  opacity=defaults.opacity, size=defaults.size, pos=defaults.pos):
        settings_file_object = open(self.file_name, "w")
        settings_dict = {"version":version,
                         "cl_path":cl_path,
                         "auto_ident":bool(auto_ident),
                         "server":server,
                         "auto_upl":bool(auto_upl),
                         "overlay":bool(overlay),
                         "opacity":float(opacity),
                         "size":size,
                         "pos":pos
                        }
        pickle.dump(settings_dict, settings_file_object)
        settings_file_object.close()
