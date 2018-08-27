"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
import os
from queue import Queue
from threading import Thread
from time import sleep
# Packages
from mss import mss
from PIL import Image
# Project Modules
from parsing.gsf import GSFInterface
from parsing.imageops import get_similarity_transparent
from utils.directories import get_assets_directory
from utils.utilities import get_cursor_position


class PointerParser(Thread):
    """
    Determine for each shot whether it was a successful hit or not

    Runs yet another Thread, receiving mouse presses and taking
    screenshots to check if the pointer has the properties of being
    on-target (which is displayed using additional markers around the
    default pointer indicator).
    """

    def __init__(self, gui_profile: GSFInterface):
        """
        :param gui_profile: GUI Profile selected by the user
        """
        self.rof = None
        self.ship_class = None
        self._scope_mode = False
        self.interface = gui_profile
        self.mouse_queue = Queue()
        self.exit_queue = Queue()
        self.chance_queue = Queue()
        self.pressed = False
        self.last = datetime.now()
        path = os.path.join(get_assets_directory(), "vision", "pointer.png")
        self.pointer = Image.open(path)

        Thread.__init__(self)

        self.mss = mss()

    def run(self):
        """
        Run the loop that takes screenshots

        The loop checks for mouse clicks continuously. The clicks are
        put in the queue, where this thread picks them up. When a click
        is processed, a screenshot is taken. Then, the screenshot is
        cropped to the pointer and a template match is ran in order to
        determine whether the shot was made on-target. Then the result
        of this process is passed on to the Thread owner.
        """
        print("[PointerParser] Starting...")
        while self.exit_queue.empty():
            if self.rof is None:
                sleep(1)  # Reduce performance impact when not active
                continue
            while not self.mouse_queue.empty():
                self.pressed = self.mouse_queue.get()
            if self.pressed is False:
                continue
            # Button is pressed
            if (datetime.now() - self.last).total_seconds() < self.rof:
                continue
            self.last = datetime.now()
            loc = get_cursor_position()
            pointer_box = tuple(c - 22 for c in loc) + (44, 44)
            if min(pointer_box) < 0 or max(pointer_box) > 1920:
                self.chance_queue.put((self.last, False))
                continue
            monitor = {k: v for k, v in zip(("left", "top", "width", "height"), pointer_box)}
            try:
                screenshot = self.mss.grab(monitor)
            except Exception as e:
                print("[PointerParser] Error: {}".format(e))
                continue
            screenshot = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            screenshot = screenshot.convert("RGBA")
            match = get_similarity_transparent(self.pointer, screenshot)
            self.chance_queue.put((self.last, match > 95))

    def stop(self):
        """Stop the Threads activities by notifying it it needs to exit"""
        self.exit_queue.put(True)
        self.join(timeout=2)
        print("[PointerParser] Stopped.")

    def set_rate_of_fire(self, rof: float, ship_class: str):
        """
        Update the ship in use by this PointerParser

        The class depends on the ship for providing accurate rate of
        fire numbers.
        """
        print("[PointerParser] Rate of Fire updated: {}".format(rof))
        self.rof = 1 / rof
        self.ship_class = ship_class

    def set_scope_mode(self, mode: bool):
        """
        Set the Scope Mode to either enabled or disabled

        If the current ship is a Gunship and the player enters Scope
        Mode, the Pointer Parser should be temporarily disabled because
        any received keypressed would be invalid.
        """
        self._scope_mode = mode

    def new_spawn(self):
        """
        Callback for new spawn event in RealTimeParser

        Resets all attributes until new information is available.
        """
        self.rof = None
        self.ship_class = None
        self._scope_mode = False
