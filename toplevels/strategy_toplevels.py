# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Own modules
from parsing.strategies import StrategyDatabase, Strategy
from widgets.strategy_map import Map


class AddStrategy(tk.Toplevel):
    maps = {
        "Kuat Mesas DOM": ("dom", "km"),
        "Lost Shipyards DOM": ("dom", "ls"),
        "Denon Exosphere DOM": ("dom", "de"),
        "Kuat Mesas TDM": ("tdm", "km"),
        "Lost Shipyards TDM": ("tdm", "ls")
    }

    def __init__(self, *args, **kwargs):
        self.db = kwargs.pop("db", StrategyDatabase())
        self.callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        self.title("GSF Strategy Planner: Add Strategy")
        self.name_entry = ttk.Entry(self, width=28, font=("default", 11))
        self.name_entry.insert(0, "Strategy name...")
        self.name_entry.bind("<Button-1>", self.entry_callback)
        self.map = tk.StringVar()
        self.map_dropdown = ttk.OptionMenu(self, self.map, *("Select a map",
                                                             "Kuat Mesas DOM",
                                                             "Lost Shipyards DOM",
                                                             "Denon Exosphere DOM",
                                                             "Kuat Mesas TDM",
                                                             "Lost Shipyards TDM"))
        print(self.map_dropdown["style"])
        self.add_button = ttk.Button(self, text="Add", command=self.add)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.grid_widgets()

    def grid_widgets(self):
        self.name_entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.map_dropdown.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=5, pady=(0, 5))
        self.add_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.cancel_button.grid(row=2, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))

    def entry_callback(self, event):
        if self.name_entry.get() == "Strategy name...":
            self.name_entry.delete(0, tk.END)
        return

    def add(self):
        name = self.name_entry.get()
        print("Saving strategy {0}...".format(name))
        if name in self.db:
            messagebox.showinfo("Info", "Please select a name that is not yet in use.")
            return
        if self.map.get() not in self.maps:
            messagebox.showinfo("Info", "Please select a map.")
            return
        self.db[name] = Strategy(name, self.maps[self.map.get()])
        self.db.save_database()
        if callable(self.callback):
            self.callback()
        self.destroy()


class AddPhase(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add new phase")
        self._entry = ttk.Entry(self, width=30)
        self._entry.bind("<Return>", self.add_phase)
        self._cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self._add_button = ttk.Button(self, text="Add", command=self.add_phase)
        self.grid_widgets()

    def grid_widgets(self):
        self._entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self._cancel_button.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self._add_button.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)

    def add_phase(self, *args):
        if callable(self._callback):
            self._callback(self._entry.get())
        self.destroy()


class MapToplevel(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self.frame = kwargs.pop("frame")
        if not self.frame:
            raise ValueError("No parent frame passed as argument")
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.map = Map(self, moveitem_callback=self.move_item_phase,
                       additem_callback=self.add_item_to_phase, delitem_callback=self.del_item_phase,
                       canvaswidth=768, canvasheight=768)
        self.map.grid()
        self.frame.in_map = self.frame.map
        self.frame.in_map.set_readonly(True)
        self.frame.map = self.map
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)
        self.title("GSF Strategy Manager: Enlarged map")

    def move_item_phase(self, *args, **kwargs):
        self.frame.list.move_item_phase(*args, **kwargs)
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase])
        self.frame.list.tree.column("#0", width=150)
        self.frame.grid_widgets()

    def add_item_to_phase(self, *args, **kwargs):
        self.frame.list.add_item_to_phase(*args, **kwargs)
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase])
        self.frame.list.tree.column("#0", width=150)

    def del_item_phase(self, item, rectangle, text):
        print("Deleting item {0}".format(text))
        del self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase][text]
        self.frame.list.db.save_database()
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase])

    def close(self):
        self.frame.map = self.frame.in_map
        self.frame.map.set_readonly(False)
        self.frame.in_map = None
        self.destroy()
