"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from collections import OrderedDict
from datetime import datetime
from queue import Queue
# Packages
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from numpy import array
# Project Modules
from data.icons import ICONS
from parsing import Parser
from utils import open_icon_pil
from widgets.overlays.gtk import GtkOverlay
import variables


class GtkEventsOverlay(GtkOverlay):
    """Gtk Window implementation of the EventsOverlay"""

    def __init__(self, _, timeout=10, location=(0, 0), **__):
        """
        :param _: Ignored master widget
        :param timeout: Amount of time an event is displayed in seconds
        :param location: Location tuple for the window in pixels0
        :param __: Other keyword arguments are ignored
        """
        Gtk.Window.__init__(self)
        self.connect("destroy", Gtk.main_quit)
        self.move(*location)
        self._grid = Gtk.Grid()
        self.add(self._grid)
        self.init_window_attr()
        self.show_all()

        self._icons = {name: open_icon_pil(path, (24, 24)) for name, path in ICONS.items()}

        self._timeout = timeout
        self._labels = OrderedDict()
        self._queue = Queue()

    def grid(self, label: Gtk.Grid, row: int):
        """Insert a widget into the Grid"""
        self._grid.attach(label, 0, row, 1, 1)

    def clear_grid(self):
        """Remove all widgets from the Grid"""
        for i in range(len(self._labels)):
            self._grid.remove_row(i)

    def process_event(self, event: dict, active_id: str):
        """Process a given event dictionary for display"""
        if event is None:
            return
        event_type = Parser.get_event_category(event, active_id)
        widget: Gtk.Grid = self.generate_widget(event, event_type)
        if widget is None:
            return
        time = datetime.combine(datetime.now().date(), event["time"].time())
        self._queue.put((time, widget))

    def match_end(self):
        """Clear all widgets and events in queue for processing"""
        with self._queue.mutex:
            self._queue.queue.clear()

    def generate_widget(self, event: dict, event_type: str) -> (Gtk.Grid, None):
        """Build a Label widget for an event"""
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

        label, image = Gtk.Label(), Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_array(array(image), GdkPixbuf.Colorspace.RGB, 8)
        image.set_from_pixbuf(pixbuf)

        label.set_use_markup(True)
        label.set_markup("<b><span color=\"{}\" face=\"Consolas\" size=\"10\">{}</span></b>".format(
            variables.colors[event_type], "{:<16}{}".format(event["ability"], amount)))

        grid = Gtk.Grid()
        grid.attach(label, 2, 1, 1, 1)
        grid.attach(image, 1, 1, 1, 1)

        return grid

    def update_events(self):
        """Update the events shown in the Overlay"""
        while not self._queue.empty():
            event, label = self._queue.get()
            self._labels[event] = label
        if len(self._labels) == 0:
            return
        # Process out of time events
        for event in list(self._labels.keys()):
            elapsed = abs((datetime.now() - event).total_seconds())
            if elapsed > self._timeout:
                self._labels[event].destroy()
                del self._labels[event]
                continue
        self.clear_grid()
        for index, label in reversed(list(enumerate(self._labels.values()))):
            self.grid(label, index)
            if index > 5:
                break
