"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
# Project Modules
from widgets.strategy.map import Map


class MapToplevel(tk.Toplevel):
    """Toplevel to show a large version of the Map widget"""

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
        Custom callback to also update the map inside the
        StrategiesFrame when an item is moved in the Phase
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
        Custom callback to also update the map inside the
        StrategiesFrame when an item is added to the Phase
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
        Custom callback to also update the map inside the
        StrategiesFrame when an item is deleted form the Phase
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
        Callback for the WM_DELETE_WINDOW event (when the red X is
        pressed on the window) to restore the situation from before
        __init__ was run, unless a Client is connected with client role,
        in which case the Map should still be readonly.
        """
        self.frame.map = self.frame.in_map
        if not self.frame.map:
            return
        if not self.frame.map.client or self.frame.settings.client_permissions[self.frame.client.name][1] is True:
            self.frame.map.set_readonly(False)
        self.frame.in_map = None
        self.destroy()
