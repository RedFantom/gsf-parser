# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

try:
    import mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import tkMessageBox
import tkSimpleDialog
import tkFont
import abilities

class builds_frame(ttk.Frame):
    def __init__(self):
        ttk.Frame.__init__(self)
