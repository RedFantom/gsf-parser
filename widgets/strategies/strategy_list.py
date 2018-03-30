"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk
# Project Modules
from parsing.strategies import *
from toplevels.strategy_toplevels import AddStrategy, AddPhase


class StrategiesList(ttk.Frame):
    """
    Frame that shows the Strategies found in the StrategyDatabase in the default location in a Treeview list. Also
    provides buttons with various functions.
    """

    def __init__(self, *args, **kwargs):
        """
        :param callback: Callback to call when a Phase is selected (to allow StrategiesFrame to update the Map
        :param settings_callback: Callback to call when the user preses the settings_button
        """
        self._callback = kwargs.pop("callback", None)
        self._settings_callback = kwargs.pop("settings_callback", None)
        self._frame = kwargs.pop("frame", None)
        self.client = None
        self.role = None
        ttk.Frame.__init__(self, *args, **kwargs)
        self.db = StrategyDatabase()
        self.phase = None
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
        """
        Callback for when a Client is connected to a ClientHandler
        """
        print("Connected!")
        self.client = client
        self.role = client.role

    def grid_widgets(self):
        """
        The usual function for gridding the widgets


        _______________________________
        | Treeview                    |
        |                             |
        | + Strategy                  |
        |      Phase                  |
        |                             |
        | new_button                  |
        | del_button                  |
        | edit_button                 |
        | show_large_button           |
        | settings_button             |
        -------------------------------
        """
        self.tree.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)
        self.new_button.grid(row=1, column=0, columnspan=2, sticky="nswe", pady=5, padx=5)
        self.del_button.grid(row=3, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.edit_button.grid(row=4, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.show_large_button.grid(row=5, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.settings_button.grid(row=6, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.update_tree()

    def add_item_to_phase(self, item, box, text, font, color):
        """
        Callback to add an item to the currently selected Phase
        :param item: item name
        :param box: (x, y) coordinates
        :param text: item text
        :param font: item font tuple
        :param color: item color hex value
        :return: None
        """
        item_obj = Item(text, box[0], box[1], color, font)
        if self.selected_phase:
            self.db[self.selected_strategy][self.selected_phase][text] = item_obj
        elif self.phase:
            self.db[self.selected_strategy][self.phase][text] = item_obj
        else:
            return
        self.db.save_database()

    def move_item_phase(self, text, x, y):
        """
        Callback to update the location of an item in the database
        :param text: item name
        :param x: item x coordinate
        :param y: item y coordinate
        :return: None
        """
        if self.selected_phase:
            self.db[self.selected_strategy][self.selected_phase][text]["x"] = x
            self.db[self.selected_strategy][self.selected_phase][text]["y"] = y
        elif self.phase:
            self.db[self.selected_strategy][self.phase][text]["x"] = x
            self.db[self.selected_strategy][self.phase][text]["y"] = y
        else:
            return
        self.db.save_database()

    def update_tree(self):
        """
        Function to update the contents of the Treeview with the Strategies and Phases found in the StrategyDatabase
        """
        self.tree.delete(*self.tree.get_children())
        iterator = self.db
        for strategy, content in iterator:
            self.tree.insert("", tk.END, iid=strategy, text=strategy)
            for phase in content:
                self.tree.insert(strategy, tk.END, iid=(content.name, "..", phase[0]), text=phase[0])
        if (self._frame is not None and hasattr(self._frame, "settings") and self._frame.settings is not None and
                self._frame.settings.share_toplevel is not None):
            self._frame.settings.share_toplevel.update_strategy_tree()

    def _right_click(self, event):
        """
        Callback for the Tkinter Button-3 event, shows the strategy menu
        """
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
        """
        Callback for Button-1 Tkinter event so the user does not have to double-click on phases
        """
        if self.selected_phase:
            self.phase = self.selected_phase
            self._callback(self.selected_phase)
        return

    def new_strategy(self):
        """
        Callback for the new strategy button to open an AddStrategy Toplevel
        """
        window = AddStrategy(db=self.db)
        window.wait_window()
        self.update_tree()

    def del_strategy(self):
        """
        Callback for the delete strategy button
        """
        selection = self.tree.selection()
        if len(selection) is 0:
            return
        selection = selection[0]
        if selection not in self.db.keys():
            return
        del self.db[selection]
        self.update_tree()

    def add_phase(self):
        """
        Callback for the add phase button
        """
        window = AddPhase(callback=self._new_phase)
        window.wait_window()

    def del_phase(self):
        """
        Callback for the del phase button
        """
        del self.db[self.selected_strategy][self.selected_phase]
        self.db.save_database()
        self.update_tree()

    def edit_phase(self):
        """
        Callback for the edit phase button
        """
        # TODO: Implement phase name changing
        pass

    def _new_phase(self, title):
        """
        Callback for the AddPhase Toplevel to create a new phase in the database
        """
        self.db[self.selection][title] = Phase(title, self.db[self.selected_strategy].map)
        self.update_tree()
        self.db.save_database()

    def edit_strategy(self):
        """
        Callback for the edit strategy button
        """
        # TODO: Implement name and map changing for Strategy
        pass

    def _select(self, event):
        """
        Callback for a double-click event to select an item from the Treeview
        """
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
        """
        Function to update widgets when a Strategy is selected
        """
        self.new_button.config(text="New strategy", command=self.new_strategy)
        self.del_button.config(text="Delete strategy", command=self.del_strategy)
        self.edit_button.config(text="Add phase", command=self.add_phase, state=tk.NORMAL)

    def _phase_selected(self):
        """
        Function to update widgets when a Phase is selected
        """
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
