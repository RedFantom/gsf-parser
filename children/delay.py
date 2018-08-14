"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from queue import Queue
from time import sleep
# Packages
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
# Project Modules
from parsing import Parser
from parsing.shipstats import ShipStats


class DelayParser(object):
    """Parser that checks Regeneration Delays and controls an overlay"""

    DELAYS = {
        "Power_Shield_Regen_Delay": "Shield",
        "Power_Weapon_Regen_Delay": "Weapon",
        "Power_Engine_Regen_Delay": "Engine"
    }

    POOLS = ["Weapon", "Shield", "Engine"]
    STATS = {
        "Delay": "Power_{}_Regen_Delay",
        "Regen": "Power_{}_Regen_Rate",
        "Recent": "Power_{}_Regen_Rate_(when_Recently_Consumed)"
    }

    INIT_ARGS = []

    def __init__(self):
        """Initialize as Thread and create attributes"""
        self._stats = {p: {k: 0.0 for k in self.STATS} for p in self.POOLS}
        self.primary = "PrimaryWeapon"
        self.__delays = dict()
        self._internal_q = Queue()
        self._match = False
        self._mouse = False
        self._string = str()
        print("[DelayParser] Initialized")

    def set_ship_stats(self, ship: ShipStats):
        """Update the ship statistics used for delay tracking"""
        self._stats = {
            p: {k: ship["Ship"][v.format(p)] for k, v in self.STATS.items()}
            for p in self.POOLS
        }
        self.primary = "PrimaryWeapon"
        print("[DelayParser] Updated ship to: {}".format(ship.ship.name))

    def swap_weapon(self, weapon: str):
        """Swap the primary weapon key"""
        if "primary" not in weapon.lower():
            return
        self.primary = "PrimaryWeapon2" if self.primary == "PrimaryWeapon" else "PrimaryWeapon"
        print("[DelayParser] Swapped Primary Weapons")

    def match_end(self):
        """Match ended callback"""
        self._internal_q.put("end")

    def match_start(self):
        """Match start callback"""
        self._internal_q.put("start")

    def update(self):
        """Update the state of the DelayParser"""
        stats, key = self._stats.copy(), self.primary

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
        string, time = "\n", datetime.now()
        for pool, start in self.__delays.items():
            elapsed = (time - start).total_seconds()
            remaining = max(stats[pool]["Delay"] - elapsed, 0.0)
            rate = stats[pool]["Regen"] if remaining == 0.0 else stats[pool]["Recent"]
            string += "{}: {:.1f}s, {:.1f}pps\n".format(pool[0], remaining, rate)
        self._string = string
        sleep(0.1)

    def process_event(self, event: dict, active_ids: list):
        """Process an event to check for shield power pool usage"""
        ctg = Parser.get_event_category(event, active_ids)
        if event["self"] is True and ctg == "engine":
            self._internal_q.put(("Engine", event["time"]))
            return
        if event["self"] is True or Parser.compare_ids(event["target"], active_ids) is False:
            return
        if "Damage" not in event["effect"]:
            return
        # event: Damage dealt to self
        self._internal_q.put(("Shield", event["time"]))

    def on_click(self, x: int, y: int, button: Button, state: bool):
        """Process a click to check for weapon power usage"""
        if button == Button.left:
            self._internal_q.put("mouse")

    def on_press(self, key: (Key, KeyCode), state: bool):
        """Process a key press to check for engine power usage"""
        if state is False:
            return
        if key == Key.space:
            self._internal_q.put(("Engine", datetime.now()))

    @property
    def string(self):
        """String to show in the Overlay"""
        return self._string
