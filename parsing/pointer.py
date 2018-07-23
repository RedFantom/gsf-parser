"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
import os
from threading import Thread
from time import sleep
# Packages
from mss import mss
from PIL import Image
from pynput.mouse import Button, Listener
from queue import Queue
# Project Modules
from parsing.gsfinterface import GSFInterface
from parsing import opencv
from utils.directories import get_assets_directory
from utils.utilities import get_cursor_position, open_icon_pil


class PointerParser(Thread):
    """
    Determine for each shot whether it was a successful hit or not

    Runs yet another Thread, receiving mouse presses and taking
    screenshots to check if the pointer has the properties of being
    on-target (which is displayed using additional markers around the
    default pointer indicator).
    """

    ICONS = {
        "spvp_evasion": 0.15,
        "spvp_distortionfield": 0.35,
    }

    ICON_SIZE = 23
    ICON_SCALE = 0.9

    def __init__(self, gui_profile: GSFInterface):
        """
        :param gui_profile: GUI Profile selected by the user
        """
        self.rof = None
        self.ship_class = None
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
        self.mouse = Listener(on_click=self.on_click)

        self.icons = dict()
        scale = self.interface.get_pixels_per_degree() / 10
        size = int(PointerParser.ICON_SIZE * (scale / PointerParser.ICON_SCALE))
        for icon in PointerParser.ICONS:
            image = open_icon_pil(icon)
            self.icons[icon] = image.resize((size, size), Image.ANTIALIAS)

    def on_click(self, _: int, __: int, button: Button, pressed: bool):
        """Process a click of the mouse"""
        if not button == Button.left:
            return
        self.mouse_queue.put(pressed)

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
            if self.rof is None or self.ship_class == "Gunship":
                sleep(1)  # Reduce performance impact when not active
                print("[PointerParser] Does not have required data...")
                continue
            while not self.mouse_queue.empty():
                self.pressed = self.mouse_queue.get()
            if self.pressed is False:
                continue
            # Button is pressed
            if (datetime.now() - self.last).total_seconds() < self.rof:
                continue
            print("[PointerParser] Processing a shot...")
            self.last = datetime.now()
            loc = get_cursor_position()
            pointer_box = tuple(c - 30 for c in loc) + (30, 30)
            screenshot = self.mss.grab({list(zip(("left", "top", "width, height"), pointer_box))})
            screenshot = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            match, _ = opencv.template_match(screenshot, self.pointer)
            print("[PointerParser] On-target: {}".format(match))
            self.chance_queue.put((self.last, match))

    def stop(self):
        """Stop the Thread's activities by notifying it it needs to exit"""
        self.exit_queue.put(True)
        self.join()

    def set_rate_of_fire(self, rof: float, ship_class: str):
        """
        Update the ship in use by this PointerParser

        The class depends on the ship for providing accurate rate of
        fire numbers.
        """
        self.rof = 1 / rof
        self.ship_class = ship_class
