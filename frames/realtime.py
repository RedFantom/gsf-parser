"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import time
import psutil
import os
import sys
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Project Modules
from widgets.time_view import TimeView
from toplevels.minimap import MiniMap
from parsing.realtime import RealTimeParser
from queue import Queue
from variables import settings
from utils.swtor import get_swtor_screen_mode
from utils.admin import check_privileges


class RealtimeFrame(ttk.Frame):
    """
    A Frame that contains all the necessary widgets to control a
    RealTimeParser instance.
    """
    def __init__(self, master, window):
        ttk.Frame.__init__(self, master)
        """
        Attributes 
        """
        self.window = window
        self.after_id = None
        self.parser = None
        self.exit_queue = None
        self.data_queue = None
        self.return_queue = None
        self.overlay = None
        self.overlay_after_id = None
        self.overlay_string = None
        self.data_after_id = None
        """
        Widget creation
        """
        # Watching Label
        self.watching_stringvar = tk.StringVar(self, value="Watching no file...")
        self.watching_label = ttk.Label(self, textvariable=self.watching_stringvar, justify=tk.LEFT)
        self.cpu_stringvar = tk.StringVar()
        self.cpu_label = ttk.Label(self, textvariable=self.cpu_stringvar, justify=tk.LEFT)

        # Control widgets
        servers = ("Choose Server",) + tuple(self.window.characters_frame.servers.values())
        self.server, self.character = tk.StringVar(), tk.StringVar()
        self.server_dropdown = ttk.OptionMenu(self, self.server, *servers, command=self.update_characters)
        self.character_dropdown = ttk.OptionMenu(self, self.character, *("Choose Character",))
        self.parsing_control_button = ttk.Button(self, text="Start Parsing", command=self.start_parsing, width=20)

        # Data widgets
        self.data = tk.StringVar()
        self.data_label = ttk.Label(self, textvariable=self.data)
        self.time_view = TimeView(self, height=6, width=1.5)
        self.time_scroll = ttk.Scrollbar(self, command=self.time_view.yview)
        self.time_view.config(yscrollcommand=self.time_scroll.set)

        # MiniMap widgets
        self.minimap_enabled = tk.BooleanVar()
        self.minimap_checkbox = ttk.Checkbutton(self, text="MiniMap Location Sharing", variable=self.minimap_enabled)
        self.minimap_address = tk.StringVar(self, "Address : Port")
        self.minimap_name = tk.StringVar(self, "Username")
        self.minimap_name_entry = ttk.Entry(self, width=25, textvariable=self.minimap_name)
        self.minimap_address_entry = ttk.Entry(self, width=25, textvariable=self.minimap_address)
        self.minimap = None

        # Start monitoring CPU usage
        self.process = psutil.Process(os.getpid())
        self.after(2000, self.update_cpu_usage)

    def grid_widgets(self):
        """Put all widgets into place"""
        self.server_dropdown.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.character_dropdown.grid(row=1, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.parsing_control_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        """Data label is deprecated. Use Overlay."""
        # self.data_label.grid(row=0, column=1, rowspan=3, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.time_view.grid(row=3, column=0, columnspan=3, sticky="nswe", padx=5, pady=5)

        self.watching_label.grid(row=4, column=0, columnspan=3, sticky="nw", padx=5, pady=5)
        self.cpu_label.grid(row=4, column=2, sticky="nw", padx=5, pady=5)

        self.minimap_checkbox.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)
        self.minimap_name_entry.grid(row=1, column=1, sticky="nsw", padx=5, pady=(0, 5))
        self.minimap_address_entry.grid(row=2, column=1, sticky="nsw", padx=5, pady=(0, 5))

    """
    Parsing Functions
    """

    def start_parsing(self):
        """
        Check if parsing can be started, and if so, start the
        parsing process
        """
        if self.character_data is None:
            messagebox.showinfo("Info", "Please select a valid character using the dropdowns.")
            return
        if (settings["realtime"]["overlay"] or
                settings["realtime"]["screen_overlay"] or
                settings["realtime"]["screenparsing"]):
            if get_swtor_screen_mode() is False:
                return
        if "Mouse and Keyboard" in settings["realtime"]["screen_features"] and sys.platform != "linux":
            if not check_privileges():
                messagebox.showinfo(
                    "Info", "Mouse and keyboard parsing is enabled, but the GSF Parser is not running as "
                            "administrator, which prevents reading input from the SWTOR window. Please restart the "
                            "GSF Parser as administrator for this feature to work.")

        # Setup attributes
        self.exit_queue, self.data_queue, self.return_queue = Queue(), Queue(), Queue()
        args = (self.window.characters_frame.characters, self.character_data, self.exit_queue,
                self.window.builds_frame.ships_data, self.window.builds_frame.companions_data)
        # Create MiniMap window
        if self.minimap_enabled.get() is True:
            self.minimap = MiniMap(self.window)
        # Generate kwargs
        kwargs = {
            "spawn_callback": self.spawn_callback,
            "match_callback": self.match_callback,
            "file_callback": self.file_callback,
            "event_callback": self.event_callback,
            "screen_parsing_enabled": settings["realtime"]["screenparsing"],
            "screen_parsing_features": settings["realtime"]["screen_features"],
            "data_queue": self.data_queue,
            "return_queue": self.return_queue,
            "minimap_share": self.minimap_enabled.get(),
            "minimap_user": self.minimap_name.get(),
            "minimap_address": self.minimap_address.get(),
            "minimap_window": self.minimap
        }
        try:
            self.parser = RealTimeParser(*args, **kwargs)
        except Exception as e:
            messagebox.showerror(
                "Error",
                "An error occurred during the initialization of the RealTimeParser. Please report the error given "
                "below, as well as, if possible, the full stack-trace to the developer.\n\n{}".format(e)
            )
            raise
        # Change Button state
        self.parsing_control_button.config(text="Stop Parsing", command=self.stop_parsing)
        self.watching_stringvar.set("Waiting for a CombatLog...")
        self.open_overlay()
        self.update_data_string()
        # Start the parser
        self.parser.start()

    def stop_parsing(self):
        """Stop the parsing process"""
        if self.minimap_enabled.get() is True and self.minimap is not None:
            self.minimap.destroy()
        self.close_overlay()
        self.parser.stop()
        self.parsing_control_button.config(text="Start Parsing", command=self.start_parsing)
        self.exit_queue, self.data_queue, self.return_queue = None, None, None
        time.sleep(1)
        try:
            self.parser.join()
        except Exception as e:
            messagebox.showerror("Error", "While real-time parsing, the following error occurred:\n\n{}".format(e))
            raise
        self.watching_stringvar.set("Watching no file...")
        self.parser = None
        self.close_overlay()

    def file_callback(self, file_name):
        """
        Callback for the RealTimeParser's LogStalker to set the file
        name in the watching label
        """
        print("[RealTimeParser] New file {}".format(file_name))
        self.watching_stringvar.set("Watching: {}".format(file_name))

    def match_callback(self):
        """Callback for the RealTimeParser to clear the TimeView"""
        self.time_view.delete_all()

    def spawn_callback(self):
        """Callback for the RealTimeParser to clear the TimeView"""
        self.time_view.delete_all()

    def event_callback(self, event, player_name, active_ids, start_time):
        """
        Callback for the RealTimeParser to insert an event into the TimeView
        """
        self.time_view.insert_event(event, player_name, active_ids, start_time)
        self.time_view.yview_moveto(1.0)

    def update_cpu_usage(self):
        """Update the CPU usage Label every two seconds"""
        string = "CPU usage: {}%".format(self.process.cpu_percent())
        self.after(2000, self.update_cpu_usage)
        if self.parser is not None and self.parser.diff is not None:
            diff = self.parser.diff
            string += ", {:.03f}s".format(diff.total_seconds())
        self.cpu_stringvar.set(string)

    """
    Overlay Handling
    """

    def open_overlay(self):
        """Open an overlay if the settings given by the user allow for it"""
        if settings["realtime"]["overlay"] is False and settings["realtime"]["screen_overlay"] is False:
            return
        if settings["realtime"]["overlay_experimental"] is True and sys.platform != "linux":
            from widgets.overlays.overlay_windows import WindowsOverlay as Overlay
        else:  # Linux or non-experimental
            from widgets import Overlay
        # Generate arguments for Overlay.__init__
        position = settings["realtime"]["overlay_position"]
        x, y = position.split("y")
        x, y = int(x[1:]), int(y)
        self.overlay_string = tk.StringVar(self)
        try:
            self.overlay = Overlay((x, y), self.overlay_string, master=self.window, auto_init=True)
        except Exception as e:
            messagebox.showerror(
                "Error", "The GSF Parser encountered an error while initializing the Overlay. Please report the error "
                         "message below to the developer. This error is fatal. The GSF Parser cannot continue."
                         "\n\n{}.".format(e))
            raise
        self.update_overlay()

    def update_data_string(self):
        if self.parser is None:
            if self.data_after_id is not None:
                self.after_cancel(self.data_after_id)
                self.data_after_id = None
            return
        self.data_label.config(text=self.parser.overlay_string)
        self.data_after_id = self.after(1000, self.update_data_string)

    def update_overlay(self):
        """
        Periodically called function to update the text shown in the Overlay
        """
        if self.parser is None or not isinstance(self.parser, RealTimeParser):
            print("[RealTimeFrame] Cancelling Overlay update.")
            return
        string = self.parser.overlay_string
        if string.endswith("\n"):
            string = string[:-1]
        self.overlay.update_text(string)
        self.overlay_after_id = self.after(1000, self.update_overlay)

    def close_overlay(self):
        """Close the overlay"""
        if self.overlay_after_id is not None:
            self.after_cancel(self.overlay_after_id)
        if self.overlay is not None:
            self.overlay.destroy()
        self.overlay = None
        self.overlay_after_id = None

    """
    Character handling
    """

    def update_characters(self, *args):
        """Update the characters shown in the character dropdown"""
        if len(args) == 0:
            return
        server = args[0]
        if "Choose" in server:
            return
        self.character_dropdown["menu"].delete(0, tk.END)
        characters = ["Choose Character"]
        if server not in self.window.characters_frame.servers.values():
            return
        for data in self.window.characters_frame.characters:
            character_server = self.window.characters_frame.servers[data[0]]
            if character_server != server:
                continue
            characters.append(data[1])
        for character in characters:
            self.character_dropdown["menu"].add_command(
                label=character, command=lambda value=character: self.character.set(value)
            )

    @property
    def character_data(self):
        """Return Character Data tuple for selected character or None"""
        if "Choose" in self.server.get() or "Choose" in self.character.get():
            return None
        reverse_servers = {value: key for key, value in self.window.characters_frame.servers.items()}
        server = reverse_servers[self.server.get()]
        return server, self.character.get()
