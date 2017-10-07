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
        self.stats_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.stats_treeview = ttk.Treeview(self, show=("headings", "tree"), columns=("value",),
                                           yscrollcommand=self.stats_scrollbar.set)
        self.stats_scrollbar.config(command=self.stats_treeview.yview)
        self.stats_treeview.heading("#0", text="Statistic")
        self.stats_treeview.heading("value", text="Value")
        self.stats_treeview.column("value", anchor=tk.E, width=50)
        self.stats_treeview.column("#0", anchor=tk.W, width=350)
        self.stats_treeview.insert("", tk.END, iid="Ship", text="Ship statistics")
        self.stats_treeview.tag_configure("even", background="lightgrey")
        tags = ("even", )
        for item in sorted(stats.stats.keys()):
            if item.isdigit() or "OBSOLETE" in item:
                continue
            value = "{.0f}".format(round(stats.stats[item], 0))
            item = item.replace("_", " ")
            self.stats_treeview.insert("Ship", tk.END, iid=item, values=value, text=item, tags=tags)
            tags = ("odd", ) if tags == ("even", ) else ("even", )
        for component in stats.components:
            pass
        self.bind("<Configure>", self.configure)
        self.grid_widgets()

    def grid_widgets(self):
        self.stats_treeview.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)
        self.stats_scrollbar.grid(row=1, column=2, sticky="ns", padx=(0, 5), pady=5)

    def configure(self, *args):
        self.grid_widgets()

