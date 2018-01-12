# This file contains utility code NOT written by RedFantom or Daethyra, though it may have been edited to suit a
# particular purpose better. This code was written by others. For the credits, see the block-comment in each class.
# This file is excluded from the copyright of RedFantom, Daethyra and Sprigellania, but the code in this file
# IS redistributed under the license found in LICENSE.md, so you only have to accept one License when using the
# software.
import tkinter.ttk as ttk
import tkinter as tk
from PIL import Image, ImageTk
from utils.directories import get_assets_directory
import os


class ToggledFrame(ttk.Frame):
    """
    A frame with a toggle button to show or hide the contents. Edited by RedFantom for image support instead of a '+'
    or '-' and other toggling options.
    Author: Onlyjus
    License: None
    Source: http://stackoverflow.com/questions/13141259
    """

    def __init__(self, parent, text="", labelwidth=25, callback=None, **options):
        ttk.Frame.__init__(self, parent, **options)
        self.show = tk.BooleanVar()
        self.show.set(False)
        self.title_frame = ttk.Frame(self)
        self.title_frame.grid(sticky="nswe")
        self.callback = callback
        closed_img = Image.open(os.path.join(get_assets_directory(), "gui", "closed.png"))
        self._closed = ImageTk.PhotoImage(closed_img)
        open_img = Image.open(os.path.join(get_assets_directory(), "gui", "open.png"))
        self._open = ImageTk.PhotoImage(open_img)
        self.toggle_button = ttk.Checkbutton(self.title_frame, width=labelwidth, image=self._closed,
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
