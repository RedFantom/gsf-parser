"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from ttkwidgets.color import askcolor
# Project Modules
from utils.colors import color_background
from utils import directories
from data import colors
from variables import settings, colors as color_scheme


class EventColors(tk.Toplevel):
    """Custom color scheme customizer window"""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("background", "white")
        tk.Toplevel.__init__(self, *args, **kwargs)
        # Window attributes
        self.wm_title("GSF Parser: Choose event colors")
        self.wm_resizable(False, False)
        # Gather current colors
        color_scheme.set_scheme(settings["gui"]["event_scheme"])
        self.colors = color_scheme.current_scheme.copy()
        """
        Widget Creation
        """
        # Column labels for the list of colors
        self.column_labels = list()
        for text in ("Type of event", "Background color", "Text color"):
            self.column_labels.append(ttk.Label(self, text=text, font=("default", 12)))
        # Color specific widgets
        self.color_widgets = dict()  # {color_key: (Label, Entry_fg, Button_fg, Entry_bg, Button_bg)}
        for key in colors.color_keys:
            label = ttk.Label(self, text=colors.color_descriptions[key], justify=tk.LEFT)
            button_fg = ttk.Button(self, text="choose", command=lambda c=key: self.set_color(c, 0))
            button_bg = ttk.Button(self, text="choose", command=lambda c=key: self.set_color(c, 1))
            entry_fg = tk.Entry(self, font=("Consolas", 10), width=10)
            entry_bg = tk.Entry(self, font=("Consolas", 10), width=10)
            self.color_widgets[key] = (label, entry_fg, button_fg, entry_bg, button_bg)
        # Control widgets
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.save_button = ttk.Button(self, text="Save", width=10, command=self.save_colors)
        self.cancel_button = ttk.Button(self, text="Cancel", width=10, command=self.destroy)
        self.import_button = ttk.Button(self, text="Import", width=10, command=self.import_colors)
        self.export_button = ttk.Button(self, text="Export", width=10, command=self.export_colors)

        # Finish setup of window
        self.grid_widgets()
        self.update_color_widgets()

    def grid_widgets(self):
        """Put the widgets in the grid geometry manager"""
        # Column labels
        column = 0
        row = 0
        for column_label in self.column_labels:
            column_label.grid(row=0, column=column, columnspan=2, padx=5, pady=5, sticky="nsw")
            column += 2
        # Color widgets
        for color_widgets in [self.color_widgets[key] for key in colors.color_keys]:
            column = 0
            row += 1
            for widget in color_widgets:
                widget.grid(column=column, row=row, padx=(0, 5), pady=(0, 5), sticky="nsw")
                column += 1 if not isinstance(widget, ttk.Label) else 2
        # Control widgets
        columns = len(self.color_widgets[colors.color_keys[0]])
        self.separator.grid(row=row+1, column=0, columnspan=columns, sticky="we", padx=5, pady=5)
        iterator = (self.import_button, self.export_button, self.cancel_button, self.save_button)
        column = columns - len(iterator)
        for widget in iterator:
            column += 1
            widget.grid(row=row+2, column=column, sticky="nswe", padx=(0, 5), pady=(0, 5))

    def update_color_widgets(self):
        """Update the color Entries' contents"""
        for key in colors.color_keys:
            _, entry_fg, _, entry_bg, _ = self.color_widgets[key]
            for i, entry in enumerate((entry_fg, entry_bg)):
                entry.delete(0, tk.END)
                color = self.colors[key][i]
                entry.insert(tk.END, color)
                entry.config(foreground=color, background=color_background(color))
        return

    def set_color(self, key, index):
        """Update a color using the askcolor"""
        title = "Choose {} color: {}".format(key, "foreground" if index == 0 else "background")
        current = self.colors[key][index]
        color = askcolor(current, title=title)  # color: ((R, G, B), "#hex")
        if color[0] is None:
            return
        self.colors[key][index] = color[1]  # hex value
        self.update_color_widgets()

    def save_colors(self):
        """Save the currently entered colors to ColorScheme"""
        color_scheme.write_custom(self.colors)
        self.destroy()

    def import_colors(self):
        """Import colors from a file selected by the user"""
        file_name = filedialog.askopenfilename(
            defaultextension=".ini",
            filetypes=[("Color Scheme", "*.ini"), ("All Filetypes", "*.*")],
            initialdir=directories.get_temp_directory(),
            title = "Import ColorScheme from file",
            parent=self)
        if file_name is None:  # Cancelled by user
            self.focus_set()
            return
        color_scheme.set_scheme("custom", custom_file=file_name)
        self.colors = color_scheme.current_scheme.copy()
        self.update_color_widgets()

    def export_colors(self):
        """Export colors to a file selected by the user"""
        file_name = filedialog.asksaveasfilename(
            defaultextension=".ini",
            filetypes=[("Color Scheme", "*.ini")],
            initialdir=directories.get_temp_directory(),
            title="Export ColorScheme to file",
            parent=self)
        if file_name is None:  # Cancelled by user
            self.focus_set()
            return
        color_scheme.write_custom(file_name=file_name)
