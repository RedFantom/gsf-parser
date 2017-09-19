# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from pynput import mouse
import threading
import tkinter as tk
# Own modules
from widgets.overlay import Overlay


class HitMissParser(threading.Thread):
    """
    A Class capable of displaying overlays where the cursor is when shooting. Shows overlays for misses due to evasion
    and misses due to not being on target separately.
    """
    pass


class MissOverlay(Overlay):
    """
    Overlay that shows for a certain time and then fades out
    """
    def __init__(self, master, position, fadeout=True, fadetime=1000, text="Miss", move_downward=20, text_size=12):
        self.text = tk.StringVar(value=text)
        Overlay.__init__(self, position, text_variable=self.text, master=master, text_size=text_size, font_family="")



