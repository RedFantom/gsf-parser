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
import re


class HoverInfo(tk.Tk):
    """
    Author: BioDataSorter
    License: MIT License
    Source: https://github.com/BioDataSorter/BioDataSorter

    Usage: Bind methods to target widget with any other commands.
    hover_instance = HoverText(parent, "Hi\nHello\nPython is awesome!")
    widget.bind('<Enter>', lambda e: (hover_instance.enter(e),
           multiple commands =>       do_something_else(hover_instance)))
    target_widget.bind('<Leave>', hover_instance.leave)
    parent.bind('<Motion>', hover_instance.motion)
    """

    def __init__(self, parent, text="", width=70):
        tk.Tk.__init__(self)
        self.overrideredirect(True)
        self.parent = parent
        self.parent.bind("<Enter>", self.enter)
        self.parent.bind("<Leave>", self.leave)
        if not isinstance(text, str):
            error_msg = 'Trying to initialize a Hover Menu with a non ' \
                        'string type: '
            raise TypeError(error_msg + text.__class__.__name__)

        text_lines = re.split('\n', text)
        # self.width = max([len(text_line) for text_line in text_lines]) * 7
        self.labels = []
        for t in text_lines:
            self.labels.append(ttk.Label(self, text=t, justify=tk.LEFT, wraplength=width * 7))
        self.width = 0
        for i, label in enumerate(self.labels):
            label.grid(row=i, sticky=tk.N + tk.W)
            if len(label["text"]) * 6 > self.width:
                self.width = len(label["text"]) * 6

        self.withdraw()
        self._displayed = False

    def enter(self, _):
        self._displayed = True
        self.deiconify()
        self.motion(_)

    def leave(self, event):
        # extra check in case mouse moves over top frame instead of hovering
        # over word cloud
        if self._displayed:
            self._displayed = False
            self.withdraw()

    def motion(self, _):
        # absolute positioning instead of compared to widget
        x = self.winfo_pointerx()
        y = self.winfo_pointery()  # b/c geometry uses absolute positioning
        self.geometry("%dx%d+%d+%d" % (self.winfo_reqwidth(),
                                       self.winfo_reqheight(),
                                       x + 2,
                                       y + 2))
