"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
# General imports
import textwrap
# Own modules
from parsing.shipstats import ShipStats
from parsing.ships import component_types_list, component_strings
from data.statistics import categories as statistic_categories, statistics as statistic_strings
from data.statistics import weapon_categories as weapon_statistic_categories


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
        self.tags = {}
        self.tags.update({key: "odd" for key in statistic_categories})
        self.tags.update({key: "odd" for key in weapon_statistic_categories})

        # Create the Treeview and its scrollbar
        self.stats_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.stats_treeview = ttk.Treeview(self, show=("headings", "tree"), columns=("value",),
                                           yscrollcommand=self.stats_scrollbar.set, height=16)
        self.stats_scrollbar.config(command=self.stats_treeview.yview)
        self.setup_treeview()

        self.update_tree()
        self.grid_widgets()

    def update_tree(self):
        """
        Update the Treeview with the data in the ShipStats instance
        """
        self.stats_treeview.delete(*self.stats_treeview.get_children())
        # First insert the header items for Ship statistics
        self.stats_treeview.insert("", tk.END, iid="Ship", tags=("category",), text="Ship")
        for category in statistic_categories:
            self.stats_treeview.insert(
                "Ship", tk.END, tags=("stat_category",), text=category.replace("_", " "), iid="Ship_{}".format(category)
            )
        # Insert the Ship statistics themselves
        for statistic, value in sorted(self.stats["Ship"].items()):
            if statistic not in statistic_strings:
                continue
            self.insert_into_treeview("Ship", statistic, value)
        # Loop over the other categories to insert the other statistics
        for category in component_types_list:
            # Skip any categories that are not in the ShipStats object
            if category not in self.stats:
                continue
            # Empty categories should not be inserted
            stats = self.stats[category].items()
            if stats is None or len(stats) == 0:
                continue
            # Insert the header for the category
            self.stats_treeview.insert(
                "", tk.END, iid=category, tags=("category",),
                text=component_strings[category] if category in component_strings else category
            )
            # insert the headers for the subcategories
            for subcategory in weapon_statistic_categories:
                self.stats_treeview.insert(
                    category, tk.END, iid="{}_{}".format(category, subcategory),
                    tags=("stat_category",), text=subcategory
                )
            for statistic, value in sorted(stats):
                self.insert_into_treeview(category, statistic, value)
            for subcategory in weapon_statistic_categories:
                item = "{}_{}".format(category, subcategory)
                amount = len(self.stats_treeview.get_children(item))
                if amount == 0:
                    self.stats_treeview.delete(item)
        return

    def insert_into_treeview(self, category, statistic, value):
        """
        Insert a statistic into the treeview. Parent categories should already be in place.
        """
        if statistic not in statistic_strings:
            print("Skipping insertion of {}".format(statistic))
            return
        subcategory = statistic_strings[statistic][0]
        if category == "Ship" and subcategory not in statistic_categories:
            return
        tag = self.tags[subcategory]
        value_string = ShipStatsFrame.get_value_string(statistic, value)
        elements = textwrap.fill(statistic_strings[statistic][1], 25).split("\n")
        for index, element in enumerate(elements):
            parent = "{}_{}".format(category, subcategory)
            if parent not in self.stats_treeview.get_children(category):
                continue
            self.stats_treeview.insert(
                parent, tk.END, tags=(tag,), text=element,
                values=("",) if index != 0 else (value_string,)
            )
        self.tags[subcategory] = "even" if self.tags[subcategory] == "odd" else "odd"

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
        self.stats_treeview.column("value", anchor=tk.E, width=55)
        self.stats_treeview.column("#0", anchor=tk.W, width=205)
        self.stats_treeview.tag_configure("category", background="gray90", font=("default", 12, "bold"))
        self.stats_treeview.tag_configure("stat_category", background="gray85", font=("default", 11, "italic"))
        self.stats_treeview.tag_configure("even", background="gray80")

    @staticmethod
    def get_value_string(statistic, value):
        """
        Get a nicely formatted string to insert into the value column of the Treeview based on the unit
        """
        category, string, unit = statistic_strings[statistic]
        if "%" in unit:
            value_string = "{:.1f}{}".format(value * 100, unit)
        elif unit == "bool":
            value_string = "False" if value == 0.0 else "True"
        elif unit == "p":
            value_string = "{:.0f} {}".format(value, unit)
        elif "m/s" in unit:
            value_string = "{:.1f} {}".format(value * 10, unit)
        elif unit == "m":
            value_string = "{} {}".format(value * 100, unit)
        else:
            value_string = "{:.1f} {}".format(value, unit)
        return textwrap.fill(value_string, 25)
