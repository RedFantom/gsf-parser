# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter.messagebox
from tkinter import StringVar
import os
import sys
# Own modules
from tools import utilities
from widgets.overlay import Overlay
import variables


class RealtimeOverlay(object):
    """
    Wrapper class around Overlay instance
    """
    def __init__(self, window):
        if sys.platform == "win32":
            try:
                with open(os.path.join(utilities.get_swtor_directory(), "swtor", "settings", "client_settings.ini"),
                          "r") as swtor:
                    if "D3DFullScreen = true" in swtor:
                        tkinter.messagebox.showerror("Error",
                                                     "The overlay cannot be shown with the current SWTOR settings. "
                                                     "Please set SWTOR to Fullscreen (windowed) in the Graphics "
                                                     "settings.")
            except IOError:
                tkinter.messagebox.showerror("Error",
                                             "The settings file for SWTOR cannot be found. Is SWTOR correctly "
                                             "installed?")
        size = variables.settings_obj["realtime"]["size"]
        self.unformatted_string = ("Damage done: {}\nDamage taken: {}\nHealing recv: {}\nSelfdamage: {}\n"
                                   "Recent enemies: {}\nSpawns: {}") if size == "big" else ("DD: {}\nDT: {}\nHR: {}\n"
                                                                                            "SD: {}")
        self.text_var = StringVar()
        # Determine required size
        text_size = variables.settings_obj["realtime"]["overlay_tx_size"]
        h_req = int((int(text_size) * 1.6) * (6 if size == "big" else 4))
        w_req = int(((int(text_size) / 1.5) + 2) * ((14 if size == "big" else 4) + 6))
        # Determine position
        position = variables.settings_obj["realtime"]["pos"]
        if position == "TL":
            position = (0, 0)
        elif position == "BL":
            position = (0, variables.screen_h - h_req)
        elif position == "TR":
            position = (variables.screen_w - w_req, 0)
        elif position == "BR":
            position = (variables.screen_w - w_req, variables.screen_h - h_req)
        elif position == "UC":
            position = (0, int(0.25 * variables.screen_h))
        elif position == "NQ":
            position = (int(variables.screen_w * 0.25), int(variables.screen_h) - int(h_req))
        elif position == "UT":
            position = (int(variables.screen_w) - int(w_req), variables.screen_h - int(0.75 * variables.screen_h))
        else:
            elements = position.split("+")
            position = (elements[1], elements[2])
        # Open the Overlay
        self.overlay = Overlay(position, self.text_var, master=window, size=(w_req, h_req))

    def destroy(self):
        self.overlay.destroy()
