"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
# Project Modules
from parsing.benchmarker import benchmark
from parsing.shipstats import ShipStats
# Packages
from pynput.keyboard import Key, KeyCode


class SpeedParser(object):
    """
    Thread that tracks key inputs to determine ship speed in m/s

    Uses the ship statistics provided by a ShipStats instance to
    determine boost acceleration, boost speed and other statistics
    to simulate the ship speed mechanic.
    """

    INIT_ARGS = []

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
        self._string = str()
        # This is not a queue, because the GIL protects it
        self.key_states = {k: False for k in SpeedParser.CONTROL_KEYS.values()}
        self.stopped = False
        self.stats = None
        self.effects = list()
        self.boost = None
        self.power = "F4"
        self.is_match = False

    @benchmark("Engine Speed")
    def update(self):
        """Calculate Ship speed and update string"""
        # Retrieve attributes
        if self.stats is None or self.is_match is False:
            self._string = "Speed: Unknown\n"
            return
        # Calculations
        now = datetime.now()
        base: float = self.stats["Engine_Base_Speed"] * 100
        if self.boost is not None:
            acceleration = self.stats["Booster_Acceleration"] * 100
            boost_multiplier = self.stats["Booster_Speed_Multiplier"]
            base = min(base * boost_multiplier, base + (now - self.boost).total_seconds() * acceleration)
            throttle = 1.0
        elif self.stopped is True:
            throttle = 0.0
        elif self.key_states["w"] is True:
            throttle = 1.0
        elif self.key_states["s"] is True:
            throttle = 0.35
        else:
            throttle = 0.7
        if self.power == "F4":
            power_multiplier = 1.0
        elif self.power == "F3":
            power_multiplier = self.stats["Engine_Speed_Modifier_at_Max_Power"]
        else:
            power_multiplier = self.stats["Engine_Speed_Modifier_at_Min_Power"]
        effect_multiplier = 1.0
        for start, (multiplier, duration) in self.effects.copy():
            if start + timedelta(seconds=duration) > now:
                self.effects.remove((start, (multiplier, duration)))
                continue
            effect_multiplier *= multiplier
        multiplier: float = self.stats["Engine_Speed_Multiplier"]
        speed: float = base * throttle * multiplier * effect_multiplier * power_multiplier
        self._string = "Speed: {:03.01f}m/s\n".format(speed)

    def on_key(self, key: (Key, KeyCode), state: bool):
        """Process the press or release of a key"""
        key = key if key in Key else repr(key).strip("'")
        if key not in SpeedParser.CONTROL_KEYS:
            return
        key = SpeedParser.CONTROL_KEYS[key]
        if key in self.key_states and self.key_states[key] is state:
            return
        self.key_states[key] = state
        if key == "x" and state is False:
            self.stopped = not self.stopped
        if key == "w" or key == "s":
            self.stopped = False
        elif key == "space":
            self.boost = datetime.now() if state is True else None
            self.stopped = False
        elif "F" in key:
            self.power = key

    @property
    def string(self):
        """Process-safe accessor to _string attribute"""
        return self._string

    def set_ship_stats(self, ship: ShipStats):
        """Update the statistics used in this class Process-safely"""
        self.stats = dict()
        for stat in SpeedParser.STATS:
            self.stats[stat] = ship["Ship"][stat]

    def process_event(self, event: dict, *args):
        """Process an Engine Slowed event"""
        if event["effect_id"] not in SpeedParser.EFFECTS or not "ApplyEffect" in event["effect"]:
            return
        self.effects.append((event["time"], SpeedParser.EFFECTS[event["effect_id"]]))

    def spawn(self):
        """Reset the attributes that contain cached values"""
        self.stats = None
        self.effects.clear()
        self.power = "F4"

    def match_start(self):
        """Set attribute for the start of a match"""
        self.is_match = True

    def match_end(self):
        """Set the attribute for the end of a match"""
        self.is_match = False

    def set_scope_mode(self, state: bool):
        """Set the Scope Mode (engine speed zero)"""
        self.stopped = state
