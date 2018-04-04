"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk, messagebox
# Project Modules
from parsing import StrategyDatabase, Strategy


class AddStrategy(tk.Toplevel):
    """
    Toplevel to allow the user to choose a name and map for the new
    Strategy the user wants to create. Also features a
    Cancel button to allow the user to cancel the action.
    """
    maps = {
        "Kuat Mesas DOM": ("dom", "km"),
        "Lost Shipyards DOM": ("dom", "ls"),
        "Denon Exosphere DOM": ("dom", "de"),
        "Kuat Mesas TDM": ("tdm", "km"),
        "Lost Shipyards TDM": ("tdm", "ls"),
        "Battle over Iokath TDM": ("tdm", "io")
    }

    def __init__(self, *args, **kwargs):
        """
        :param db: StrategyDatabase object to create the Strategy in
        :param callback: Function to call upon the creation of the Strategy
        """
        self.db = kwargs.pop("db", StrategyDatabase())
        self.callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        self.title("GSF Strategy Planner: Add Strategy")
        self.name_entry = ttk.Entry(self, width=28, font=("default", 11))
        self.name_entry.insert(0, "Strategy name...")
        # Bind left mouse button to self.entry_callback
        self.name_entry.bind("<Button-1>", self.entry_callback)
        self.map = tk.StringVar()
        self.map_dropdown = ttk.OptionMenu(self, self.map, *("Select a map",
                                                             "Kuat Mesas DOM",
                                                             "Lost Shipyards DOM",
                                                             "Denon Exosphere DOM",
                                                             "Kuat Mesas TDM",
                                                             "Lost Shipyards TDM"))
        self.add_button = ttk.Button(self, text="Add", command=self.add)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.grid_widgets()

    def grid_widgets(self):
        """The usual function to setup the geometry of the Toplevel"""
        self.name_entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.map_dropdown.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=5, pady=(0, 5))
        self.add_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.cancel_button.grid(row=2, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))

    def entry_callback(self, event):
        """
        Callback to remove the placeholder from the strategy name entry
        when clicked
        """
        if self.name_entry.get() == "Strategy name...":
            self.name_entry.delete(0, tk.END)
        return

    def add(self):
        """
        Function called by the Add-button to actually add the Strategy.
        Destroys the Toplevel after the Strategy is saved to the
        database.
        """
        name = self.name_entry.get()
        if not self.check_widgets():
            return
        print("Saving strategy {0}...".format(name))
        self.db[name] = Strategy(name, self.maps[self.map.get()])
        self.db.save_database()
        if callable(self.callback):
            self.callback()
        self.destroy()

    def check_widgets(self):
        """
        Performs checks on the widgets in order to check if the data
        the user entered was valid. If not, the user is shown an
        information message. Currently checks:
        - Strategy name exists in database
        - Strategy name does not contain invalid characters
        - Map entered is valid
        :return: True if data is valid, False if not
        """
        name = self.name_entry.get()
        if name in self.db:
            messagebox.showinfo("Info", "The name you have chosen for your Strategy is already in use. Please select a "
                                        "name that is not yet in use.")
            return False
        if "¤" in name or "³" in name or "_" in name or "`" in name or "~" in name or "€" in name:
            messagebox.showinfo("Info", "The name you have chosen for your Strategy contains invalid characters. A "
                                        "Strategy name may not contain the characters _, `, ~, ³, ¤ or €.")
            return False
        if self.map.get() not in self.maps:
            messagebox.showinfo("Info", "Please select a map.")
            return False
        return True