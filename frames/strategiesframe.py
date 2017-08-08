# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from strategies.widgets import StrategyList, Map
from strategies.strategies import StrategyDatabase
from strategies.toplevels import SettingsToplevel
import _pickle as pickle


class StrategyFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        # Add menu bar and items
        self.menu = tk.Menu(self)
        # self.config(menu=self.menu)
        # File menu
        self.filemenu = tk.Menu(self, tearoff=False)
        self.filemenu.add_command(label="New", command=self.new_strategy)
        self.filemenu.add_command(label="Open", command=self.open_strategy)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save", command=self.save_strategy)
        self.filemenu.add_command(label="Save as", command=self.save_strategy_as)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.exit)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        # Edit menu
        self.editmenu = tk.Menu(self, tearoff=False)
        self.editmenu.add_command(label="Settings", command=self.open_settings)
        self.editmenu.add_command(label="Export database", command=self._export)
        self.editmenu.add_command(label="Import database", command=self._import)
        self.menu.add_cascade(label="Edit", menu=self.editmenu)
        # Create widgets
        self.list = StrategyList(self, callback=self._set_phase)
        self.map = Map(self, moveitem_callback=self.list.move_item_phase, additem_callback=self.list.add_item_to_phase)
        self.description_header = ttk.Label(self, text="Description", font=("default", 12), justify=tk.LEFT)
        self.description = tk.Text(self, width=20, height=23, wrap=tk.WORD)
        self.description.bind("<KeyPress>", self.set_description)
        self.description_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.description.yview)
        self.description.config(yscrollcommand=self.description_scroll.set)
        # Set up widgets
        self.grid_widgets()

    def show_menu(self, event):
        self.menu.post(event.x, event.y)

    def grid_widgets(self):
        # self.menu.grid(column=0, row=0, columnspan=2, sticky="nswe")
        self.list.grid(column=0, row=1, sticky="nswe", rowspan=2)
        self.map.grid(column=1, row=1, sticky="nswe", pady=5, rowspan=2)
        self.description_header.grid(column=2, columnspan=2, sticky="w", pady=(5, 0), padx=5, row=1)
        self.description.grid(column=2, row=2, sticky="nwe", padx=5, pady=(0, 5))
        self.description_scroll.grid(column=3, row=2, sticky="ns")

    def new_strategy(self):
        self.list.new_strategy()

    def open_strategy(self):
        file_name = filedialog.askopenfilename()
        with open(file_name, "rb") as fi:
            strategy = pickle.load(fi)
        self.list.db[strategy["name"]] = strategy
        self.list.update_tree()

    def save_strategy(self):
        self.save_strategy_as()

    def save_strategy_as(self):
        file_name = filedialog.asksaveasfilename()
        strategy = self.list.db[self.list.selected_strategy]
        with open(file_name, "wb") as fo:
            pickle.dump(strategy, fo)

    def save_strategy_database(self):
        self.list.db.save_database()

    def _import(self):
        file_name = filedialog.askopenfilename()
        self.list.db.merge_database(StrategyDatabase(file_name=file_name))
        self.list.update_tree()

    def _export(self):
        file_name = filedialog.asksaveasfilename()
        self.list.db.save_database_as(file_name)

    def open_settings(self):
        SettingsToplevel().wait_window()

    def _set_phase(self, phase):
        self.map.update_map(self.list.db[self.list.selected_strategy][phase])

    def exit(self):
        self.save_strategy_database()
        self.destroy()

    def set_description(self, *args):
        if self.list.selected_phase is not None:
            self.list.db[self.list.selected_strategy][self.list.selected_phase].\
                description = self.description.get("1.0", tk.END)
            self.list.db.save_database()
        else:
            self.list.db[self.list.selected_strategy].description = self.description.get("1.0", tk.END)
            self.list.db.save_database()
