"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
from ast import literal_eval
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
# Packages
from PIL import Image, ImageTk
# Project Modules
from data.maps import MAP_NAMES
from utils.directories import get_assets_directory
from network.minimap.client import MiniMapClient


class MiniMap(tk.Toplevel):
    """
    Show a MiniMap with control widgets on which allied players can be
    displayed. Offers the following controls:
    - List of players currently logged in to the server
    - Map Selection dropdown
    # TODO: Map magnification factor
    """

    DIAMETER = 14

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.wm_title("GSF Parser: MiniMap Sharing")
        self.wm_resizable(False, False)

        # Attributes
        self._items = dict()
        self._client = None
        self.after_id = None
        self._background = None
        self._users = list()
        self._health = dict()

        # Widget Creation
        self._canvas = tk.Canvas(self)
        self._map = tk.StringVar()
        self._map_dropdown = ttk.OptionMenu(self, self._map, "Choose Environment", *tuple(MAP_NAMES.keys()))
        self._map_update = ttk.Button(self, text="Update", command=self.set_map)
        self._users_list = tk.Listbox(self, height=12, width=20)
        self._magnification = tk.StringVar()
        self._magnification_dropdown = ttk.OptionMenu(
            self, self._magnification, "1", "2", "4", "8")

        # Finish up
        self.setup_widgets()
        self.grid_widgets()

    def setup_widgets(self):
        """Configure widget contents"""
        self._canvas.config(width=800, height=800)

    def grid_widgets(self):
        """Put the widgets in their place"""
        self._canvas.grid(row=0, column=0, sticky="nswe", rowspan=4, padx=5, pady=5)
        self._map_update.grid(row=1, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))
        self._map_dropdown.grid(row=0, column=1, sticky="nswe", padx=(0, 5), pady=5)
        self._users_list.grid(row=2, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))
        self._magnification_dropdown.grid(row=3, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))

    def set_map(self):
        """Update map background"""
        map_name = self._map.get()
        if map_name not in MAP_NAMES:
            mb.showerror("Error", "Invalid map entered.")
            return
        file_name = MAP_NAMES[map_name]
        file_path = os.path.join(get_assets_directory(), "maps", file_name + ".jpg")
        size = self._canvas.winfo_width(), self._canvas.winfo_height()
        image = Image.open(file_path).resize((800, 800), Image.ANTIALIAS)
        print("[MiniMap] Image opened: ", image)
        self._background = ImageTk.PhotoImage(master=self, image=image)
        if "map" in self._items:
            self._canvas.delete(self._items["map"])
        self._items["map"] = self._canvas.create_image(0, 0, image=self._background, anchor=tk.NW, tag="background")
        # self._canvas.tag_lower("background")
        print("[MiniMap] New background: {}: {}, {}".format(self._items["map"], file_name, size))
        self._canvas.update()

    def update_markers(self):
        """Update markers by retrieving data from the client"""
        # Receive locations
        if not isinstance(self._client, MiniMapClient):
            raise TypeError
        self._client.receive()
        while not self._client.message_queue.empty():
            message = self._client.message_queue.get()
            if message == "exit":
                mb.showinfo("Info", "The remote host closed the connection.")
                self.destroy()
                return

            # Command
            elems = message.decode().split("_")
            command = elems[0]

            if command == "login":
                """A new user just logged in: login_username"""
                _, name = elems
                self._items[name] = None, None
                self._health[name] = "blue"
                self._users.append(name)
                self.update_users_list()

            elif command == "location":
                """A user sent us location data: location_username_tuple"""
                self.update_location(message)

            elif command == "health":
                """A user sent us health data: location_username_color"""
                self._health[elems[1]] = elems[2]

            elif command == "logout":
                """A user just logged out: logout_username"""
                _, name = elems
                # Delete markers
                old_mark, old_text = self._items[name]
                if old_mark is not None:
                    self._canvas.delete(old_mark, old_text)
                # Remove references
                del self._items[name]
                del self._health[name]
                self._users.remove(name)
                self.update_users_list()

        self.after_id = self.after(1000, self.update_markers)

    def update_users_list(self):
        """Update the users list widget"""
        self._users_list.delete(0, tk.END)
        for name in self._users:
            self._users_list.insert(tk.END, name)
        return True

    def set_client(self, client: MiniMapClient):
        """Set the Client for the window and start activities"""
        self._client = client
        self.after_id = self.after(1000, self.update_markers)

    def destroy(self):
        """Override destroy to cancel after task"""
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        tk.Toplevel.destroy(self)

    def update_location(self, message: str):
        """
        Update the location of a given user. Message:
        location_username_(x_float, y_float)
        """
        if isinstance(message, bytes):
            message = message.decode()
        elems = message.split("_")
        width, height = self._canvas.winfo_width(), self._canvas.winfo_height()
        # Collect data
        tup = literal_eval(elems[2])
        if tup[0] is None:
            return
        name = elems[1]
        if name not in self._items or name not in self._health:
            return
        health = self._health[name]
        # Calculate item location
        x, y = int(tup[0] * width), int(tup[1] * height)
        mark = self._canvas.create_oval(
            x, y, x + self.DIAMETER, y + self.DIAMETER, fill=health, tag="mark")
        text = self._canvas.create_text(
            x + self.DIAMETER + 2, y, anchor=tk.NW, text=name, fill="black", tag="name")
        # Delete old markers, if there are any
        if name in self._items and self._items[name] != (None, None):
            old_mark, old_text = self._items[name]
            self._canvas.delete(old_mark, old_text)
        # Update items dictionary
        self._items[name] = (mark, text)
