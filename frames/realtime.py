"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from multiprocessing import Event, Pipe
import psutil
import os
import sys
import time
from typing import Tuple, Any
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Project Modules
from network.discord import DiscordClient
from parsing.file import FileParser
from toplevels.minimap import MiniMap
from toplevels.event_overlay import EventOverlay
from utils.swtor import get_swtor_screen_mode
from utils.admin import check_privileges
from widgets.time_view import TimeView
from variables import settings


class RealTimeFrame(ttk.Frame):
    """
    A Frame that contains all the necessary widgets to control a
    RealTimeParser instance.
    """

    DATA_STR_BASE = "Slow screen parsing features:\n\n{}"

    def __init__(self, master, window):
        ttk.Frame.__init__(self, master)

        self.window = window
        self.after_id: int = None
        self.alive_id: int = None
        self.parser: FileParser = None
        self.overlay = None
        self.overlay_string: tk.StringVar = None
        self.event_overlay: EventOverlay = None
        self.exit: Event = Event()
        self.pipe = None
        self._pids = [os.getpid()]

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
            self, textvariable=self.data, font=("default", 9), justify=tk.LEFT,
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
        self.after(1000, self.update_cpu_usage)

    def grid_widgets(self):
        """Put all widgets into place"""
        self.server_dropdown.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.character_dropdown.grid(row=1, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.parsing_control_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.minimap_checkbox.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)
        self.minimap_name_entry.grid(row=1, column=1, sticky="nsw", padx=5, pady=(0, 5))
        self.minimap_address_entry.grid(row=2, column=1, sticky="nsw", padx=5, pady=(0, 5))

        self.data_label.grid(row=0, column=2, rowspan=3, columnspan=2, sticky="nwe", padx=(0, 5), pady=5)
        self.time_view.grid(row=3, column=0, columnspan=4, sticky="nswe", padx=5, pady=5)

        self.watching_label.grid(row=4, column=0, columnspan=4, sticky="nw", padx=5, pady=5)
        self.cpu_label.grid(row=4, column=2, sticky="nw", padx=5, pady=5)

    def check_parser_start(self) -> bool:
        """Check if a RealTimeParser can be started"""
        if self.character_data is None:
            messagebox.showinfo("Info", "Please select a valid character using the dropdowns.")
            return False
        if settings["realtime"]["overlay"] or settings["screen"]["enabled"]:
            if get_swtor_screen_mode() is False:
                return False
        if "Mouse and Keyboard" in settings["screen"]["features"] and sys.platform != "linux":
            if not check_privileges():
                messagebox.showinfo(
                    "Info", "Mouse and keyboard parsing is enabled, but the GSF Parser is not running as "
                            "administrator, which prevents reading input from the SWTOR window. Please restart the "
                            "GSF Parser as administrator for this feature to work.")
        return True

    def start_parsing(self):
        """Start the parsing process and open the Overlay"""
        if self.check_parser_start() is False:
            return
        self._pids.append(os.getpid())
        self.parsing_control_button.config(state=tk.DISABLED)
        self.parsing_control_button.update()
        try:
            characters = self.window.characters_frame.characters.copy()
            self.pipe, conn = Pipe()
            self.parser = FileParser(conn, self.exit, characters, self.character_data)
        except Exception as e:
            messagebox.showerror("Error", "Failed to initialize RealTimeParser.")
            raise
        # Change Button state
        self.parsing_control_button.config(text="Stop Parsing", command=self.stop_parsing)
        self.watching_stringvar.set("Waiting for a CombatLog...")
        self.open_overlay()
        self.parser.start()
        self.check_alive()
        self.update_from_pipe()
        self.parsing_control_button.config(state=tk.NORMAL)

    def stop_parsing(self):
        """Stop the parsing process"""
        self.parsing_control_button.config(state=tk.DISABLED)
        self.parsing_control_button.update()
        if self.minimap_enabled.get() is True and self.minimap is not None:
            self.minimap.destroy()
        self.close_overlay()
        self.exit.set()
        self.parsing_control_button.config(text="Start Parsing", command=self.start_parsing)
        time.sleep(0.1)
        try:
            self.parser.join(timeout=2)
        except Exception as e:
            messagebox.showerror("Error", "While real-time parsing, the following error occurred:\n\n{}".format(e))
        self.exit.clear()
        self.watching_stringvar.set("Watching no file...")
        print("[RealTimeFrame] RealTimeParser reference count: {}".format(sys.getrefcount(self.parser)))
        self.parser = None
        self.close_overlay()
        DiscordClient().send_recent_files(self.window)
        self.parsing_control_button.config(state=tk.NORMAL)
        self.data.set(self.DATA_STR_BASE.format("Not real-time parsing\n"))
        self._pids.clear()
        self._pids.append(os.getpid())

    def update_from_pipe(self):
        """Read from the data pipe and update attributes accordingly"""
        done = 0
        while self.pipe.poll():
            try:
                data: Tuple[str, Any] = self.pipe.recv()
            except EOFError:
                break
            self.process_pipe_data(data)
            done += 1
            if done == 10:
                break
        self.after_id = self.after(50, self.update_from_pipe)

    def process_pipe_data(self, data: Tuple[str, Any]):
        """Process the data received from the FileParser pipe"""
        type, data = data
        if type == "string":
            if self.overlay is not None:
                self.overlay.update_text(data)
        elif type == "perf":
            self.data.set(data)
        elif type == "error":
            messagebox.showerror("Error", "The RealTimeParser encountered an error: {}.".format(data))
        elif type == "event":
            event, player, active_ids, start = data
            self.event_callback(event, player, active_ids, start)
        elif type == "match":
            self.match_callback()
        elif type == "spawn":
            self.spawn_callback()
        elif type == "file":
            self.file_callback(data)
        elif type == "pid":
            self._pids.append(data)
        else:
            print("[RealTimeFrame] Unhandled Pipe data: {}".format((type, data)))

    def file_callback(self, file_name):
        """LogStalker new file callback to set file name in label"""
        print("[RealTimeParser] New file {}".format(file_name))
        self.watching_stringvar.set("Watching: {}".format(file_name))

    def match_callback(self):
        """Callback for the RealTimeParser to clear the TimeView"""
        self.time_view.delete_all()

    def spawn_callback(self):
        """Callback for the RealTimeParser to clear the TimeView"""
        self.time_view.delete_all()

    def event_callback(self, event, player_name, active_ids, start_time):
        """RealTimeParser event callback for TimeView insertion"""
        self.time_view.insert_event(event, player_name, active_ids, start_time)
        self.time_view.yview_moveto(1.0)
        if self.event_overlay is not None:
            self.event_overlay.process_event(event, active_ids)

    def update_cpu_usage(self):
        """Update the CPU usage Label every two seconds"""
        cpu_percent, memory = 0, 0
        for pid in self._pids:
            process = psutil.Process(pid)
            cpu_percent += process.cpu_percent()
            memory += process.memory_full_info().rss / 1024 ** 2
        string = "CPU: {:4.1f}%".format(cpu_percent)
        string += ", Memory: {:5.1f}MiB".format(memory)
        self.after(2000, self.update_cpu_usage)
        self.cpu_stringvar.set(string)

    def open_overlay(self):
        """Open an overlay if the settings given by the user allow for it"""
        if settings["realtime"]["overlay"] is False:
            return
        from widgets.overlays import Overlay
        # Generate arguments for Overlay.__init__
        position = settings["realtime"]["overlay_position"]
        x, y = position.split("y")
        x, y = int(x[1:]), int(y)
        self.overlay_string = tk.StringVar(self)
        self.overlay = Overlay((x, y), self.overlay_string, master=self.window)
        self.overlay.start()
        self.open_event_overlay()

    def open_event_overlay(self):
        """Open an EventOverlay if it is enabled in settings"""
        if settings["event"]["enabled"] is False:
            return
        x, y = settings["event"]["position"].split("y")
        x, y = int(x[1:]), int(y)
        self.event_overlay = EventOverlay(self.window, location=(x, y))

    def close_overlay(self):
        """Close the overlay"""
        if self.overlay is not None:
            self.overlay.destroy()
        self.overlay = None
        if self.event_overlay is not None:
            self.event_overlay.match_end()
            self.event_overlay.destroy()
            self.event_overlay = None

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
            self.alive_id = None
            return
        if self.parser.is_alive() is False:
            self.stop_parsing()
            return
        self.alive_id = self.after(100, self.check_alive)
