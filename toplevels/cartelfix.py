"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI imports
import tkinter as tk
from tkinter.messagebox import showinfo
# General imports
from pynput import keyboard
import sys
# Own modules
import variables
from utils import admin


factions = {
    "Imperial": "imp",
    "Republic": "rep"
}

railguns = {
    "Slug Railgun": {"imp": "03", "rep": "03"},
    "Ion Railgun": {"imp": "02", "rep": "01"},
    "Plasma Railgun": {"imp": "04", "rep": "04"}
}


class CartelFix(tk.Toplevel):
    """
    Provide a teensy overlay for Cartel Market Gunships secondary
    weapon icons.
    """
    def __init__(self, master: tk.Tk, first: tk.PhotoImage, second: tk.PhotoImage, coordinates: tuple):
        if not admin.check_privileges():
            if sys.platform == "win32":
                variables.main_window.destroy()
                admin.escalate_privileges()
                exit()
            else:
                showinfo("Information", "This feature is currently not supported on Unix machines.")
                raise ValueError()
        tk.Toplevel.__init__(self, master)
        self.label = tk.Label(self)
        self.railgun = 1
        self.first = first
        self.second = second
        self.label.config(image=self.first)
        self.label.grid()
        self.listener = keyboard.Listener(on_press=self.switch)
        self.coordinates = coordinates
        self.set_geometry()

    def switch(self, key: keyboard.Key):
        """
        Callback for the keyboard press Listener. Only if the pressed
        key is `1` on the keyboard (either NumPad or numeric row)
        will the icon switch status.
        """
        try:
            if int(key.char) != 1:
                return True
        except AttributeError:
            return True
        except ValueError:
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
        """Update window geometry and attributes"""
        self.configure(background="white")
        self.wm_attributes("-transparentcolor", "white")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_geometry("+{0}+{1}".format(self.coordinates[0], self.coordinates[1]))

    def start_listener(self):
        self.listener.start()

    @staticmethod
    def generate_icon_path(faction: str, railgun: str):
        """Generate the filename for specified railgun for faction"""
        base = "spvp.{}.gunship.sweapon.{}.jpg"
        return base.format(factions[faction], railguns[railgun][factions[faction]])
