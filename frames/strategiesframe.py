# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ast import literal_eval
# Own modules
from widgets.strategy_list import StrategiesList
from widgets.strategy_map import Map
from toplevels.strategy_settings_toplevel import SettingsToplevel
from toplevels.strategy_toplevels import MapToplevel


class StrategiesFrame(ttk.Frame):
    """
    Frame to display a StrategiesList and Map widget to allow the user to create and edit Strategies with custom items
    in them to visualize their tactics. An interface to allow real-time Strategy editing is also provided.
    """
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        # The two core widgets of this frame, with lots of callbacks to support the different functionality
        # Not all functionality is provided through callbacks, and providing any other widget than the StrategiesFrame
        # as a master widget is inadvisable. This is the result of bad coding practices.
        self.list = StrategiesList(self, callback=self._set_phase, settings_callback=self.open_settings)
        self.map = Map(self, moveitem_callback=self.list.move_item_phase, additem_callback=self.list.add_item_to_phase,
                       canvasheight=385, canvaswidth=385)
        self.large = None
        self.settings = None
        self.in_map = self.map
        # Create the widgets to support the description section on the right of the frame.
        self.description_header = ttk.Label(self, text="Description", font=("default", 12), justify=tk.LEFT)
        self.description = tk.Text(self, width=20, height=23, wrap=tk.WORD)
        # Bind the KeyPress event to a callback. A KeyPress is fired when *any* key is pressed on the keyboard.
        self.description.bind("<KeyPress>", self.set_description)
        self.description_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.description.yview)
        self.description.config(yscrollcommand=self.description_scroll.set)
        self.client = None
        # This frame calls grid_widgets in its __init__ function
        self.grid_widgets()

    def open_settings(self, *args):
        """
        Callback for the Settings button to open a SettingsToplevel. Only one SettingsToplevel is allowed to be open at
        any given time, to prevent any problems with the Client/Server functionality. If a SettingsToplevel is already
        open, lifts the SettingsToplevel to the front so it is visible to the user.
        """
        if self.settings:
            self.settings.lift()
            return
        # The StrategiesFrame instance is passed as an argument because not all functionality is provided through
        # callbacks, but some code is directly executed on the StrategiesFrame instance. Bad coding practices yet again.
        self.settings = SettingsToplevel(master=self, disconnect_callback=self.disconnect_callback)

    def grid_widgets(self):
        """
        It is pretty obvious what this does
        """
        self.list.grid(column=0, row=1, sticky="nswe", rowspan=2)
        self.map.grid(column=1, row=1, sticky="nswe", pady=5, rowspan=2)
        self.description_header.grid(column=3, columnspan=2, sticky="w", pady=(5, 0), padx=5, row=1)
        self.description.grid(column=3, row=2, sticky="nwe", padx=5, pady=(0, 5))
        self.description_scroll.grid(column=4, row=2, sticky="ns")

    def _set_phase(self, phase):
        """
        Callback for the StrategiesList widget to call when a new Phase is selected.
        :param phase: phase name
        :return: None
        """
        self.map.update_map(self.list.db[self.list.selected_strategy][phase])
        if self.in_map:
            self.in_map.update_map(self.list.db[self.list.selected_strategy][phase])

    def set_description(self, *args):
        """
        Update the description of a certain item in the database. Also immediately saves the database, so the
        description is automatically saved when updated.
        """
        if self.list.selected_phase is not None:
            self.list.db[self.list.selected_strategy][self.list.selected_phase]. \
                description = self.description.get("1.0", tk.END)
            self.list.db.save_database()
        else:
            self.list.db[self.list.selected_strategy].description = self.description.get("1.0", tk.END)
            self.list.db.save_database()

    def show_large(self):
        """
        Callback for the Edit (large map)-Button of the StrategiesList widget to open a larger map in a Toplevel (the
        MapToplevel from toplevels.strategy_toplevels)
        """
        self.large = MapToplevel(frame=self)
        if self.list.selected_phase is None:
            return
        self.large.map.update_map(self.list.db[self.list.selected_strategy][self.list.selected_phase])
        # If the instance is connected to a server, then the Map in the MapToplevel should know about it.
        if self.client:
            self.large.map.client = self.client

    def client_connected(self, client):
        """
        Callback for the SettingsToplevel (when open) to call when a Client object is connected to a server. Sets the
        client attribute for this instance, calls another callback, sets the client attribute for the Map instance and
        *starts the Client Thread to start the functionality of the Client*.
        :param client: Client instance
        :return: None
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
        - Before doing anything checks if the Client object is valid for operations to be performed
        - Inserts a log entry for the command received into the ServerToplevel widget if the client is a master client
        - Executes the command of the server on the Map widgets with the given arguments
          * add_item
          * move_item
          * del_item
        :param command: command received from the server
        :param args: arguments to perform this command
        :return: None
        :raises: ValueError when the Client is not set or not logged in
        :raises: ValueError when the command received is unknown
        """
        if not self.client or not self.client.logged_in:
            raise ValueError("insert_callback called when the client attribute is not set or not logged_in")
        print("Insert callback received: ", command, args)

        # If the command is a login, then only a log should be created, and *all* Strategies in the database
        # are sent to the new client to ensure smooth editing of the Strategies
        # TODO: Allow the master Client to select only specific Strategies for replication
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
                allowed = literal_eval(args)
            else:
                allowed = args[1]
            if allowed:
                messagebox.showinfo("Info", "You are now allowed by the Master of the Server to share your Strategies.")
                self.settings.update_share(allowed)
            else:
                messagebox.showinfo("Info", "You are now no longer allowed by the Master of the Server to share your "
                                            "Strategies.")
                self.settings.update_share(allowed)
            return
        elif command == "allowedit":
            _, name, allowed = args
            if not isinstance(allowed, bool):
                allowed = literal_eval(allowed)
            if name == self.client.name:
                if allowed:
                    messagebox.showinfo("Info", "You are now allowed by the Master of the Server to edit the Strategies "
                                                "you have available. These edits will be shared with the other users.")
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

        # The arguments *always* include the Strategy name and Phase name for the operations to be performed on
        # If these do not match the selected Strategy and Phase, then no visible changes occur on the Map widgets
        # However, the saving of the changes happen before this code is reached, and thus if the user moves to the other
        # Strategy and Phase that the operations were performed on, the user will still see the changed elements
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
                    coords = (int(int(x) / 768 * map.width), int(int(y) / 768 * map.height))
                    map.canvas.coords(item, *coords)
                else:
                    map.canvas.coords(item, int(x), int(y))
                map.canvas.coords(rectangle, map.canvas.bbox(item))
        else:
            raise ValueError("Unknown command: {0} with args {1}".format(command, args))

    def disconnect_callback(self):
        """
        Callback that is called when the Client is disconnected from the Server, for whatever reason. All changes the
        master Client made are already saved, so this code only resets the state of the widgets in the StrategiesFrame
        instance.
        """
        self.map.client = None
        if self.in_map:
            self.in_map.client = None
        self.client = None
        self.list.client = None
        self.map.set_readonly(False)

    @property
    def maps(self):
        """
        :return: list of Map objects available in StrategiesFrame instance
        """
        if self.in_map:
            return [self.map, self.in_map]
        else:
            return [self.map]

