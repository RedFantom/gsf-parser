import tkinter as tk
from tkinter import ttk
from parsing.guiparsing import GSFInterface


class MapOverlay(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

    def set_position_on_map(self, x, y):
        pass

    def set_position_on_screen(self, x, y):
        pass
