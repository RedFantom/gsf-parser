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
from data.icons import ICONS
from parsing import Parser
from utils.utilities import open_icon
import variables


class EventOverlay(tk.Toplevel):
    """
    Overlay with shifting events view of certain types of events that
    can be observed during the match.
    """
    def __init__(self, master, timeout=10, bg="darkblue", location=(0, 0), after=100):
        """
        :param master: master widget
        :param timeout: Amount of time an event is displayed in seconds
        :param bg: Background color of the window
        :param location: Location tuple for the window in pixels
        """
        print("[EventOverlay] Initializing")
        tk.Toplevel.__init__(self, master)

        # Arguments
        self._background = bg
        self._timeout = timeout
        self._location = location
        self._after = after
        # Attributes
        self._labels = OrderedDict()
        self._queue = Queue()
        self._icons = {name: open_icon(path, (24, 24)) for name, path in ICONS.items()}
        self._destroyed = False

        self._parent = tk.Frame(self, background=self._background)

        self.setup_window()
        self.grid_widgets()
        self.update_events()

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
        self.wm_attributes("-topmost", True)
        self.wm_overrideredirect(True)
        self.config(background="darkblue")
        if sys.platform == "linux":
            print("[EventOverlay] Setting special Overlay attributes for Linux.")
            self.wm_attributes("-alpha", 0.75)
        else:  # Windows
            print("[EventOverlay] Setting special Overlay attributes for Windows.")
            self.wm_attributes("-transparentcolor", self._background)
        self.wm_geometry("+{}+{}".format(*self._location))

    def process_event(self, event: dict, active_id: str):
        """Process a given event dictionary for display"""
        if event is None:
            return
        event_type = Parser.get_event_category(event, active_id)
        widget = self.generate_widget(event, event_type)
        if widget is None:
            return
        time = datetime.combine(datetime.now().date(), event["time"].time())
        self._queue.put((time, widget))

    def update_events(self):
        """Update the events shown in the Overlay"""
        if self._destroyed is True:
            return False
        while not self._queue.empty():
            event, label = self._queue.get()
            self._labels[event] = label
        if len(self._labels) == 0:
            return
        # Process out of time events
        for time in list(self._labels.keys()):
            elapsed = abs((datetime.now() - time).total_seconds())
            if elapsed > self._timeout:
                self._labels[time].grid_forget()
                self._labels[time].destroy()  # Prevent memory leak
                del self._labels[time]
                continue
            self._labels[time].grid_forget()
        # Grid the events
        gridded = 0
        for index, label in reversed(list(enumerate(self._labels.values()))):
            label.grid(row=index, column=0, sticky="nsw", padx=5, pady=(0, 2))
            gridded += 1
            if gridded == 5:
                break

    def match_end(self):
        """Clear all widgets"""
        print("[EventOverlay] Match end.")
        while not self._queue.empty():
            self._queue.get()
        self._labels.clear()

    def generate_widget(self, event: dict, event_type: str) -> (tk.Label, None):
        """Build a abel widget for an event"""
        now = datetime.now()
        elapsed = (now - datetime.combine(now.date(), event["time"].time())).total_seconds()
        if elapsed > self._timeout:
            return None
        if "AbilityActivate" not in event["effect"] and "Damage" not in event["effect"]:
            return None
        ability = event["ability"]
        if ability not in self._icons:
            ability = ability.split(":")[0]
        if ability not in self._icons or ability in Parser.IGNORABLE:
            return None
        amount = "" if event["amount"] in ("", "0", 0) else " - {}".format(event["amount"])
        label = tk.Label(
            self._parent, image=self._icons[ability], compound=tk.LEFT,
            text="{:<16}{}".format(event["ability"], amount),
            background=self._background, foreground=variables.colors[event_type][0],
            font=("Consolas", 10, "bold"))
        return label

    def destroy(self):
        """Set destroyed attribute and destroy"""
        self._destroyed = True
        tk.Toplevel.destroy(self)
