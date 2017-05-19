# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from toplevels import cartelfix


class ToolsFrame(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.cartelfix_label = ttk.Label(self, text="Utility to show the right icon for the Cartel Gunships")
        self.cartelfix_faction = tk.StringVar()
        self.cartelfix_first = tk.StringVar()
        self.cartelfix_second = tk.StringVar()
        self.cartelfix_faction_dropdown = ttk.OptionMenu(self, self.cartelfix_faction, "Choose faction", "Imperial",
                                                         "Republic")
        self.cartelfix_first_dropdown = ttk.OptionMenu(self, self.cartelfix_first, "Choose railgun", "Slug Railgun",
                                                       "Ion Railgun", "Plasma Railgun")
        self.cartelfix_second_dropdown = ttk.OptionMenu(self, self.cartelfix_second, "Choos railgun", "Slug Railgun",
                                                        "Ion Railgun", "Plasma Railgun")
        self.cartelfix_button = ttk.Button(self, text="Open CartelFix", command=self.open_cartel_fix)

    def open_cartel_fix(self):
        pass

    @staticmethod
    def open_old_parser():
        exec(open("../tools/gsfparserv1.py").read())

    def grid_widgets(self):
        pass
