"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk, messagebox


class AddPhase(tk.Toplevel):
    """
    Toplevel to show widgets for entering the data required to create
    a new Phase.
    """
    def __init__(self, *args, **kwargs):
        """
        :param callback: Function to call when the Phase is created,
            arguments: *(phase_name)
        """
        self._callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add new phase")
        self._entry = ttk.Entry(self, width=30)
        # Bind the Enter key to the same function as the Add-button for user convenience
        self._entry.bind("<Return>", self.add_phase)
        self._cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self._add_button = ttk.Button(self, text="Add", command=self.add_phase)
        self.grid_widgets()

    def grid_widgets(self):
        """The usual function to setup the geometry of the Toplevel"""
        self._entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self._cancel_button.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self._add_button.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)

    def add_phase(self, *args):
        """
        Function to call the callback when the phase is created
        :param args: For Tkinter <Return> event, not used
        """
        if not self.check_widgets():
            return
        if callable(self._callback):
            self._callback(self._entry.get())
        self.destroy()

    def check_widgets(self):
        """
        Checks if the data entered by the user is valid to create a Phase
        :return: True if data is valid, False if not
        """
        name = self._entry.get()
        if "¤" in name or "³" in name or "_" in name or "`" in name or "~" in name or "€" in name:
            messagebox.showinfo("Info", "The name you have chosen for your Phase contains invalid characters. A "
                                        "Phase name may not contain the characters _, `, ~, ³, ¤ or €.")
            return False
        return True