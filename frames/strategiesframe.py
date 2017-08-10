# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from strategies.strategylist import StrategyList
from strategies.map import Map
from strategies.settingstoplevel import SettingsToplevel
from strategies.toplevels import MapToplevel


class StrategyFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        # Create widgets
        self.list = StrategyList(self, callback=self._set_phase, settings_callback=self.open_settings)
        self.map = Map(self, moveitem_callback=self.list.move_item_phase, additem_callback=self.list.add_item_to_phase,
                       canvasheight=385, canvaswidth=385)
        self.large = None
        self.settings = None
        self.in_map = self.map
        self.description_header = ttk.Label(self, text="Description", font=("default", 12), justify=tk.LEFT)
        self.description = tk.Text(self, width=20, height=23, wrap=tk.WORD)
        self.description.bind("<KeyPress>", self.set_description)
        self.description_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.description.yview)
        self.description.config(yscrollcommand=self.description_scroll.set)
        self.client = None
        # Set up widgets
        self.grid_widgets()

    def open_settings(self, *args):
        if self.settings:
            self.settings.lift()
            return
        self.settings = SettingsToplevel(master=self, disconnect_callback=self.disconnect_callback)

    def grid_widgets(self):
        # self.menu.grid(column=0, row=0, columnspan=2, sticky="nswe")
        self.list.grid(column=0, row=1, sticky="nswe", rowspan=2)
        self.map.grid(column=1, row=1, sticky="nswe", pady=5, rowspan=2)
        self.description_header.grid(column=3, columnspan=2, sticky="w", pady=(5, 0), padx=5, row=1)
        self.description.grid(column=3, row=2, sticky="nwe", padx=5, pady=(0, 5))
        self.description_scroll.grid(column=4, row=2, sticky="ns")

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
        self.large = MapToplevel(frame=self)
        if self.list.selected_phase is None:
            return
        self.large.map.update_map(self.list.db[self.list.selected_strategy][self.list.selected_phase])
        if self.client:
            self.large.client = self.client

    def client_connected(self, client):
        if client is None:
            raise ValueError()
        self.client = client
        if client.role.lower() == "master":
            pass
        self.list.client_connected(client)
        self.map.client = self.client
        self.client.start()

    def insert_callback(self, command, args):
        if not self.client:
            raise ValueError()
        print("Insert callback received: ", command, args)
        if command == "client_login":
            for strategy in self.list.db.data.keys():
                self.client.send_strategy(self.list.db.data[strategy])
        if self.list.selected_strategy != args[0] or self.list.selected_phase != args[1]:
            return
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
                    map.canvas.coords(item, int(int(x) / 768 * 385), int(int(y) / 768 * 385))
                else:
                    map.canvas.coords(item, int(x), int(y))
                map.canvas.coords(rectangle, map.canvas.bbox(item))
        else:
            raise ValueError("Unknown command: {0} with args {1}".format(command, args))

    def disconnect_callback(self):
        self.map.client = None
        if self.in_map:
            self.in_map.client = None
        self.client = None
        self.list.client = None
        for map in self.maps:
            map.set_readonly(False)

    @property
    def maps(self):
        if self.in_map:
            return [self.map, self.in_map]
        else:
            return [self.map]


