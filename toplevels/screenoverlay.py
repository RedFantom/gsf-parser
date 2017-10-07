# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from widgets.overlay import Overlay
# Own modules
from tools.utilities import get_pointer_position_win32, get_screen_resolution
import variables


class HitChanceOverlay(object):
    def __init__(self, master):
        resolution = get_screen_resolution()
        x = int(round(resolution[0] / 1920 * 1200))
        y = int(round(resolution[1] / 1080 * 250))
        self.text = tk.StringVar()
        self.text.set("None")
        self.master = master
        self.overlay = Overlay((x, y), self.text, master=master, auto_init=False)
        self.running = True
        if variables.settings_obj["realtime"]["screenparsing_overlay_geometry"]:
            self.master.after(50, self.set_geometry)

    def set_geometry(self):
        (x, y) = get_pointer_position_win32()
        self.overlay.config(position=(x + 10, y + 10))
        self.master.after(30, self.set_geometry)

    def set_percentage(self, string):
        self.master.after(10, lambda: self.text.set(string))

    def destroy(self):
        self.overlay.destroy()
