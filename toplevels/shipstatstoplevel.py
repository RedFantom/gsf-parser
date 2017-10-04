# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import os
import sys
# Own modules
from tools import utilities
from parsing.shipstats import ShipStats
import variables


class ShipStatsToplevel(tk.Toplevel):
    """
    A Toplevel that shows the statistics for a certain ship in an organized manner, categorized and in alphabetical
    order where applicable, in human readable format.
    """
    def __init__(self, master, ship, ships_data, companions_data):
        tk.Toplevel.__init__(self, master)
        stats = ShipStats(ship, ships_data, companions_data)
        self.stats_treeview = ttk.Treeview(self, show=("headings", "tree"), columns=("#0", "value"))
        self.stats_treeview.insert("", tk.END, iid="Ship", text="Ship statistics")
        for item in sorted(stats.stats.keys()):
            if item.isdigit() or "OBSOLETE" in item:
                continue
            value = stats.stats[item]
            item = item.replace("_", " ")
            self.stats_treeview.insert("Ship", tk.END, iid=item, values=value, text=item)
        for component in stats.components:
            pass
        self.bind("<Configure>", self.configure)
        self.grid_widgets()

    def grid_widgets(self):
        self.stats_treeview.grid()

    def configure(self, *args):
        self.grid_widgets()

