# -*- coding: utf-8 -*-

"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk


class ReadonlyEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        ttk.Entry.__init__(self, *args, **kwargs)
        self.bind("<Key>", self.callback)

    def callback(self, event):
        self.after(5, lambda: self.delete(0, tk.END))
