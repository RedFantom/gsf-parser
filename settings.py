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
            self.write_def()

    def read_set(self):
        self.file = open("settings.ini", "r")
        for line in self.file:
            if "#" not in line:
                items = line.replace("\n", "").split("=")
                print items
                if len(items) != 2:
                    print "[DEBUG] Fatal error while reading settings file!"
                    return
                if items[0] == "version":
                    self.version = items[1]
                elif items[0] == "cl_path":
                    self.cl_path = items[1]
                elif items[0] == "auto_ident":
                    try:
                        self.auto_ident = bool(items[1])
                    except:
                        print "[DEBUG] Non-fatal error while converting auto_ident to bool: " + items[1]
                        tkMessageBox.showinfo("Error", "The value of auto_ident in the settings file could not be converted to a boolean. Continuing with default value.")
                        self.auto_ident = bool(defaults.auto_ident)
                elif items[0] == "server":
                    address = items[1].split(":")
                    if len(address) != 2:
                        print "[DEBUG] Non-fatal error: server does not consist of two items."
                        tkMessageBox.showinfo("Error", "The value of server in the settings file is not valid. Continuing with default value.")
                        self.server = defaults.server
                    else:
                        try:
                            self.server = (address[0], int(address[1]))
                        except:
                            print "[DEBUG] Fatal error: port cannnot be converter to int."
                            tkMessageBox.showerror("Fatal error", "The port value of the server in the settings file is not an integer.")
                            return
                elif items[0] == "auto_upl":
                    try:
                        self.auto_upl = bool(items[1])
                    except:
                        print "[DEBUG] Non-fatal error while converting auto_upl to bool: " + items[1]
                        tkmessageBox.showinfo("Error", "The value of auto_upl in the settings file could not converted to a boolean. Continuing with default value.")
                        self.auto_upl = bool(defaults.auto_upl)
                elif items[0] == "overlay":
                    try:
                        self.overlay = bool(items[1])
                    except:
                        print "[DEBUG] Non-fatal error while converting overlay to bool: " + items[1]
                        tkmessageBox.showinfo("Error", "The value of overlay in the settings file could not converted to a boolean. Continuing with default value.")
                        self.overlay = bool(defaults.overlay)
                elif items[0] == "opacity":
                    try:
                        self.opacity = float(items[1])
                    except:
                        print "[DEBUG] non-fatal error while converting opacity to int: " + items[1]
                        tkMessageBox.showinfo("Error", "The value of opacity in the settings file could not converted to a float. Continuing with default value.")
                        self.opacity = float(defaults.opacity)
                elif items[0] == "size":
                    if (items[1] != "big" and items[1] != "small"):
                        print "[DEBUG] Non-fatal error: the value of size is not big or small: " + items[1]
                        tkMessageBox.showinfo("Error", "The value of size in the settings file is neither 'big' nor 'small'. Continuing with default value.")
                        self.size = defaults.size
                    else:
                        self.size = items[1]
                elif items[0] == "pos":
                    if(items[1] != "TL" and items[1] != "BL" and items[1] != "TR" and items[1] != "BR"):
                        print "[DEBUG] Non-fatal error: pos is not a valid value: " + items[1]
                        tkMessageBox.showinfo("Error", "The value of pos in the settings file is invalid. Continuing with default value.")
                        self.pos = defaults.pos
                    else:
                        self.pos = items[1]
                else:
                    print "[DEBUG] Invalid setting found! Fatal error."
                    tkMessageBox.showerror("Fatal error", "An invalid setting was found in the settings file.")
                    return
        self.file.close()
        return

    def write_def(self):
        self.file = open(self.file_name, "w")
        self.file.write("# MUST be first setting\n")
        self.file.write("version=" + defaults.version + "\n")
        self.file.write("# Default path for the CombatLogs\n")
        self.file.write("cl_path=" + defaults.cl_path + "\n")
        self.file.write("# Automatically upload your player ID's to the specified server\n")
        self.file.write("# And identify players in the parser\n")
        self.file.write("auto_ident=" + defaults.auto_ident + "\n")
        self.file.write("# Server address and port\n")
        self.file.write("server=" + defaults.server[0] + ":" + str(defaults.server[1]) + "\n")
        self.file.write("# Auto-upload parsed CombatLogs to the server\n")
        self.file.write("auto_upl=" + defaults.auto_upl + "\n")
        self.file.write("# Enable the overlay for parsing\n")
        self.file.write("overlay=" + defaults.overlay + "\n")
        self.file.write("# Set the overlay opacity\n")
        self.file.write("opacity=" + defaults.opacity + "\n")
        self.file.write("# Set the overlay size\n")
        self.file.write("size=" + defaults.size + "\n")
        self.file.write("# Set the overlay position on the screen\n")
        self.file.write("pos=" + defaults.pos + "\n")
        self.file.close()
        return

    def write_set(self, version=defaults.version, cl_path=defaults.cl_path,
                  auto_ident=defaults.auto_ident, server=defaults.server,
                  auto_upl=defaults.auto_upl, overlay=defaults.overlay,
                  opacity=defaults.opacity, size=defaults.size, pos=defaults.pos):
        self.file.seek(0)
        print "[DEBUG] Writing defaults"
        self.file.write("# MUST be first setting")
        self.file.write("version=" + version + "")
        self.file.write("# Default path for the CombatLogs")
        self.file.write("cl_path=" + cl_path + "")
        self.file.write("# Automatically upload your player ID's to the specified server")
        self.file.write("auto_ident=" + auto_ident + "")
        self.file.write("# Server address and port")
        self.file.write("server=" + server + "")
        self.file.write("# Auto-upload parsed CombagLogs to the server")
        self.file.write("auto_upl=" + auto_upl + "")
        self.file.write("# Enable the overlay for parsing")
        self.file.write("overlay=" + overlay + "")
        self.file.write("# Set the overlay opacity")
        self.file.write("opacity=" + opacity + "")
        self.file.write("# Set the overlay size")
        self.file.write("size=" + size + "")
        self.file.write("# Set the overlay position on the screen")
        self.file.write("pos=" + pos + "")
        self.file.close()
        self.read_set()

    def __exit__(self):
        self.file.close()
