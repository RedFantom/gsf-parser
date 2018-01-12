"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk


class AddCharacter(tk.Toplevel):
    def __init__(self, master, servers, callback):
        tk.Toplevel.__init__(self, master)
        self.character_name_entry = ttk.Entry(self, width=30)
        self.character_name_entry.insert(tk.END, "Character name...")
        self.legacy_name_entry = ttk.Entry(self)
        self.legacy_name_entry.insert(tk.END, "Legacy name...")
        self.server = tk.StringVar()
        servers = ("Choose network",) + servers
        self.callback = callback
        self.server_dropdown = ttk.OptionMenu(self, self.server, *servers)
        self.faction = tk.StringVar()
        self.faction_dropdown = ttk.OptionMenu(self, self.faction, *("Choose faction", "Republic", "Imperial"))
        self.done_button = ttk.Button(self, text="Add character", command=self.add_character)
        self.grid_widgets()

    def grid_widgets(self):
        self.character_name_entry.grid(row=0, column=0, sticky="we")
        self.legacy_name_entry.grid(row=1, column=0, sticky="we")
        self.server_dropdown.grid(row=2, column=0, sticky="we")
        self.faction_dropdown.grid(row=3, column=0, sticky="we")
        self.done_button.grid(row=4, column=0, sticky="we")

    def add_character(self):
        self.callback(self.character_name_entry.get(), self.legacy_name_entry.get(), self.server.get(),
                      self.faction.get())
        self.destroy()
