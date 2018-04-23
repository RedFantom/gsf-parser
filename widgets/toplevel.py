"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import tkinter as tk


__init__original = tk.Toplevel.__init__


def __init__toplevel(*args, **kwargs):
    kwargs.setdefault("background", "#F5F6F7")
    __init__original(*args, **kwargs)


tk.Toplevel.__init__ = __init__toplevel
