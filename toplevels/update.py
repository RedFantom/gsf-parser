"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk
import webbrowser


class UpdateWindow(tk.Toplevel):
    """Small Window  to display a GSF Parser update notification"""

    def __init__(self, master: tk.Tk, version: str):
        """
        :param master: MainWindow instance
        :param version: Version tag string
        """
        tk.Toplevel.__init__(self, master)
        self.explanation_label = ttk.Label(
            self, text="A new version for the GSF Parser is available! You can now "
                       "download GSF Parser {0}, so you can use the latest features, "
                       "benefit from optimizations and get rid of annoying bugs.".format(version),
            justify=tk.LEFT, wraplength=200)
        self.close_button = ttk.Button(self, text="Close", command=self.destroy)
        self.open_button = ttk.Button(self, text="Open", command=lambda: webbrowser.open(
            "https://github.com/RedFantom/GSF-Parser/releases/tag/{0}".format(version)))
        self.explanation_label.grid(column=0, row=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.close_button.grid(column=0, row=1, sticky="nswe", padx=5, pady=(0, 5))
        self.open_button.grid(column=1, row=1, sticky="nswe", padx=5, pady=(0, 5))
