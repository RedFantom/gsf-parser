# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import components.primaries
import components.secondaries
import components.shields
import components.engines
import components.thrusters
import components.reactors
import components.sensors
import components.capacitors
import components.magazines


class Ship(object):
    def __init__(self):
        self.components = {'primary': None,
                           'secondary': None,
                           'shield': None,
                           'engine': None,
                           'system': None,
                           'capacitor': None,
                           'reactor': None,
                           'magazine': None,
                           'sensor': None,
                           'armor': None,
                           'thruster': None}

    def __setitem__(self, item, value):
        pass

    def __getitem__(self, item):
        pass

    def update_modifiers(self):
        pass


class Razorwire(Ship):
    pass


class Legion(Ship):
    pass


class Decimus(Ship):
    pass


class Mangler(Ship):
    pass


class Dustmaker(Ship):
    pass


class Jurgoran(Ship):
    pass


class Sting(Ship):
    pass


class Bloodmark(Ship):
    pass


class Blackbolt(Ship):
    pass


class Rycer(Ship):
    pass


class Quell(Ship):
    pass


class Imperium(Ship):
    pass
