"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
# Own modules
from parsing.lineops import print_event


class EventsView(tk.Toplevel):
    def __init__(self, window, spawn, player, spawn_timing, match_timing):
        tk.Toplevel.__init__(self, window)
        if isinstance(spawn_timing, datetime):
            spawn_timing = spawn_timing.strftime("%H:%M:%S")
        if isinstance(match_timing, datetime):
            match_timing = match_timing.strftime("%H:%M")
        self.title("GSF Parser: Events for spawn on %s of match started at %s" % (
            spawn_timing, match_timing))
        self.listbox = tk.Listbox(self, width=100, height=15, font=("Consolas", 10))
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.grid(column=1, row=0, sticky="nswe")
        self.scroll.grid(column=2, row=0, sticky="nswe")
        self.resizable(width=False, height=False)
        for line in spawn:
            event = print_event(line, spawn_timing, player)
            if not isinstance(event, tuple):
                pass
            if event is not None:
                self.listbox.insert(tk.END, event[0])
                self.listbox.itemconfig(tk.END, fg=event[2], bg=event[1])
