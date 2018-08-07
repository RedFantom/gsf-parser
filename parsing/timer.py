"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from queue import Queue, Empty as QueueEmpty
from threading import Thread, Lock
from time import sleep
from tkinter import StringVar, Tk
# Packages
from pynput.keyboard import Listener as KBListener, Key
from pynput.mouse import Listener as MSListener, Button
# Project Modules
from parsing import Parser
from parsing.shipstats import ShipStats
from widgets.overlays import Overlay


class TimerParser(Thread):
    """Parser that checks Regeneration Delays and controls an overlay"""

    DELAYS = {
        "Power_Shield_Regen_Delay": "Shield",
        "Power_Weapon_Regen_Delay": "Weapon",
        "Power_Engine_Regen_Delay": "Engine"
    }

    def __init__(self, root: Tk, string: StringVar):
        """Initialize as Thread and create attributes"""
        Thread.__init__(self)
        self._root = root
        self._after_id = None
        self._delays = {k: 1.0 for k in self.DELAYS.values()}
        self._lock = Lock()
        self._exit_queue = Queue()
        self._data_queue = Queue()
        self.primary = "PrimaryWeapon"
        self.__delays = dict()
        self._internal_q = Queue()
        self._match = False
        self._ms_listener = MSListener(on_click=self._on_click)
        self._kb_listener = KBListener(on_press=self._on_press)
        self._mouse = False
        print("[TimerParser] Initialized")

    def set_ship_stats(self, ship: ShipStats):
        """Update the ship statistics used for delay tracking"""
        self._lock.acquire()
        self._delays = {k: ship["Ship"][v] for v, k in self.DELAYS.items()}
        self.primary = "PrimaryWeapon"
        self._lock.release()
        print("[TimerParser] Updated ship to: {}".format(ship.ship.name))

    def primary_weapon_swap(self):
        """Swap the primary weapon key"""
        self.primary = "PrimaryWeapon2" if self.primary == "PrimaryWeapon" else "PrimaryWeapon"
        print("[TimerParser] Swapped Primary Weapons")

    def match_end(self):
        """Match ended callback"""
        self._internal_q.put("end")

    def match_start(self):
        """Match start callback"""
        self._internal_q.put("start")

    def update(self):
        """Update the state of the TimerParser"""
        self._lock.acquire()
        delays, key = self._delays.copy(), self.primary
        self._lock.release()

        while not self._internal_q.empty():
            v = self._internal_q.get()
            if v == "start":
                self._match = True
            elif v == "end":
                self._match = False
            elif v == "mouse":
                self._mouse = not self._mouse
            else:
                pool, time = v
                self.__delays[pool] = time
        if self._match is False:
            return
        if self._mouse is True:
            self.__delays["Weapon"] = datetime.now()
        string, time = str(), datetime.now()
        for pool, start in self.__delays.items():
            elapsed = (time - start).total_seconds()
            if elapsed < delays[pool]:
                remaining = "{:.1f}s".format(delays[pool] - elapsed)
            else:
                remaining = "Regenerating"
            string += "{}: {}\n".format(pool, remaining)
        if len(string) != 0:
            self._data_queue.put(string)
        sleep(0.1)

    def process_event(self, event: dict, active_ids: list):
        """Process an event to check for shield power pool usage"""
        if event["self"] is True or Parser.compare_ids(event["target"], active_ids) is False:
            return
        if "Damage" not in event["effect"]:
            return
        # event: Damage dealt to self
        self._internal_q.put(("Shield", event["time"]))

    def cleanup(self):
        """Clean up everything in use"""
        self._ms_listener.stop()
        self._kb_listener.stop()

    def run(self):
        """Run the Thread"""
        self._ms_listener.start()
        self._kb_listener.start()
        while True:
            if not self._exit_queue.empty():
                break
            self.update()
        self.cleanup()

    def stop(self):
        """Stop activities and join Thread"""
        if not self.is_alive():
            return
        self._exit_queue.put(True)
        self.join()

    def _on_click(self, x: int, y: int, button: Button, state: bool):
        """Process a click to check for weapon power usage"""
        if button == Button.left:
            self._internal_q.put("mouse")

    def _on_press(self, key: (Key, str)):
        """Process a key press to check for engine power usage"""
        if key == Key.space or key == "3":
            self._internal_q.put(("Engine", datetime.now()))
