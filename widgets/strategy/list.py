"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
# Project Modules
from parsing.strategies import *
from toplevels.strategy.add_phase import AddPhase
from toplevels.strategy.add_strategy import AddStrategy
from network.strategy.client import StrategyClient


class StrategiesList(ttk.Frame):
    """
    Frame that shows the Strategies found in the StrategyDatabase in
    the default location in a Treeview list. Also provides buttons with
    to manipulate the Strategies in the StrategyDatabase.
    """

    def __init__(self, *args, **kwargs):
        """
        :param callback: Callback to call when a Phase is selected (to
            allow StrategiesFrame to update the Map)
        :param settings_callback: Callback to call when the user presses
            the settings_button
        """
        # Arguments and Attributes
        self._callback = kwargs.pop("callback", None)
        self._settings_callback = kwargs.pop("settings_callback", None)
        self._frame = kwargs.pop("frame", None)
        self.client = None
        self.role = None
        self.db = StrategyDatabase()
        self.phase = None

        ttk.Frame.__init__(self, *args, **kwargs)

        """Widget Creation"""
        self._phase_menu = tk.Menu(self, tearoff=False)
        self._strategy_menu = tk.Menu(self, tearoff=False)
        self.tree = ttk.Treeview(self, height=7)
        self.scrollbar = ttk.Scrollbar(self, command=self.tree.yview, orient=tk.VERTICAL)
        self.new_button = ttk.Button(self, text="New strategy", command=self.new_strategy)
        self.del_button = ttk.Button(self, text="Delete strategy", command=self.del_strategy)
        self.edit_button = ttk.Button(self, text="Edit strategy", command=self.edit_strategy, state=tk.DISABLED)
        self.settings_button = ttk.Button(self, text="Settings", command=self._settings_callback)
        self.show_large_button = ttk.Button(self, text="Show large", command=self.master.show_large)

        self.setup_menus()
        self.setup_treeview()
        self.grid_widgets()

    def setup_menus(self):
        """Configure the various menus with their commands"""
        self._strategy_menu.add_command(label="Add phase", command=self.add_phase)
        self._phase_menu.add_command(label="Rename", command=self.edit_phase)
        self._phase_menu.add_command(label="Delete", command=self.del_phase)

    def setup_treeview(self):
        """Configure columns and bindings of the Treeview"""
        self.tree.config(yscrollcommand=self.scrollbar.set)
        self.tree.bind("<Button-3>", self._right_click)
        self.tree.bind("<Double-1>", self._select)
        self.tree.heading("#0", text="Strategies")
        self.tree.column("#0", width=150)

    def client_connected(self, client: StrategyClient):
        """Callback for when a Client is connected to a ClientHandler"""
        print("[StrategiesList] Successfully connect to server")
        self.client = client
        self.role = client.role

    def grid_widgets(self):
        """
        Configure widgets in grid geometry manager

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
        Callback to save a new item to the currently selected Phase
        :param item: item name
        :param box: (x, y) coordinates
        :param text: item text
        :param font: item font tuple
        :param color: item color hex value
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
        Callback to save the updated location of an item in the database
        :param text: item name
        :param x: item x coordinate
        :param y: item y coordinate
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
        """Update list of Strategies and Phases in Treeview"""
        self.tree.delete(*self.tree.get_children())
        for strategy, content in self.db:
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
        Callback for Button-1 Tkinter event so the user does not have
        to double-click on phases
        """
        if self.selected_phase:
            self.phase = self.selected_phase
            self._callback(self.selected_phase)
        return

    def new_strategy(self):
        """Open an AddStrategy Toplevel and wait to finish"""
        window = AddStrategy(db=self.db)
        window.wait_window()
        self.update_tree()

    def del_strategy(self):
        """Delete the selected strategy from the StrategyDatabase"""
        selection = self.tree.selection()
        if len(selection) is 0:
            return
        selection = selection[0]
        if selection not in self.db.keys():
            return
        del self.db[selection]
        self.update_tree()

    def add_phase(self):
        """Open an AddPhase Toplevel and wait to finish"""
        window = AddPhase(callback=self._new_phase)
        window.wait_window()

    def del_phase(self):
        """Delete the selected phase from the selected Strategy"""
        if self.selected_phase is None:
            return
        del self.db[self.selected_strategy][self.selected_phase]
        self.db.save_database()
        self.update_tree()

    def edit_phase(self):
        """Take user input to change the name of the selected Phase"""
        if self.selected_phase is None:
            return
        current = self.selected_phase
        string = askstring("GSF Parser: Phase Name", "Enter new name for {} Phase".format(current))
        if string is None or string == current:  # Cancelled by user
            return
        self.db[self.selected_strategy][string] = self.db[self.selected_strategy][current]
        del self.db[self.selected_strategy][current]
        self.update_tree()

    def _new_phase(self, title: str):
        """
        Callback for AddPhase Toplevel

        Create a new Phase in the Database with name title
        """
        self.db[self.selected_strategy][title] = Phase(title, self.db[self.selected_strategy].map)
        if self.selected_phase is not None:
            items = self.db[self.selected_strategy][self.selected_phase].items.copy()
            self.db[self.selected_strategy][title].items = items
        self.update_tree()
        self.db.save_database()

    def edit_strategy(self):
        """Callback for the edit strategy button"""
        # TODO: Implement name and map changing for Strategy
        pass

    def _select(self, event):
        """
        Callback for a double-click event to select an item from the
        Treeview.

        Updates UI and calls callback for updating Map
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
        """Callback to update widgets when a Strategy is selected"""
        self.new_button.config(text="New strategy", command=self.new_strategy)
        self.del_button.config(text="Delete strategy", command=self.del_strategy)
        self.edit_button.config(text="Add phase", command=self.add_phase, state=tk.NORMAL)

    def _phase_selected(self):
        """Callback to update widgets when a Phase is selected"""
        # self.new_button.config(text="New strategy", state=tk.DISABLED)
        self.del_button.config(text="Delete phase", command=self.del_phase)
        # self.edit_button.config(text="Edit phase", command=self.edit_phase, state=tk.DISABLED)

    @property
    def selection(self):
        """Return selection str instead of Treeview tuple"""
        selection = self.tree.selection()
        if len(selection) is 0:
            return None
        return selection[0]

    @property
    def selected_strategy(self):
        """Return name of selected Strategy in Treeview"""
        selection = self.selection
        if not selection:
            return None
        elements = selection.split("..")
        strategy = elements[0]
        strategy = strategy.strip()
        return strategy.replace("{", "").replace("}", "")

    @property
    def selected_phase(self):
        """Return name of selected Phase in Treeview"""
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
