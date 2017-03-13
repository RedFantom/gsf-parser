# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import components


class PrimaryWeapon(components.MajorComponent):
    def __init__(self):
        components.MajorComponent.__init__(self)
        super(components.MajorComponent, self)
        self.hull_damage = 0
        self.shield_damage = 0
        self.shield_piercing = 0
        self.accuracy = []
        self.range = []
        self.shots_per_second = 0
        self.critical_chance = 0


class BurstLaserCannon(PrimaryWeapon):
    def update_damage_amounts(self):
        pass


class LightLaserCannon(PrimaryWeapon):
    def update_damage_amounts(self):
        pass


class QuadLaserCannon(PrimaryWeapon):
    def update_damage_amounts(self):
        pass

# etc
