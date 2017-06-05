# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk


class ShipStatsToplevel(tk.Toplevel):
    """
    A Toplevel that shows the statistics for a certain ship in an organized manner, categorized and in alphabetical
    order where applicable, in human readable format.
    """
    def __init__(self, master, ship_object):
        tk.Toplevel.__init__(self, master)
