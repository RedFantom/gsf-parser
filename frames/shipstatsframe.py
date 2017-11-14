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
from parsing.ships import component_types_list, component_strings
import variables


class ShipStatsFrame(ttk.Frame):
    """
    A Toplevel that shows the statistics for a certain ship in an organized manner, categorized and in alphabetical
    order where applicable, in human readable format.
    """

    def __init__(self, master, ship, ships_data, companions_data):
        """
        :param master: MainWindow
        :param ship: Ship instance to calculate statistics for
        :param ships_data: Ships data dictionary (ships.db)
        :param companions_data: Companions data dictionary (companions.db)
        """
        ttk.Frame.__init__(self, master)
        self.stats = ShipStats(ship, ships_data, companions_data)

        # Create the Treeview and its scrollbar
        self.stats_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.stats_treeview = ttk.Treeview(self, show=("headings", "tree"), columns=("value",),
                                           yscrollcommand=self.stats_scrollbar.set, height=16)
        self.stats_scrollbar.config(command=self.stats_treeview.yview)
        self.setup_treeview()

        self.bind("<Configure>", self.configure)
        self.update_tree()
        self.grid_widgets()

    def update_tree(self):
        """
        Update the Treeview with the data in the ShipStats instance
        """
        self.stats_treeview.delete(*self.stats_treeview.get_children())
        self.stats_treeview.insert("", tk.END, iid="Ship", text="Ship statistics", tags=("category",))
        tags = ("even",)
        for item in sorted(self.stats.stats.keys()):
            if item.isdigit() or "OBSOLETE" in item:
                continue
            value = self.stats.stats[item]
            # value = value * 100 if value <= 2 else value
            value = "{:.2f}".format(value)
            item = item.replace("_", " ")
            self.stats_treeview.insert("Ship", tk.END, iid=item, values=value, text=item, tags=tags)
            tags = ("odd",) if tags == ("even",) else ("even",)
        for component in component_types_list:
            if component not in self.stats.components:
                continue
            print("Component: {}, {}".format(component, self.stats.components[component]))
            string = component_strings[component] if component in component_strings else component
            self.stats_treeview.insert("", tk.END, iid=component, text=string, tags=("category",))
            for key in sorted(self.stats.components[component].keys()):
                print("Processing component stat {}".format(key))
                if "OBSOLETE" in key or "[Pc]" in key:
                    continue
                value = "{:.2f}".format(self.stats.components[component][key])
                key = key.replace("_", " ")
                self.stats_treeview.insert(component, tk.END, iid="{}_{}".format(component, key), text=key, tags=tags,
                                           values=value)
                tags = ("odd",) if tags == ("even",) else ("even",)

    def grid_widgets(self):
        self.stats_treeview.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)
        self.stats_scrollbar.grid(row=1, column=2, sticky="ns", padx=(0, 5), pady=5)

    def grid_widgets_forget(self):
        self.stats_treeview.grid_forget()
        self.stats_scrollbar.grid_forget()

    def setup_treeview(self):
        """
        Sets up the Treeview with columns and headings
        """
        self.stats_treeview.heading("#0", text="Statistic")
        self.stats_treeview.heading("value", text="Value")
        self.stats_treeview.column("value", anchor=tk.E, width=40)
        self.stats_treeview.column("#0", anchor=tk.W, width=220)
        self.stats_treeview.tag_configure("category", background="grey90", font=("default", 12, "bold"))
        self.stats_treeview.tag_configure("even", background="gray80")

    @staticmethod
