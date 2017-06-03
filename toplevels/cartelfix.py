# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from pynput import keyboard
from PIL import Image, ImageTk
import variables


class CartelFix(tk.Toplevel):
    def __init__(self, master, first, second, coordinates, scale):
        tk.Toplevel.__init__(self, master)
        self.label = tk.Label(self)
        self.railgun = 1
        size = (int(round(45.0 * scale, 0)), int(round(45.0 * scale, 0)))
        self.first = ImageTk.PhotoImage(Image.open(first).resize(size, Image.ANTIALIAS))
        self.second = ImageTk.PhotoImage(Image.open(second).resize(size, Image.ANTIALIAS))
        self.label.config(image=self.first)
        self.label.grid()
        self.listener = keyboard.Listener(on_press=self.switch)
        self.coordinates = coordinates
        self.set_geometry()

    def switch(self, key):
        # This annoying code path is necessary because pynput does not provide full documentation
        # key.char is only provided by the pynput library if the key is an alphanumeric key
        # It is unknown whether key.char is always a str, or can also be int when a numeric key is pressed
        # The return value of this function is always True to keep the pynput thread running
        try:
            if int(key.char) != 1:
                return True
        except AttributeError:
            return True
        except TypeError:
            return True
        if self.railgun == 1:
            self.label.config(image=self.second)
            self.railgun = 2
        elif self.railgun == 2:
            self.label.config(image=self.first)
            self.railgun = 1
        else:
            raise ValueError("Not a valid railgun number: {0}".format(self.railgun))
        return True

    def set_geometry(self):
        self.configure(background="white")
        self.wm_attributes("-transparentcolor", "white")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_geometry("+{0}+{1}".format(self.coordinates[0], self.coordinates[1]))

    def start_listener(self):
        self.listener.start()

    def destroy(self):
        variables.main_window.realtime_frame.cartelfix = None
        super(tk.Toplevel, self)
