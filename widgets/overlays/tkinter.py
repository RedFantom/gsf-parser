"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import sys
from typing import Tuple
# UI Libraries
import tkinter as tk
from tkinter import ttk
# Project Modules
from variables import settings


class TkinterOverlay(tk.Toplevel):
    """Default cross-platform Overlay implementation"""

    def __init__(self, position: Tuple[int, int], master: tk.Tk=None):
        tk.Toplevel.__init__(self, master)
        self._master = master
        self._color = settings["overlay"]["color"]
        self._position = position
        self.text_label = ttk.Label(self, background="white", foreground=self._color)
        self.disabled_label = ttk.Label(self, background="white", foreground="red")
        # Setup window
        self.setup_window()
        # Create label
        self.text_label.grid(row=0, column=0)
        self.disabled_label.grid(row=1, column=0)

    def setup_window(self):
        """Configure window with Tkinter window attributes"""
        self.update_geometry()
        self.wm_attributes("-topmost", True)
        self.wm_overrideredirect(True)
        if sys.platform == "linux" and settings[""]:
            print("[TkinterOverlay] Setting special Overlay attributes for Linux.")
            self.wm_attributes("-alpha", 0.75)
            for w in (self, self.text_label, self.disabled_label):
                w.config(background="darkblue")
        else:  # Windows and transparency
            print("[TkinterOverlay] Setting special Overlay attributes for Windows.")
            self.config(background="white")
            self.wm_attributes("-transparentcolor", "white")

    def update_geometry(self):
        w, h = self.text_label.winfo_reqwidth(), self.text_label.winfo_reqheight()
        w = max(w, self.disabled_label.winfo_reqwidth())
        h += self.disabled_label.winfo_reqheight()
        self.wm_geometry("{}x{}+{}+{}".format(w, h, *self._position))

    def update_text(self, text):
        self.text_label.config(text=text)
        self.update_geometry()

    def update_disabled(self, text: str):
        self.disabled_label.config(text=text)
        self.update_geometry()

    def initialize_window(self):
        self.wm_deiconify()
