# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from ast import literal_eval as eval
import tkinter.ttk as ttk
from tools.utilities import get_pointer_position_win32, get_screen_resolution
import variables


class HitChanceOverlay(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.label = ttk.Label(self, foreground=variables.settings_obj["realtime"]["overlay_tx_color"],
                               background=variables.settings_obj["realtime"]["overlay_bg_color"], font=("Calibri", 16))
        self.configure(background=variables.settings_obj["realtime"]["overlay_bg_color"])
        self.wm_attributes("-transparentcolor", variables.settings_obj["realtime"]["overlay_tr_color"])
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", variables.settings_obj["realtime"]["opacity"])
        self.grid_widgets()
        if eval(variables.settings_obj["realtime"]["screenparsing_overlay_geometry"]):
            self.after(50, self.set_geometry)
        else:
            resolution = get_screen_resolution()
            x = int(round(resolution[0] / 1920 * 1200))
            y = int(round(resolution[1] / 1080 * 250))
            self.wm_geometry("{0}x{1}+{2}+{3}".format(120, 30, x, y))
        self.running = True

    def grid_widgets(self):
        self.label.grid(sticky="w")

    def set_geometry(self):
        (x, y) = get_pointer_position_win32()
        self.wm_geometry("%sx%s+%s+%s" % (120, 30, x + 10, y + 10))
        if self.running:
            self.after(50, self.set_geometry)
        else:
            self.destroy()

    def set_percentage(self, string):
        self.label["text"] = string
