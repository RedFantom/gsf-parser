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
    """
    Toplevel to allow the user to choose a name and map for the new Strategy the user wants to create. Also features a
    Cancel button to allow the user to cancel the action.
    """
    maps = {
        "Kuat Mesas DOM": ("dom", "km"),
        "Lost Shipyards DOM": ("dom", "ls"),
        "Denon Exosphere DOM": ("dom", "de"),
        "Kuat Mesas TDM": ("tdm", "km"),
        "Lost Shipyards TDM": ("tdm", "ls")
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
        """
        The usual function to setup the geometry of the Toplevel
        """
        self.name_entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.map_dropdown.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=5, pady=(0, 5))
        self.add_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.cancel_button.grid(row=2, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))

    def entry_callback(self, event):
        """
        Callback to remove the placeholder from the strategy name entry when clicked
        """
        if self.name_entry.get() == "Strategy name...":
            self.name_entry.delete(0, tk.END)
        return

    def add(self):
        """
        Function called by the Add-button to actually add the Strategy. Destroys the Toplevel after the Strategy is
        saved to the database.
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
        Performs checks on the widgets in order to check if the data the user entered was valid. If not, the user is
        shown an information message. Currently checks:
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


class AddPhase(tk.Toplevel):
    """
    Toplevel to show widgets for entering the data required to create a new Phase.
    """
    def __init__(self, *args, **kwargs):
        """
        :param callback: Function to call when the Phase is created, arguments: *(phase_name)
        """
        self._callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add new phase")
        self._entry = ttk.Entry(self, width=30)
        # Bind the Enter key to the same function as the Add-button for user convenience
        self._entry.bind("<Return>", self.add_phase)
        self._cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self._add_button = ttk.Button(self, text="Add", command=self.add_phase)
        self.grid_widgets()

    def grid_widgets(self):
        """
        The usual function to setup the geometry of the Toplevel
        """
        self._entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self._cancel_button.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self._add_button.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)

    def add_phase(self, *args):
        """
        Function to call the callback when the phase is created
        :param args: For Tkinter <Return> event, not used
        :return: None
        """
        if not self.check_widgets():
            return
        if callable(self._callback):
            self._callback(self._entry.get())
        self.destroy()

    def check_widgets(self):
        """
        Checks if the data entered by the user is valid to create a Phase
        :return: True if data is valid, False if not
        """
        name = self._entry.get()
        if "¤" in name or "³" in name or "_" in name or "`" in name or "~" in name or "€" in name:
            messagebox.showinfo("Info", "The name you have chosen for your Phase contains invalid characters. A "
                                        "Phase name may not contain the characters _, `, ~, ³, ¤ or €.")
            return False
        return True


class MapToplevel(tk.Toplevel):
    """
    Toplevel to show a large version of the Map widget.
    """
    def __init__(self, *args, **kwargs):
        """
        :param frame: StrategiesFrame instance
        """
        self.frame = kwargs.pop("frame", None)
        self.list = self.frame.list
        if not self.frame:
            raise ValueError("No parent frame passed as argument")
        tk.Toplevel.__init__(self, *args, **kwargs)
        # The MapToplevel reroutes the callbacks that usually go to StrategiesFrame to itself in order to perform
        # additional functionality to keep the Map in the StrategiesFrame up-to-date with itself.
        self.map = Map(self, moveitem_callback=self.move_item_phase,
                       additem_callback=self.add_item_to_phase, delitem_callback=self.del_item_phase,
                       canvaswidth=768, canvasheight=768)
        self.map.grid()
        # Sets the in_map attribute of StrategiesFrame to the former map attribute to keep the Map reference for
        # the map visible in the StrategiesFrame itself. The map in the StrategiesFrame is then set to readonly.
        self.frame.in_map = self.frame.map
        self.frame.in_map.set_readonly(True)
        self.frame.map = self.map
        # Reroute the closing of the window to a custom function to make sure that the above code is rolled back before
        # closing the map, so as not to leave the user with only a readonly map.
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)
        self.title("GSF Strategy Manager: Enlarged map")

    def move_item_phase(self, *args, **kwargs):
        """
        Custom callback to also update the map inside the StrategiesFrame when an item is moved in the Phase
        """
        self.frame.list.move_item_phase(*args, **kwargs)
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase]
            )
        # If not called, the Treeview in the StrategiesList will expand for some weird reason
        self.frame.list.tree.column("#0", width=150)
        self.frame.grid_widgets()

    def add_item_to_phase(self, *args, **kwargs):
        """
        Custom callback to also update the map inside the StrategiesFrame when an item is added to the Phase
        """
        self.frame.list.add_item_to_phase(*args, **kwargs)
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase]
            )
        # If not called, the Treeview in the StrategiesList will expand for some weird reason
        self.frame.list.tree.column("#0", width=150)

    def del_item_phase(self, item, rectangle, text):
        """
        Custom callback to also update the map inside the StrategiesFrame when an item is deleted form the Phase
        """
        print("Deleting item {0}".format(text))
        del self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase][text]
        self.frame.list.db.save_database()
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase]
            )

    def close(self):
        """
        Callback for the WM_DELETE_WINDOW event (when the red X is pressed on the window) to restore the situation from
        before __init__ was run, unless a Client is connected with client role, in which case the Map should still be
        readonly.
        """
        self.frame.map = self.frame.in_map
        if not self.frame.map:
            return
        if not self.frame.map.client or self.frame.settings.client_permissions[self.frame.client.name][1] is True:
            self.frame.map.set_readonly(False)
        self.frame.in_map = None
        self.destroy()
