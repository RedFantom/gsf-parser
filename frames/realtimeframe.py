# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
# Custom widgets
from widgets.time_view import TimeView


class RealtimeFrame(ttk.Frame):
    """
    A Frame that contains all the necessary widgets to control a RealTimeParser
    """
    def __init__(self, master, window):
        ttk.Frame.__init__(self, master)
        self.window = window
        """
        Widget creation
        """
        # Watching Label
        self.watching_stringvar = tk.StringVar()
        self.watching_label = ttk.Label(self, textvariable=self.watching_stringvar, justify=tk.LEFT)
        # Control widgets
        servers = ("Choose Server", ) + tuple(self.window.characters_frame.servers.values())
        self.server, self.character = tk.StringVar(), tk.StringVar()
        self.server_dropdown = ttk.OptionMenu(self, self.server, *servers)
        self.character_dropdown = ttk.OptionMenu(self, self.character, *("Choose Character",))
        self.parsing_control_button = ttk.Button(self, text="Start Parsing")
        # Data widgets
        self.data = tk.StringVar()
        self.data_label = ttk.Label(self, textvariable=self.data)
        self.time_view = TimeView(self, height=6, width=1.5)
        self.time_scroll = ttk.Scrollbar(self, command=self.time_view.yview)
        self.time_view.config(yscrollcommand=self.time_scroll.set)

    def grid_widgets(self):
        """
        Put all widgets into place
        """
        self.server_dropdown.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.character_dropdown.grid(row=1, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.parsing_control_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.data_label.grid(row=0, column=1, rowspan=3, sticky="nswe", padx=5, pady=5)
        self.time_view.grid(row=3, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)

        self.watching_label.grid(row=4, column=0, columnspan=2, sticky="nw", padx=5, pady=5)

    def start_parsing(self):
        pass

    def stop_parsing(self):
        pass

    def file_callback(self, file_name):
        """
        Callback for the RealTimeParser's LogStalker to set the file name in the watching label
        """
        self.watching_stringvar.set("Watching: {}".format(file_name))

    def match_callback(self):
        """
        Callback for the RealTimeParser to clear the TimeView
        """
        self.time_view.delete_all()

    def spawn_callback(self):
        """
        Callback for the RealTimeParser to clear the TimeView
        """
        self.time_view.delete_all()

    def event_callback(self, event, player_name, active_ids, start_time):
        """
        Callback for the RealTimeParser to insert an event into the TimeView
        """
        self.time_view.insert_event(event, player_name, active_ids, start_time)

    def open_overlay(self):
        pass

    def update_overlay(self):
        pass

    def close_overlay(self):
        pass

    @property
    def character_data(self):
        """
        Return Character Data tuple for selected character or None
        """
        if "Choose" in self.server.get() or "Choose" in self.character.get():
            return None
        reverse_servers = {value: key for key, value in self.window.characters_frame.servers.items()}
        server = reverse_servers[self.server.get()]
        return server, self.character.get()

