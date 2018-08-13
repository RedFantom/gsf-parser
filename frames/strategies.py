"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from ast import literal_eval
import sys
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Project Modules
from widgets.strategy.list import StrategiesList
from widgets.strategy.map import Map
from toplevels.strategy.settings import SettingsToplevel
from toplevels.strategy.map import MapToplevel


class StrategiesFrame(ttk.Frame):
    """
    Frame to display a StrategiesList and Map widget to allow the user
    to create and edit Strategies with custom item in them to visualize
    their tactics. An interface to allow real-time Strategy editing is
    also provided.
    """

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        """
        The two core widgets of this frame, with lots of callbacks to support 
        the different functionality. Not all functionality is provided through 
        callbacks, and providing any other widget than the StrategiesFrame as a
        master widget is inadvisable. This is the result of bad coding practices.
        """
        self.list = StrategiesList(self, callback=self._set_phase, settings_callback=self.open_settings, frame=self)
        self.map = Map(self, moveitem_callback=self.list.move_item_phase, additem_callback=self.list.add_item_to_phase,
                       canvasheight=385, canvaswidth=385)
        self.large = None
        self.settings = None
        self.in_map = self.map
        # Create the widgets to support the description section on the right of the frame.
        self.description_header = ttk.Label(self, text="Description", font=("default", 12), justify=tk.LEFT)
        self._descr_l = 20 if sys.platform != "linux" else 30
        self.description = tk.Text(
            self, width=self._descr_l, height=23, wrap=tk.WORD, font=("default", 11))
        self._descr_w = self.description.winfo_reqwidth()
        # Bind the KeyPress event to a callback. A KeyPress is fired when *any* key is pressed on the keyboard.
        self.description.bind("<KeyPress>", self.set_description_callback)
        self.description_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.description.yview)
        self.description.config(yscrollcommand=self.description_scroll.set)
        self.client = None
        self.description_update_task = None
        # This frame calls grid_widgets in its __init__ function
        self.grid_widgets()

    def open_settings(self, *args):
        """
        Callback for the Settings button to open a SettingsToplevel.
        Only one SettingsToplevel is allowed to be open at any given
        time, to prevent any problems with the Client/Server
        functionality. If a SettingsToplevel is already open, lifts the
        SettingsToplevel to the front so it is visible to the user.
        """
        if self.settings:
            self.settings.lift()
            return
        """
        The StrategiesFrame instance is passed as an argument because 
        not all functionality is provided through callbacks, but some 
        code is directly executed on the StrategiesFrame instance. Bad 
        coding practices yet again.
        """
        self.settings = SettingsToplevel(master=self, disconnect_callback=self.disconnect_callback)

    def grid_widgets(self):
        """It is pretty obvious what this does"""
        self.list.grid(column=0, row=1, sticky="nswe", rowspan=2)
        self.map.grid(column=1, row=1, sticky="nswe", pady=5, rowspan=2)
        self.description_header.grid(column=3, columnspan=2, sticky="w", pady=(5, 0), padx=5, row=1)
        self.description.grid(column=3, row=2, sticky="nwe", padx=5, pady=(0, 5))
        self.description_scroll.grid(column=4, row=2, sticky="ns", pady=(0, 10))

    def _set_phase(self, phase):
        """
        Callback for the StrategiesList widget to call when a new Phase
        is selected.
        :param phase: Phase name
        """
        for map in self.maps:
            map.update_map(self.list.db[self.list.selected_strategy][phase])
        return

    def set_description_callback(self, *args):
        """Delay for issue #142"""
        self.after(5, self.set_description)

    def set_description(self):
        """
        Update the description of a certain item in the database. Also
        immediately saves the database, so the description is
        automatically saved when updated.
        """
        if self.list.selected_strategy is None:
            return
        if self.client and self.settings.client_permissions[self.client.name][1] is False:
            self.description.delete("1.0", tk.END)
            self.description.insert("1.0",
                                    self.list.db[self.list.selected_strategy][self.list.selected_phase].description)
        if self.list.selected_phase is not None:
            self.list.db[self.list.selected_strategy][self.list.selected_phase]. \
                description = self.description.get("1.0", tk.END)
            self.list.db.save_database()
        else:
            self.list.db[self.list.selected_strategy].description = self.description.get("1.0", tk.END)
            self.list.db.save_database()
        if self.settings is not None:
            allowed = self.settings.client_permissions[self.client.name][1]
            if self.client and (allowed is True or allowed == "True" or allowed == "Master"):
                self.send_description()

    def send_description(self):
        """
        Function to make sure that the description only gets sent two
        seconds after stopping typing when editing it, to lower
        bandwidth requirements.
        """
        if self.description_update_task:
            self.after_cancel(self.description_update_task)
        self.description_update_task = self.after(
            2000, lambda: self.client.update_description(
                self.list.selected_strategy, self.list.selected_phase,
                self.description.get("1.0", tk.END)))

    def show_large(self):
        """
        Callback for the Edit (large map)-Button of the StrategiesList
        widget to open a larger map in a Toplevel (the MapToplevel from
        toplevels.strategy_toplevels)
        """
        self.large = MapToplevel(frame=self)
        if self.list.selected_phase is None:
            return
        self.large.map.update_map(self.list.db[self.list.selected_strategy][self.list.selected_phase])
        # If the instance is connected to a network, then the Map in the MapToplevel should know about it.
        if self.client:
            self.large.map.client = self.client

    def client_connected(self, client):
        """
        Callback for the SettingsToplevel (when open) to call when a
        Client object is connected to a network. Sets the client
        attribute for this instance, calls another callback, sets the
        client attribute for the Map instance and *starts the Client
        Thread to start the functionality of the Client*.
        """
        self.client = client
        self.list.client_connected(client)
        self.map.client = self.client
        if self.in_map:
            self.in_map.client = self.client
        self.client.start()

    def insert_callback(self, command, args):
        """
        Callback that has numerous functions:
        - Before doing anything checks if the Client object is valid for
          operations to be performed
        - Inserts a log entry for the command received into the
          ServerToplevel widget if the client is a master client
        - Executes the command of the network on the Map widgets with
          the given arguments
          * add_item
          * move_item
          * del_item
        :param command: command received from the network
        :param args: arguments to perform this command
        :return: None
        :raises: ValueError when the Client is not set or not logged in
        :raises: ValueError when the command received is unknown
        """
        print("Insert callback received: ", command, args)

        # If the command is a login, then only a log should be created, and *all* Strategies in the database
        # are sent to the new client to ensure smooth editing of the Strategies
        # These are the commands with which the master can control the Server and its Clients
        if command == "readonly":
            target, allowed = args
            if target != self.client.name:
                return
            allowed = literal_eval(allowed)
            for map in self.maps:
                map.set_readonly(allowed)
            if allowed:
                messagebox.showinfo("Info", "You are now allowed to edit the maps.")
            else:
                messagebox.showinfo("Info", "You are no longer allowed to edit the maps.")
        elif command == "kicked":
            messagebox.showerror("Info", "You were kicked from the Server.")
            self.settings.disconnect_client()
            return
        elif command == "banned":
            messagebox.showerror("Info", "You were banned from the Server.")
            self.settings.disconnect_client()
            return
        elif command == "allowshare":
            if not isinstance(args, list):
                args = literal_eval(args)
            _, name, allowed = args
            if not isinstance(allowed, bool):
                allowed = literal_eval(allowed)
            self.settings.update_share(name, allowed)
            if name != self.client.name:
                return
            if allowed:
                messagebox.showinfo("Info", "You are now allowed by the Master of the Server to share your Strategies.")
            else:
                messagebox.showinfo("Info", "You are now no longer allowed by the Master of the Server to share your "
                                            "Strategies.")
            return
        elif command == "allowedit":
            _, name, allowed = args
            if not isinstance(allowed, bool):
                allowed = literal_eval(allowed)
            if name == self.client.name:
                if allowed:
                    messagebox.showinfo("Info", "You are now allowed by the Master of the Server to edit the "
                                                "Strategies you have available. These edits will be shared with the "
                                                "other users.")
                    for map in self.maps:
                        map.set_readonly(False)
                else:
                    messagebox.showinfo("Info", "You are now no longer allowed by the Master of the Server to edit the "
                                                "Strategies you have available.")
                    for map in self.maps:
                        map.set_readonly(True)
            self.settings.update_edit(name, allowed)
            return
        elif command == "master":
            name = args
            if name == self.client.name:
                messagebox.showinfo("Info", "You are now the Master of the Server.")
                self.settings.update_master()
            else:
                self.settings.new_master(name)
            return

        elif command == "master_login":
            name = args
            self.settings._login_callback(name, "master")

        elif command == "client_login":
            name = args
            self.settings._login_callback(name, "client")

        elif command == "logout":
            name = args
            self.settings._logout_callback(name)

        elif command == "description":
            _, strategy, phase, description = args
            if phase == "None":
                phase = None
            self.list.db[strategy][phase].description = description
            if strategy == self.list.selected_strategy:
                self.description.delete("1.0", tk.END)
                self.description.insert("1.0", description)

        # The arguments *always* include the Strategy name and Phase name for
        # the operations to be performed on if these do not match the selected
        # Strategy and Phase, then no visible changes occur on the Map widgets.
        # However, the saving of the changes happen before this code is reached,
        # and thus if the user moves to the other Strategy and Phase that the
        # operations were performed on, the user will still see the changed
        # elements
        elif self.list.selected_strategy != args[0] or self.list.selected_phase != args[1]:
            return
        # Perform the operations on the Map instances to make the visual changes
        elif command == "add_item":
            _, _, text, font, color = args
            for map in self.maps:
                map.add_item(text, font=font, color=color)
        elif command == "del_item":
            _, _, text = args
            for map in self.maps:
                map.canvas.delete(map.items[text][0], map.items[text][1])
        elif command == "move_item":
            _, _, text, x, y = args
            for map in self.maps:
                rectangle, item = map.items[text]
                if map is self.in_map:
                    coords = (int(int(x) / 768 * 385), int(int(y) / 768 * 385))
                    map.canvas.coords(item, *coords)
                else:
                    map.canvas.coords(item, int(x), int(y))
                map.canvas.coords(rectangle, map.canvas.bbox(item))
        else:
            raise ValueError("Unknown command: {0} with args {1}".format(command, args))

    def disconnect_callback(self):
        """
        Callback that is called when the Client is disconnected from the
        Server, for whatever reason. All changes the master Client made
        are already saved, so this code only resets the state of the
        widgets in the StrategiesFrame instance.
        """
        self.map.client = None
        if self.in_map:
            self.in_map.client = None
        self.client = None
        self.list.client = None
        self.map.set_readonly(False)

    @property
    def maps(self):
        """Return list of Map objects available in StrategiesFrame instance"""
        if self.in_map is not self.map:
            return [self.map, self.in_map]
        return [self.map]

    def config_size(self, width: int, height: int):
        """Configure size of child widgets"""
        list_w, scroll_w = self.list.winfo_width(), self.description_scroll.winfo_width()
        canvas_w = min(width - self._descr_w - list_w - scroll_w, height)
        self.in_map.configure(width=canvas_w, height=canvas_w)
        self.list.configure_height(height)

        text_w = width - canvas_w - list_w - scroll_w
        self.description.configure(width=int(text_w // 10), height=int(height // 18.5 - 2))

