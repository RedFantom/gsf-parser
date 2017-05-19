# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from pynput import keyboard
import cv2
from PIL import Image, ImageTk
from parsing.vision import pillow_to_numpy
from tools.utilities import get_pillow_screen
import numpy


class CartelFix(tk.Toplevel):
    def __init__(self, master, first, second):
        tk.Toplevel.__init__(self, master)
        self.label = tk.Label(self)
        self.railgun = 1
        self.first_pil = Image.open(first)
        self.first = ImageTk.PhotoImage(self.first_pil)
        self.second = ImageTk.PhotoImage(Image.open(second))
        self.label.config(image=self.first)
        self.listener = keyboard.Listener(on_press=self.switch)

    def switch(self, *args):
        if self.railgun == 1:
            self.label.config(image=self.second)
            self.railgun = 2
        elif self.railgun == 2:
            self.label.config(image=self.first)
            self.railgun = 1
        else:
            raise ValueError("Not a valid railgun number: {0}".format(self.railgun))

    def set_geometry(self):
        screen = pillow_to_numpy(get_pillow_screen())
        template = pillow_to_numpy(self.first_pil)
        results = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        y, x = numpy.unravel_index(results.argmax(), results.shape)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_geometry("+{0}+{1}".format(x, y))

    def start_listener(self):
        self.listener.start()
