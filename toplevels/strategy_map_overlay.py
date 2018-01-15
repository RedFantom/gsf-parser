"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk
from tkinter import ttk
# Own modules
from parsing.gsfinterface import GSFInterface


class MapOverlay(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

    def set_position_on_map(self, x, y):
        pass

    def set_position_on_screen(self, x, y):
        pass
