# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

try:
    import mttkinter.mtTkinter as tk
except ImportError:
    print "mtTkinter not found, please use 'pip install mttkinter'"
    import Tkinter as tk
import ttk
import collections
import os
from PIL import Image
from PIL.ImageTk import PhotoImage
import widgets


class builds_frame(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.ships = collections.OrderedDict()
        self.ships['Blackbolt'] = 'blackbolt.png'
        self.ships['Bloodmark'] = 'bloodmark.png'
        self.ships['Sting'] = 'sting.png'
        self.ships['Quell'] = 'quell.png'
        self.ships['Imperium'] = 'imperium.png'
        self.ships['Rcyer'] = 'rycer.png'
        self.ships['Decimus'] = 'decimus.png'
        self.ships['Razorwire'] = 'razorwire.png'
        self.ships['Legion'] = 'legion.png'
        self.ships['Jurgoran'] = 'jurgoran.png'
        self.ships['Mangler'] = 'mangler.png'
        self.ships['Dustmaker'] = 'dustmaker.png'
        self.ship_buttons = {}
        self.ship_scrollable_frame = widgets.vertical_scroll_frame(self, width=60, height=400)
        self.ship_frame = self.ship_scrollable_frame.interior
        self.ship_images = {}
        for key, value in self.ships.iteritems():
            temp_img = Image.open(os.path.dirname(__file__).replace("frames", "") + "\\assets\\ships\\" + value)
            self.ship_images[key] = PhotoImage(temp_img)
            self.ship_buttons[key] = ttk.Button(self.ship_frame, image=self.ship_images[key],
                                                command=lambda ship=key: self.set_ship(ship))

    def set_ship(self, ship):
        pass

    def grid_widgets(self):
        set_row = 0
        for widget in self.ship_buttons.itervalues():
            widget.grid(column=0, row=set_row)
            set_row += 1
        self.ship_frame.grid(column=0, row=0, rowspan=6, sticky=tk.W + tk.N)
