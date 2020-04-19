"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import threading
import time
import psutil
import os
import sys
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Project Modules
from network.discord import DiscordClient
from parsing.realtime import RealTimeParser
from toplevels.minimap import MiniMap
from widgets.events import EventOverlay
from utils.swtor import get_swtor_screen_mode
from utils.admin import check_privileges
from widgets.results.time_view import TimeView
from variables import settings


class RealTimeFrame(ttk.Frame):
    """
    A Frame that contains all the necessary widgets to control a
    RealTimeParser instance.
    """

    DATA_STR_BASE = "Slow screen results features:\n\n{}"

    def __init__(self, master, window):
        ttk.Frame.__init__(self, master)
        """
        Attributes 
        """
        self.window = window
        self.after_id = None
        self._rtp_id = None
        self.parser = None
        self.overlay = None
        self.overlay_after_id = None
        self.data_after_id = None
        self._event_overlay = None

        # Watching Label
        self.watching_stringvar = tk.StringVar(self, value="Watching no file...")
        self.watching_label = ttk.Label(self, textvariable=self.watching_stringvar, justify=tk.LEFT)
        self.cpu_stringvar = tk.StringVar()
        self.cpu_label = ttk.Label(self, textvariable=self.cpu_stringvar, justify=tk.LEFT, font="TkFixedFont")

        # Control widgets
        servers = ("Choose Server",) + tuple(self.window.characters_frame.servers.values())
        self.server, self.character = tk.StringVar(), tk.StringVar()
        self.server_dropdown = ttk.OptionMenu(self, self.server, *servers, command=self.update_characters)
        self.character_dropdown = ttk.OptionMenu(self, self.character, *("Choose Character",))
        self.parsing_control_button = ttk.Button(self, text="Start Parsing", command=self.start_parsing, width=20)

        # Data widgets
        self.data = tk.StringVar(value=self.DATA_STR_BASE.format("Not real-time parsing\n"))
        self.data_label = ttk.Label(
            self, textvariable=self.data, font=("Consolas", 9), justify=tk.LEFT,
            wraplength=300)
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
        self.after(1000, self.update_cpu_usage)

    def grid_widgets(self):
        """Put all widgets into place"""
        self.server_dropdown.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.character_dropdown.grid(row=1, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.parsing_control_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.minimap_checkbox.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)
        self.minimap_name_entry.grid(row=1, column=1, sticky="nsw", padx=5, pady=(0, 5))
        self.minimap_address_entry.grid(row=2, column=1, sticky="nsw", padx=5, pady=5)

        self.data_label.grid(row=0, column=2, rowspan=3, columnspan=2, sticky="nwe", padx=(0, 5), pady=5)
        self.time_view.grid(row=3, column=0, columnspan=4, sticky="nswe", padx=5, pady=5)

        self.watching_label.grid(row=4, column=0, columnspan=4, sticky="nw", padx=5, pady=5)
        self.cpu_label.grid(row=4, column=2, sticky="nw", padx=5, pady=5)

    def check_parser_start(self) -> bool:
        """Check if a RealTimeParser can be started"""
        if self.character_data is None:
            messagebox.showinfo("Info", "Please select a valid character using the dropdowns.")
            return False
        if settings["overlay"]["enabled"] or settings["screen"]["enabled"]:
            if get_swtor_screen_mode() is False:
                return False
        if "Mouse and Keyboard" in settings["screen"]["features"] and sys.platform != "linux":
            if not check_privileges():
                messagebox.showinfo(
                    "Info", "Mouse and keyboard results is enabled, but the GSF Parser is not running as "
                            "administrator, which prevents reading input from the SWTOR window. Please restart the "
                            "GSF Parser as administrator for this feature to work.")
        return True

    def start_parsing(self):
        """Start the results process and open the Overlay"""
        if self.check_parser_start() is False:
            return
        self.parsing_control_button.config(state=tk.DISABLED)
        self.parsing_control_button.update()
        # Setup attributes
        args = (self.window.characters_frame.characters, self.character_data,
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
            "minimap_share": self.minimap_enabled.get(),
            "minimap_user": self.minimap_name.get(),
            "minimap_address": self.minimap_address.get(),
            "minimap_window": self.minimap,
            "rpc": self.window.rpc,
        }
        try:
            self.parser = RealTimeParser(*args, **kwargs)
        except Exception as e:
            messagebox.showerror(
                "Error",
                "An error occurred during the initialization of the RealTimeParser. Please report the error given "
                "below, as well as, if possible, the full stack-trace to the developer.\n\n{}".format(e))
            raise
        # Change Button state
        self.parsing_control_button.config(text="Stop Parsing", command=self.stop_parsing)
        self.watching_stringvar.set("Waiting for a CombatLog...")
        self.open_overlay()
        self.open_event_overlay()
        self.update_data_string()
        # Start the parser
        self.parser.start()
        self._rtp_id = self.after(100, self.check_alive)
        self.data_after_id = self.after(1000, self.update_data_string)
        self.parsing_control_button.config(state=tk.NORMAL)
        print("[RealTimeFrame] Parsing started. Threads: {}".format(threading.enumerate()))

    def stop_parsing(self):
        """Stop the results process"""
        if self.parser._scoreboard_parser is not None:
            messagebox.showwarning("Warning", "Parsing cannot be stopped while results a scoreboard.")
            return
        self.parsing_control_button.config(state=tk.DISABLED)
        self.parsing_control_button.update()
        if self.minimap_enabled.get() is True and self.minimap is not None:
            self.minimap.destroy()
        self.close_overlay()
        self.parser.stop()
        self.parsing_control_button.config(text="Start Parsing", command=self.start_parsing)
        time.sleep(0.1)
        try:
            self.parser.join(timeout=2)
        except Exception as e:
            messagebox.showerror("Error", "While real-time parsing, the following error occurred:\n\n{}".format(e))
            raise
        self.watching_stringvar.set("Watching no file...")
        print("[RealTimeFrame] RealTimeParser reference count: {}".format(sys.getrefcount(self.parser)))
        self.parser = None
        self.close_overlay()
        DiscordClient().send_recent_files(self.window)
        self.window.update_presence()
        self.parsing_control_button.config(state=tk.NORMAL)
        self.data.set(self.DATA_STR_BASE.format("Not real-time parsing\n"))

    def file_callback(self, file_name):
        """LogStalker new file callback to set file name in label"""
        print("[RealTimeParser] New file {}".format(file_name))
        self.watching_stringvar.set("Watching: {}".format(file_name))

    def match_callback(self, match: bool=False):
        """Callback for the RealTimeParser to clear the TimeView"""
        self.time_view.delete_all()

    def spawn_callback(self):
        """Callback for the RealTimeParser to clear the TimeView"""
        self.time_view.delete_all()

    def event_callback(self, event, player_name, active_ids, start_time):
        """RealTimeParser event callback for TimeView insertion"""
        self.time_view.insert_event(event, player_name, active_ids, start_time)
        self.time_view.yview_moveto(1.0)
        if self._event_overlay is not None:
            self._event_overlay.process_event(event, active_ids)

    def update_cpu_usage(self):
        """Update the CPU usage Label every two seconds"""
        string = "CPU: {:4.1f}%".format(self.process.cpu_percent())
        assert isinstance(self.process, psutil.Process)
        memory = self.process.memory_full_info().rss / 1024 ** 2
        string += ", Memory: {:5.1f}MiB".format(memory)
        self.after(2000, self.update_cpu_usage)
        if self.parser is not None and self.parser.diff is not None:
            diff = self.parser.diff
            string += ", Cycle Time: {:.03f}s".format(diff.total_seconds())
        else:
            string += ", Cycle Time: -.---s"
        self.cpu_stringvar.set(string)

    def open_overlay(self):
        """Open an overlay if the settings given by the user allow for it"""
        if settings["overlay"]["enabled"] is False:
            return
        from widgets.overlays import Overlay
        # Generate arguments for Overlay.__init__
        position = settings["overlay"]["position"]
        x, y = position.split("y")
        x, y = int(x[1:]), int(y)
        self.overlay = Overlay((x, y), master=self.window)
        self.update_overlay()

    def open_event_overlay(self):
        """Open an EventOverlay if it is enabled in settings"""
        if settings["event"]["enabled"] is False:
            return
        x, y = settings["event"]["position"].split("y")
        x, y = int(x[1:]), int(y)
        self._event_overlay = EventOverlay(self.window, location=(x, y))

    def update_data_string(self):
        """Update the string in the data label with the parser stats"""
        if self.parser is None:
            if self.data_after_id is not None:
                self.after_cancel(self.data_after_id)
                self.data_after_id = None
            return
        if settings["screen"]["perf"] is False:
            string = self.DATA_STR_BASE.format("Screen feature performance profiling disabled\n")
            self.data.set(string)
            return
        perf = self.parser.perf_string
        self.data_after_id = self.after(1000, self.update_data_string)
        if perf is None:
            return
        elif len(perf) == 0:
            string = self.DATA_STR_BASE.format("No slow screen results features\n")
        else:
            string = self.DATA_STR_BASE.format(perf)
        self.data.set(string)

    def update_overlay(self):
        """Update the Overlay with the text from the RealTimeParser"""
        if self.parser is None or not isinstance(self.parser, RealTimeParser):
            print("[RealTimeFrame] Cancelling Overlay update.")
            return
        string = self.parser.overlay_string
        if string is not None:
            self.overlay.update_text(string)
        self.overlay.update_disabled(self.parser.disabled_string)
        if self._event_overlay is not None:
            assert isinstance(self._event_overlay, EventOverlay)
            self._event_overlay.update_events()
        self.overlay_after_id = self.after(100, self.update_overlay)

    def close_overlay(self):
        """Close the overlay"""
        if self.overlay_after_id is not None:
            self.after_cancel(self.overlay_after_id)
        if self.overlay is not None:
            self.overlay.destroy()
        self.overlay = None
        self.overlay_after_id = None
        if self._event_overlay is not None:
            self._event_overlay.destroy()
            self._event_overlay = None

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
        for character in sorted(characters):
            self.character_dropdown["menu"].add_command(
                label=character, command=lambda value=character: self.character.set(value))

    @property
    def character_data(self):
        """Return Character Data tuple for selected character or None"""
        if "Choose" in self.server.get() or "Choose" in self.character.get():
            return None
        reverse_servers = {value: key for key, value in self.window.characters_frame.servers.items()}
        server = reverse_servers[self.server.get()]
        return server, self.character.get()

    def check_alive(self):
        """Check if the RealTimeParser is still alive"""
        if self.parser is None:
            self._rtp_id = None
            return
        if self.parser.is_alive() is False:
            self.stop_parsing()
            return
        self._rtp_id = self.after(100, self.check_alive)
