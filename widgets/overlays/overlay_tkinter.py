"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk
from variables import settings
import sys


class TkinterOverlay(tk.Toplevel):
    """
    A class that can display text on the screen through the default
    Tkinter Toplevel interface.
    """

    def __init__(self, position, text_variable, font=("default", 11, "bold"), master=None, opacity=255):
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
        """Configure window with Tkinter window attributes"""
        self.update_geometry()
        self.wm_attributes("-topmost", True)
        self.wm_overrideredirect(True)
        if hasattr(self, "text_label"):
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
