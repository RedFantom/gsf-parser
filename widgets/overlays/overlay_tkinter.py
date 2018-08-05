"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk
from widgets.overlays.overlay import Overlay
from variables import settings
import sys


class TkinterOverlay(Overlay, tk.Toplevel):
    """
    A class that can display text on the screen through the default
    Tkinter Toplevel interface.
    """

    def __init__(self, position, text_variable, wait_time=20, font=("default", 11, "bold"), master=None,
                 color=(255, 255, 0), opacity=255, auto_init=True):
        tk.Toplevel.__init__(self, master)
        self._master = master
        self._opacity = opacity
        self._color = settings["realtime"]["overlay_text"]
        self._text_variable = text_variable
        self._position = position
        self._font = font if isinstance(font, tuple) else (font["family"], font["size"])
        self.text_label = ttk.Label(
            self, textvariable=self._text_variable, font=self._font, background="white", foreground=self._color)
        # Setup window
        self.setup_window()
        # Create label
        self.text_label.grid()

    def setup_window(self):
        """
        Configure the window with the options given in instance attributes
        """
        self.update_geometry()
        self.wm_attributes("-topmost", True)
        self.wm_overrideredirect(True)
        self.text_label.config(background="darkblue")
        tk.Toplevel.config(self, background="darkblue")
        if sys.platform == "linux":
            print("[TkinterOverlay] Setting special Overlay attributes for Linux.")
            self.wm_attributes("-alpha", 0.75)
        else:  # Windows
            print("[TkinterOverlay] Setting special Overlay attributes for Windows.")
            self.wm_attributes("-transparentcolor", "darkblue")

    def update_geometry(self):
        size = self.text_label.winfo_reqwidth(), self.text_label.winfo_reqheight()
        self.wm_geometry("{}x{}+{}+{}".format(*size, *self._position))

    def update_text(self, text):
        self._text_variable.set(text)
        self.update_geometry()

    def initialize_window(self):
        self.wm_deiconify()

    def update(self):
        tk.Toplevel.update(self)

    def destroy(self):
        tk.Toplevel.destroy(self)

    def cget(self, key):
        if key == "opacity":
            return self._opacity
        elif key == "color":
            return self._color
        elif key == "text_variable":
            return self._text_variable
        elif key == "position":
            return self._position
        elif key == "font":
            return self._font
        elif key == "master":
            return self._master
        else:
            return tk.Toplevel.cget(self, key)

    def config(self, **kwargs):
        self._position = kwargs.pop("position", self._position)
        self._font = kwargs.pop("font", self._font)
        self._opacity = kwargs.pop("opacity", self._opacity)
        if isinstance(self._font, dict):
            self._font = (self._font["family"], self._font["size"])
        self.setup_window()
        return tk.Toplevel.config(**kwargs)

    @property
    def rectangle(self):
        geometry = self.wm_geometry()
        coordinates, width, height = geometry.split("+")
        x, y = coordinates.split("x")
        width, height, x, y = int(width), int(height), int(x), int(y)
        return x, y, x + width, y + height

    @property
    def position(self):
        return self.rectangle[0], self.rectangle[1]



