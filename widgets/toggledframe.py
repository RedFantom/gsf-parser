"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter.ttk as ttk
import tkinter as tk
from utils import open_icon
import sys


class ToggledFrame(ttk.Frame):
    """
    A frame with a toggle button to show or hide the contents. Edited
    by RedFantom for image support instead of a '+' or '-' and other
    toggling options.
    Author: Onlyjus
    License: None
    Source: http://stackoverflow.com/questions/13141259
    """

    WIDTH = 25 if sys.platform == "win32" else 18

    def __init__(self, parent, text="", labelwidth=None, callback=None, **options):
        if labelwidth is None:
            labelwidth = ToggledFrame.WIDTH
        ttk.Frame.__init__(self, parent, **options)
        self.show = tk.BooleanVar()
        self.show.set(False)
        self.title_frame = ttk.Frame(self)
        self.title_frame.grid(sticky="nswe")
        self.callback = callback
        self._closed = open_icon("closed.png", folder="gui")
        self._open = open_icon("open.png", folder="gui")
        self.toggle_button = ttk.Checkbutton(
            self.title_frame, width=labelwidth, image=self._closed,
            command=self.toggle, variable=self.show, style='Toolbutton',
            text=text, compound=tk.LEFT)
        self.toggle_button.grid(sticky="nswe", padx=5, pady=(0, 5))
        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)
        self.interior = self.sub_frame
        self.called = False

    def toggle(self, callback=True):
        """
        Toggle the state of the ToggledFrame.
        """
        self.open() if self.show.get() else self.close()
        if callback is True and callable(self.callback):
            self.callback(self, self.show.get())

    def open(self):
        self.sub_frame.grid(sticky="nswe", padx=5, pady=(0, 5))
        self.toggle_button.configure(image=self._open)
        self.show.set(True)

    def close(self):
        self.sub_frame.grid_forget()
        self.toggle_button.configure(image=self._closed)
        self.show.set(False)

    def set_width(self, width: int):
        """Configure the width in pixels of the header Label"""
        self.toggle_button.config(width=int(ToggledFrame.WIDTH / 152 * width) - 1)
        for name in self.interior.children:
            widget = self.interior.nametowidget(name)
            widget.configure(width=int(ToggledFrame.WIDTH / 152 * width) - 10)
        self.configure(width=width)
