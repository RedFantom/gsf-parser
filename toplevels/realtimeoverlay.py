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
        self.unformatted_string = ("{dd:<20}{}\n{dt:<20}{}\n{hr:<20}{}\n{sd:<20}{}\n{en:<20}{}\n{sp:<20}{}".
                                   format(*(("{:>6}",) * 6), dd="Damage dealt:", dt="Damage taken:",
                                          hr="Healing received:", sd="Selfdamage:", en="Recent Enemies:", sp="Spawns:")
                                   if size == "big" else
                                   "DD: {}\nDT: {}\nHR: {}\nSD: {}")
        self.text_var = StringVar()
        # Determine required size
        text_size = variables.settings_obj["realtime"]["overlay_tx_size"]
        h_req = int((int(text_size) * 1.6) * (6 if size == "big" else 4))
        w_req = int(((int(text_size) / 0.9) + 2) * ((14 if size == "big" else 4) + 6))
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
        color = variables.settings_obj["realtime"]["overlay_tx_color"].lower()
        if color == "red":
            color_tuple = (255, 0, 0)
        elif color == "yellow":
            color_tuple = (255, 255, 0)
        elif color == "green":
            color_tuple = (0, 255, 0)
        elif color == "blue":
            color_tuple = (0, 255, 255)
        elif color == "white":
            color_tuple = (255, 255, 255)
        else:
            color_tuple = (255, 255, 0)
        opacity = int(variables.settings_obj["realtime"]["opacity"] * 255)
        self.overlay = Overlay(position, self.text_var, master=window, size=(w_req, h_req),
                               font={"family": "Courier New", "bold": True, "size": text_size, "italic": False},
                               color=color_tuple, opacity=opacity)

    def destroy(self):
        self.overlay.destroy()
