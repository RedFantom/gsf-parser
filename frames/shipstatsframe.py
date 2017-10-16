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

        # Create main menu objects
        self.main_menu = tk.Menu(self, tearoff=False)
        self.file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.stats_menu = tk.Menu(self.main_menu, tearoff=False)
        self.ttk_menu = tk.Menu(self.main_menu, tearoff=False)
        self.excel_menu = tk.Menu(self.main_menu, tearoff=False)
        self.setup_menu()

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

    def setup_menu(self):
        """
        Sets up the menu of the window
        """
        # Setup the File menu
        self.file_menu.add_command(label="Export", command=self.export_ship)
        self.file_menu.add_command(label="Import", command=self.import_ship)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close", command=self.destroy)
        # Setup the stats menu
        self.stats_menu.add_command(label="Distance travelled", command=lambda: self.calculate_stat("distance"))
        # Setup the TTK menu
        self.ttk_menu.add_command(label="TTK against self", command=lambda: self.calculate_stat("ttk_self"))
        self.ttk_menu.add_command(label="TTK against target", command=lambda: self.calculate_stat("ttk_target"))
        self.stats_menu.add_cascade(label="Time-to-kill", menu=self.ttk_menu)
        # Setup the Excel menu
        pass
        # Add the menus to the main_menu
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.main_menu.add_cascade(label="Stats", menu=self.stats_menu)
        # Add the menu to the window
        # self.config(menu=self.main_menu)

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
    def format_value(key, value):
        pass

    def configure(self, *args):
        pass

    def export_ship(self):
        pass

    def import_ship(self):
        pass

    def calculate_stat(self, stat):
        pass


class StatsCalculationToplevel(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
