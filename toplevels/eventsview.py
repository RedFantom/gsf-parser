# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk

import tkinter.ttk as ttk
import variables
from parsing.lineops import print_event


class EventsView(tk.Toplevel):
    def __init__(self, window, spawn, player):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Events for spawn on %s of match started at %s" % (
            variables.spawn_timing, variables.match_timing))
        self.listbox = tk.Listbox(self, width=100, height=15, font=("Consolas", 10))
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.grid(column=1, row=0, sticky="nswe")
        self.scroll.grid(column=2, row=0, sticky="nswe")
        self.resizable(width=False, height=False)
        for line in spawn:
            event = print_event(line, variables.spawn_timing, player)
            if not isinstance(event, tuple):
                pass
            if event is not None:
                self.listbox.insert(tk.END, event[0])
                self.listbox.itemconfig(tk.END, fg=event[2], bg=event[1])
