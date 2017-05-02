# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
try:
    import mttkinter.mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
from parsing.vision import get_pointer_position_win32
import variables


class HitChanceOverlay(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.label = ttk.Label(self, foreground=variables.settings_obj.overlay_tx_color,
                               background=variables.settings_obj.overlay_bg_color)
        self.after(10, func=self.set_geometry)

    def grid_widgets(self):
        self.label.grid(sticky=tk.W)

    def set_geometry(self):
        (x, y) = get_pointer_position_win32()
        self.wm_geometry("%sx%s+%s+%s" % (self.label.winfo_reqheight(), self.label.winfo_reqwidth(), x, y))

    def set_percentage(self, string):
        self.label["text"] = string
