# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from tkinter import StringVar


class Overlay(object):
    """
    Overlay skeleton class
    """

    default_font = {
        "family": "Calibri",
        "bold": True,
        "italic": False,
        "size": 12
    }

    def __init__(self, position, text_variable, wait_time=20, font=default_font, master=None, color=(0, 255, 255),
                 opacity=255, auto_init=True):
        if not isinstance(position, tuple) or not len(position) == 2:
            raise ValueError("position argument invalid")
        if not isinstance(text_variable, StringVar):
            raise TypeError("text_variable not StringVar")
        if not isinstance(wait_time, int):
            raise TypeError("wait_time not int")
        if not isinstance(font, (tuple, dict)):
            raise TypeError("font argument not valid type")
        if not isinstance(color, tuple) or not len(color) == 3:
            raise ValueError("color not valid color tuple")
        if not isinstance(opacity, int):
            raise TypeError("opacity not int")
        if not 0 <= opacity <= 255:
            raise ValueError("opacity out of range (8-bit)")
        if not isinstance(auto_init, bool):
            raise TypeError("auto_init not bool")

    def initialize_window(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()

    def cget(self, key):
        raise NotImplementedError()

    def config(self, **kwargs):
        raise NotImplementedError()

    def configure(self, **kwargs):
        return self.config(**kwargs)

    def __getitem__(self, item):
        return self.cget(item)

    def __setitem__(self, key, value):
        return self.config(**{key: value})

    def update_text(self, text):
        raise NotImplementedError()

    @property
    def rectangle(self):
        raise NotImplementedError()

    @property
    def position(self):
        raise NotImplementedError()

    def __exit__(self):
        self.destroy()
