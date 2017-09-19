# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk


class ReadonlyEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        ttk.Entry.__init__(self, *args, **kwargs)
        self.bind("<Key>", self.callback)

    def callback(self, event):
        self.after(5, lambda: self.delete(0, tk.END))
