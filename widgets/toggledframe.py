# This file contains utility code NOT written by RedFantom or Daethyra, though it may have been edited to suit a
# particular purpose better. This code was written by others. For the credits, see the block-comment in each class.
# This file is excluded from the copyright of RedFantom, Daethyra and Sprigellania, but the code in this file
# IS redistributed under the license found in LICENSE, so you only have to accept one License when using the
# software.
import ttk

try:
    import mttkinter.mtTkinter as tk
except ImportError:
    import Tkinter as tk
from PIL import Image, ImageTk
import os


class ToggledFrame(ttk.Frame):
    """
    A frame with a toggle button to show or hide the contents. Edited by RedFantom for image support instead of a '+'
    or '-'.
    Author: Onlyjus
    License: None
    Source: http://stackoverflow.com/questions/13141259/expandable-and-contracting-frame-in-tkinter
    """

    def __init__(self, parent, text="", labelwidth=25, **options):
        ttk.Frame.__init__(self, parent, **options)
        self.show = tk.IntVar()
        self.show.set(0)
        self.title_frame = ttk.Frame(self)
        self.title_frame.grid(sticky=tk.N + tk.S + tk.W + tk.E)
        closed_img = Image.open(os.path.abspath(os.path.dirname(os.path.realpath(__file__))
                                                + "\\..\\assets\\gui\\closed.png"))
        self.closed = ImageTk.PhotoImage(closed_img)
        open_img = Image.open(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +
                                              "\\..\\assets\\gui\\open.png"))
        self.open = ImageTk.PhotoImage(open_img)
        # ttk.Label(self.title_frame, text=text, font=("Calibri", 11), width=labelwidth).\
        #     pack(side="left", fill="x", expand=1)
        self.toggle_button = ttk.Checkbutton(self.title_frame, width=labelwidth, image=self.closed,
                                             command=self.toggle, variable=self.show, style='Toolbutton',
                                             text=text, compound=tk.LEFT)
        self.toggle_button.grid(sticky=tk.N + tk.S + tk.W + tk.E)
        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.grid(sticky=tk.N + tk.S + tk.W + tk.E)
            self.toggle_button.configure(image=self.open)
        else:
            self.sub_frame.grid_forget()
            self.toggle_button.configure(image=self.closed)
