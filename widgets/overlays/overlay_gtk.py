"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom
"""
# Standard Library
import os
from threading import Thread
# Packages
import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # python3-gi
# Project Modules
from utils.directories import get_assets_directory


class GtkOverlay(Gtk.Window):
    """Window that represents the actual Overlay and draws the text"""

    def __init__(self, position: tuple, string, standard=True, master=None):
        """Initialize window and attributes"""
        Gtk.Window.__init__(self)
        Thread.__init__(self)
        self._string = string
        self.connect("destroy", Gtk.main_quit)
        self.move(*position)
        self._grid = Gtk.Grid()
        self.add(self._grid)
        if standard is True:
            self._init_label()
        self.init_window_attr()
        self.show_all()

    def _init_label(self):
        self._label = Gtk.Label("Placeholder")
        self._label.set_justify(Gtk.Justification.LEFT)
        self._grid.attach(self._label, 0, 0, 1, 1)

    def init_window_attr(self):
        """Initialize Window attributes"""
        # Initialize Transparency Handler
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            print("[GtkOverlay] Transparency available")
            self.set_visual(visual)
        # Initialize other attributes
        self.set_border_width(0)
        self.set_app_paintable(True)
        self.set_resizable(False)
        self.connect("draw", self._redraw)
        self.connect("destroy", Gtk.main_quit)
        self.set_keep_above(True)
        self.set_default_icon_from_file(
            os.path.join(get_assets_directory(), "logos", "icon_green.ico"))
        self.set_decorated(False)
        self.show_all()

    def show(self):
        """Show the Overlay"""
        self.set_keep_above(True)

    def hide(self):
        """Hide the Overlay"""
        self.set_keep_below(True)

    def update_text(self, string: str):
        """Update the text in the Label"""
        if not hasattr(self, "_label"):
            raise RuntimeError("This is not a standard GtkOverlay")
        self._label.set_use_markup(True)
        self._label.set_markup("<b><span color=\"yellow\">{}</span></b>".format(string))
        Gtk.main_iteration()

    def destroy(self):
        """Destroy and run an interation immediately afterwards"""
        Gtk.Window.destroy(self)
        Gtk.main_iteration()

    @staticmethod
    def _redraw(_: Gtk.Widget, cr):
        """Redraw this window with transparency"""
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)


if __name__ == '__main__':
    overlay = GtkOverlay((0, 0), None)
    overlay.update_text("Hello")
    Gtk.main()
