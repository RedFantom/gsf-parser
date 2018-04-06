"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import sys
from queue import Queue
from collections import OrderedDict
from datetime import datetime
# UI Libraries
import tkinter as tk
# Project Modules
from data.icons import icons
from parsing import Parser
from utils.utilities import open_icon
import variables


class EventOverlay(tk.Toplevel):
    """
    Overlay with shifting events view of certain types of events that can be
    observed during the match.
    """
    def __init__(self, master, timeout=4, types=None, bg="darkblue", location=(0, 0), after=100):
        """
        :param master: master widget
        :param timeout: Amount of time an event is displayed in seconds
        :param types: list of event types displayed
        :param bg: Background color of the window
        :param location: Location tuple for the window in pixels
        """
        tk.Toplevel.__init__(self, master)
        if types is None:
            types = ["selfheal", "healing", "dmgt_sec", "dmgt_pri", "selfdmg"]

        # Arguments
        self._types = types
        self._background = bg
        self._timeout = timeout
        self._location = location
        self._after = after
        # Attributes
        self._labels = OrderedDict()
        self._queue = Queue()
        self._icons = {name: open_icon(path) for name, path in icons.items()}
        self._destroyed = False
        self._after_id = None

        self._parent = tk.Frame(self, background=self._background)

        self.setup_window()
        self.grid_widgets()

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
        self._parent.grid(sticky="nswe")

    def setup_window(self):
        """
        Configure the window manager attributes specifically supported by the
        platform.
        Windows: -transparentcolor, makes window fully transparent
        Linux: -alpha, makes window transparent by a certain amount,
            inherited by child widgets
        """
        self.update_geometry()
        self.wm_attributes("-topmost", True)
        self.wm_overrideredirect(True)
        self.config(background=self._background)
        if sys.platform == "linux":
            print("[EventOverlay] Setting special Overlay attributes for Linux.")
            self.wm_attributes("-alpha", 0.75)
        else:  # Windows
            print("[EventOverlay] Setting special Overlay attributes for Windows.")
            self.wm_attributes("-transparentcolor", self._background)

    def update_geometry(self):
        """Update the geometry of the window"""
        size = self._parent.winfo_reqwidth(), self._parent.winfo_reqheight()
        self.wm_geometry("{}x{}+{}+{}".format(*size, *self._location))

    def process_event(self, event: dict, active_id: str):
        """Process a given event dictionary for display"""
        event_type = Parser.get_event_category(event, active_id)
        if event_type not in self._types:
            return False
        self._queue.put((event, self.generate_widget(event, event_type)))

    def update_events(self):
        """Update the events shown in the Overlay"""
        if self._destroyed is True:
            return False
        while not self._queue.empty():
            event, label = self._queue.get()
            self._labels[event] = label
        # Process out of time events
        for event in list(self._labels.keys()):
            if (datetime.now() - event["time"]).total_seconds() > self._timeout:
                self._labels[event].grid_forget()
                self._labels[event].destroy()  # Prevent memory leak
                del self._labels[event]
        # Grid the events
        for index, label in enumerate(self._labels.values()):
            label.grid(row=index, column=0, sticky="nsw", padx=5, pady=(0, 5))
        # Create after command
        self._after_id = self.after(self._after, self.update_events)

    def match_end(self):
        """Clear all widgets"""
        while not self._queue.empty():
            self._queue.get()
        self._labels.clear()
        self.update_geometry()

    def generate_widget(self, event: dict, event_type: str):
        """Build a abel widget for an event"""
        return tk.Label(
            self, image=self._icons[event["ability"]], compound=tk.LEFT,
            text="{} - {}".format(event["ability"].ljust(24), event["amount"].ljust(4)),
            background=self._background, foreground=variables.colors[event_type])

    def destroy(self):
        """Set destroyed attribute and destroy"""
        self._destroyed = True
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        tk.Toplevel.destroy(self)
