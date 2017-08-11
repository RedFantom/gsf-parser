# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import tkinter as tk
from tkinter import ttk

from parsing.strategies import *
from toplevels.strategy_toplevels import AddStrategy, AddPhase


class StrategyList(ttk.Frame):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop("callback", None)
        self._settings_callback = kwargs.pop("settings_callback", None)
        self.client = None
        self.role = None
        ttk.Frame.__init__(self, *args, **kwargs)
        self.db = StrategyDatabase()
        self.phase = None
        self._flipped = False
        self._phase_menu = tk.Menu(self, tearoff=0)
        self._phase_menu.add_command(label="Rename", command=self.edit_phase)
        self._phase_menu.add_command(label="Delete", command=self.del_phase)
        self._strategy_menu = tk.Menu(self, tearoff=0)
        self._strategy_menu.add_command(label="Add phase", command=self.add_phase)
        self.tree = ttk.Treeview(self, height=7)
        self.scrollbar = ttk.Scrollbar(self, command=self.tree.yview, orient=tk.VERTICAL)
        self.tree.config(yscrollcommand=self.scrollbar.set)
        self.tree.bind("<Button-3>", self._right_click)
        self.tree.bind("<Double-1>", self._select)
        self.tree.heading("#0", text="Strategies")
        self.tree.column("#0", width=150)
        self.new_button = ttk.Button(self, text="New strategy", command=self.new_strategy)
        self.del_button = ttk.Button(self, text="Delete strategy", command=self.del_strategy)
        self.edit_button = ttk.Button(self, text="Edit strategy", command=self.edit_strategy, state=tk.DISABLED)
        self.settings_button = ttk.Button(self, text="Settings", command=self._settings_callback)
        self.show_large_button = ttk.Button(self, text="Show large", command=self.master.show_large)
        self.grid_widgets()

    def client_connected(self, client):
        print("Connected!")
        self.client = client
        self.role = client.role

    def grid_widgets(self):
        self.tree.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)
        self.new_button.grid(row=1, column=0, columnspan=2, sticky="nswe", pady=5, padx=5)
        self.del_button.grid(row=3, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.edit_button.grid(row=4, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.show_large_button.grid(row=5, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.settings_button.grid(row=6, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.update_tree()

    def add_item_to_phase(self, item, box, text, font, color):
        item_obj = Item(text, box[0], box[1], color, font)
        try:
            self.db[self.selected_strategy][self.selected_phase][text] = item_obj
        except KeyError:
            self.db[self.selected_strategy][self.phase][text] = item_obj
        self.db.save_database()

    def move_item_phase(self, text, x, y):
        self.db[self.selected_strategy][self.selected_phase][text]["x"] = x
        self.db[self.selected_strategy][self.selected_phase][text]["y"] = y
        self.db.save_database()

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        iterator = self.db
        for strategy, content in iterator:
            print("Found a strategy: ", strategy)
            self.tree.insert("", tk.END, iid=strategy, text=strategy)
            for phase in content:
                self.tree.insert(strategy, tk.END, iid=(content.name, "..", phase[0]), text=phase[0])

    def _right_click(self, event):
        selection = self.tree.selection()
        if len(selection) is 0:
            print("No item in the tree is selected")
            return
        value = selection[0]
        elements = value.split("..")
        if len(elements) is 1:
            self._strategy_menu.post(event.x_root, event.y_root)
        elif len(elements) is 2:
            self._phase_menu.post(event.x_root, event.y_root)
        else:
            raise ValueError("Invalid elements value found: ", elements)

    def _left_click(self, event):
        print("Left click")

    def sort_strategies(self):
        self._flipped = not self._flipped
        self.update_tree()

    def new_strategy(self):
        window = AddStrategy(db=self.db)
        window.wait_window()
        self.update_tree()

    def del_strategy(self):
        selection = self.tree.selection()
        print("Selection: ", selection)
        if len(selection) is 0:
            return
        selection = selection[0]
        print("Selection[0]: ", selection)
        if selection not in self.db.keys():
            print("Strategy not found in database: {0}".format(self.db.keys()))
            return
        del self.db[selection]
        self.update_tree()

    def add_phase(self):
        window = AddPhase(callback=self._new_phase)
        window.wait_window()

    def del_phase(self):
        del self.db[self.selected_strategy][self.selected_phase]
        self.db.save_database()
        self.update_tree()

    def edit_phase(self):
        pass

    def _new_phase(self, title):
        self.db[self.selection][title] = Phase(title, self.db[self.selected_strategy].map)
        self.update_tree()
        self.db.save_database()

    def edit_strategy(self):
        pass

    def _select(self, event):
        if self.selected_phase:
            self._phase_selected()
            if callable(self._callback):
                self._callback(self.selected_phase)
            self._phase = self.selected_phase
            self.master.description.delete("1.0", tk.END)
            self.master.description.insert("1.0", self.db[self.selected_strategy][self.selected_phase].description)
        else:
            if not self.selected_strategy:
                return
            self.master.description.delete("1.0", tk.END)
            self.master.description.insert("1.0", self.db[self.selected_strategy].description)
            self._strategy_selected()

    def _strategy_selected(self):
        self.new_button.config(text="New strategy", command=self.new_strategy)
        self.del_button.config(text="Delete strategy", command=self.del_strategy)
        self.edit_button.config(text="Add phase", command=self.add_phase, state=tk.NORMAL)

    def _phase_selected(self):
        # self.new_button.config(text="New strategy", state=tk.DISABLED)
        self.del_button.config(text="Delete phase", command=self.del_phase)
        self.edit_button.config(text="Edit phase", command=self.edit_phase, state=tk.DISABLED)

    @property
    def selection(self):
        selection = self.tree.selection()
        if len(selection) is 0:
            return None
        return selection[0]

    @property
    def selected_strategy(self):
        selection = self.selection
        if not selection:
            return None
        elements = selection.split("..")
        strategy = elements[0]
        strategy = strategy.strip()
        return strategy.replace("{", "").replace("}", "")

    @property
    def selected_phase(self):
        selection = self.selection
        if not selection:
            return None
        elements = selection.split("..")
        if len(elements) is not 2:
            return None
        phase = elements[1]
        if phase.startswith(" "):
            phase = phase[1:]
        if phase.endswith(" "):
            phase = phase[:1]
        return phase.replace("{", "").replace("}", "")
