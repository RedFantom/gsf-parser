# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import tkinter as tk
from tkinter import ttk
from strategies.strategylist import StrategyList
from strategies.map import Map
from strategies.toplevels import SettingsToplevel
from strategies.toplevels import MapToplevel


class StrategyFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        # Create widgets
        self.list = StrategyList(self, callback=self._set_phase, settings_callback=self.open_settings)
        self.map = Map(self, moveitem_callback=self.list.move_item_phase, additem_callback=self.list.add_item_to_phase,
                       canvasheight=385, canvaswidth=385)
        self.in_map = self.map
        self.description_header = ttk.Label(self, text="Description", font=("default", 12), justify=tk.LEFT)
        self.description = tk.Text(self, width=20, height=23, wrap=tk.WORD)
        self.description.bind("<KeyPress>", self.set_description)
        self.description_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.description.yview)
        self.description.config(yscrollcommand=self.description_scroll.set)
        # Set up widgets
        self.grid_widgets()

    def open_settings(self, *args):
        settings = SettingsToplevel(master=self)
        settings.wait_window()

    def grid_widgets(self):
        # self.menu.grid(column=0, row=0, columnspan=2, sticky="nswe")
        self.list.grid(column=0, row=1, sticky="nswe", rowspan=2)
        self.map.grid(column=1, row=1, sticky="nswe", pady=5, rowspan=2)
        self.description_header.grid(column=2, columnspan=2, sticky="w", pady=(5, 0), padx=5, row=1)
        self.description.grid(column=2, row=2, sticky="nwe", padx=5, pady=(0, 5))
        self.description_scroll.grid(column=3, row=2, sticky="ns")

    def new_strategy(self):
        self.list.new_strategy()

    def _set_phase(self, phase):
        self.map.update_map(self.list.db[self.list.selected_strategy][phase])

    def set_description(self, *args):
        if self.list.selected_phase is not None:
            self.list.db[self.list.selected_strategy][self.list.selected_phase]. \
                description = self.description.get("1.0", tk.END)
            self.list.db.save_database()
        else:
            self.list.db[self.list.selected_strategy].description = self.description.get("1.0", tk.END)
            self.list.db.save_database()

    def show_large(self):
        window = MapToplevel(frame=self)
        if self.list.selected_phase is None:
            return
        window.map.update_map(self.list.db[self.list.selected_strategy][self.list.selected_phase])
