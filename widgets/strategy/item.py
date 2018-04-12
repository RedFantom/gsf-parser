"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk, messagebox
from ttkwidgets.color import askcolor
from ttkwidgets.font import FontSelectFrame
# Project Modules
from utils.colors import color_background


class CreateItem(tk.Toplevel):
    """
    Toplevel that provides the widgets required to create a new item
    in a Strategy Phase. Allows for the following attributes to be set:
    - Item text
    - Text font
    - Background color
    """
    def __init__(self, *args, **kwargs):
        """
        :param callback: Callback called upon finalizing the creation
            of the item. Arguments:
            text: str, font: tuple, color: str
        """
        # Arguments
        self.callback = kwargs.pop("callback", None)

        # Toplevel initialziation and Attributes
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add Item")
        self.attributes("-topmost", True)

        # Widget creation
        self.header_label = ttk.Label(self, text="Add a new item", font=("default", 12), justify=tk.LEFT)
        self.text_header = ttk.Label(self, text="Item text", font=("default", 11), justify=tk.LEFT)
        self.text = tk.StringVar()
        self.text_entry = ttk.Entry(self, textvariable=self.text)
        self.background_color = tk.StringVar()
        self.background_color.set("#ffffff")
        self.background_color_header = ttk.Label(self, text="Item background", font=("default", 11), justify=tk.LEFT)
        self.background_color_entry = tk.Entry(self, textvariable=self.background_color)
        self.background_color_button = ttk.Button(self, text="Choose color", command=self.update_color)
        self.font_header = ttk.Label(self, text="Item font", font=("default", 11), justify=tk.LEFT)
        self.font_select_frame = FontSelectFrame(self)
        self.add_button = ttk.Button(self, text="Create item", command=self.add_item)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)

        self.grid_widgets()

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
        self.text_header.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.text_entry.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.background_color_header.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.background_color_entry.grid(row=6, column=0, sticky="nswe", padx=5, pady=5)
        self.background_color_button.grid(row=6, column=1, padx=5, pady=5)
        self.font_header.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.font_select_frame.grid(row=8, column=0, columnspan=3, sticky="nswe", padx=5, pady=5)
        self.add_button.grid(row=9, column=1, sticky="nswe", padx=5, pady=5)
        self.cancel_button.grid(row=9, column=0, sticky="nswe", padx=5, pady=5)

    def add_item(self):
        """Callback for add_button"""
        if "_" in self.text.get() or "+" in self.text.get():
            messagebox.showerror("Error", "The characters _ and + are not allowed in item texts.")
            return
        if callable(self.callback):
            if not self.font_select_frame._family:
                print("[CreateItem] No font family selected.")
            font = self.font_select_frame.font if self.font_select_frame.font is not None else ("default", 12)
            if font == ("default", 12):
                print("[CreateItem] Default font selected")
            self.callback(self.text.get(), font, color=self.background_color.get())
        self.destroy()

    def update_color(self):
        """Callback for background_color_button"""
        tuple, hex = askcolor()
        if not tuple or not hex:
            return
        self.background_color.set(hex)
        self.update_entry(tuple)

    def update_entry(self, color_tuple):
        """Configure color Entry colors"""
        self.background_color_entry.config(
            background=self.background_color.get(), foreground=color_background(color_tuple))