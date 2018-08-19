"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from time import sleep
# Project Modules
from parsing.shipstats import ShipStats
# Packages
from pynput.keyboard import Key, KeyCode


class SpeedParser(Thread):
    """
    Thread that tracks key inputs to determine ship speed in m/s

    Uses the ship statistics provided by a ShipStats instance to
    determine boost acceleration, boost speed and other statistics
    to simulate the ship speed mechanic.
    """

    CONTROL_KEYS = {
        "x": "x",
        "w": "w",
        "s": "s",
        Key.space: "space",
        Key.f1: "F1",
        Key.f2: "F2",
        Key.f3: "F3",
        Key.f4: "F4",
    }

    X = "x"

    STATS = [
        "Engine_Base_Speed",
        "Engine_Speed_Modifier_at_Max_Power",
        "Engine_Speed_Modifier_at_Min_Power",
        "Engine_Speed_Multiplier",
        "Booster_Acceleration",
        "Booster_Speed_Multiplier",
    ]

    EFFECTS = {
        "3325021946642721": (0.50, 3.00),  # Seismic Mine
        "3296133996609804": (0.65, 0.00),  # Sabotage Probe
        "3298960085090571": (0.70, 15.0),  # Concussion Missile
        "3298981559927073": (0.60, 6.00),  # Ion Missile
        "3327289689374988": (0.40, 20.0),  # Interdiction Mine
        "3302546382782728": (0.70, 6.00),  # Interdiction Drive
    }

    def __init__(self):
        """Initialize attributes and Queues"""
        self._exit_queue = Queue()
        self._string = str()
        Thread.__init__(self)
        # This is not a queue, because the GIL protects it
        self._key_states = {k: False for k in SpeedParser.CONTROL_KEYS.values()}
        self._stopped = False
        self._slowed = False
        self._stats = None
        self._effects = list()
        self._boost = None
        self._power_mode = "F4"
        self._match = False

    def run(self):
        """Run the Thread's tasks"""
        print("[SpeedParser] Started")
        while True:
            sleep(0.05)
            # Exit Loop if exit requested
            try:
                self._exit_queue.get(False)
                break
            except:
                pass
            # Retrieve attributes
            stats: dict = self._stats.copy() if self._stats else None
            effects = self._effects.copy()
            boost = self._boost
            power = self._power_mode
            match = self._match
            if stats is None or match is False:
                self._string = "Speed: Unknown\n"
                continue
            # Calculations
            now = datetime.now()
            base: float = stats["Engine_Base_Speed"] * 100
            if boost is not None:
                acceleration = stats["Booster_Acceleration"] * 100
                boost_multiplier = stats["Booster_Speed_Multiplier"]
                base = min(base * boost_multiplier, base + (now - boost).total_seconds() * acceleration)
                throttle = 1.0
            elif self._stopped is True:
                throttle = 0.0
            elif self._key_states["w"] is True:
                throttle = 1.0
            elif self._key_states["s"] is True:
                throttle = 0.35
            else:
                throttle = 0.7
            if power == "F4":
                power_multiplier = 1.0
            elif power == "F3":
                power_multiplier = stats["Engine_Speed_Modifier_at_Max_Power"]
            else:
                power_multiplier = stats["Engine_Speed_Modifier_at_Min_Power"]
            effect_multiplier = 1.0
            for start, (multiplier, duration) in effects:
                if start + timedelta(seconds=duration) > now:
                    self._effects.remove((start, (multiplier, duration)))
                    continue
                effect_multiplier *= multiplier
            multiplier: float = stats["Engine_Speed_Multiplier"]
            speed: float = base * throttle * multiplier * effect_multiplier * power_multiplier
            self._string = "Speed: {:03.01f}m/s\n".format(speed)

    def on_key(self, key: (Key, KeyCode), state: bool):
        """Process the press or release of a key"""
        key = key if key in Key else repr(key).strip("'")
        if key not in SpeedParser.CONTROL_KEYS:
            return
        key = SpeedParser.CONTROL_KEYS[key]
        if key in self._key_states and self._key_states[key] is state:
            return
        self._key_states[key] = state
        if key == "x" and state is False:
            self._stopped = not self._stopped
        if key == "w" or key == "s":
            self._stopped = False
        elif key == "space":
            self._boost = datetime.now() if state is True else None
            self._stopped = False
        elif "F" in key:
            self._power_mode = key
        print("[SpeedParser] Processed Key: {}, {}".format(key, state))

    @property
    def string(self):
        """Process-safe accessor to _string attribute"""
        return self._string

    def update_ship_stats(self, ship: ShipStats):
        """Update the statistics used in this class Process-safely"""
        self._stats = dict()
        for stat in SpeedParser.STATS:
            self._stats[stat] = ship["Ship"][stat]

    def process_slowed_event(self, event: dict):
        """Process an Engine Slowed event"""
        if event["effect_id"] not in SpeedParser.EFFECTS or not "ApplyEffect" in event["effect"]:
            return
        self._effects.append((event["time"], SpeedParser.EFFECTS[event["effect_id"]]))

    def reset(self):
        """Reset the attributes that contain cached values"""
        self._stats = None
        self._effects.clear()
        self._power_mode = "F4"

    def stop(self):
        """Stop the Thread's activities and join it"""
        self._exit_queue.put(True)
        self.join(timeout=2)

    def match_start(self):
        """Set attribute for the start of a match"""
        self._match = True

    def match_end(self):
        """Set the attribute for the end of a match"""
        self._match = False

    def set_scope_mode(self, state: bool):
        """Set the Scope Mode (engine speed zero)"""
        self._stopped = state
