# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE


class MajorComponent(object):
    def __init__(self):
        self.upgrades = {"t1": False,
                         "t2": False,
                         "t3": False,
                         "t4": None,  # Could be 1 or 2
                         "t5": None}

    def __getitem__(self, item):
        return self.upgrades[item]

    def __setitem__(self, item, value):
        if item == "t1" or item == "t2" or item == "t3":
            if value == False or value == True:
                self.upgrades[item] = value
            else:
                raise ValueError("Not a valid upgrade value")
        elif item == "t4" or item == "t5":
            if item == "t5" and (value == 1 or value == 2) and self.upgrades["t4"]:
                raise ValueError("Attempt to set t5 to 1 or 2 while t4 is not enabled")
            if value == None or value == 1 or value == 2:
                self.upgrades[item] = value
            else:
                raise ValueError("Not a valid upgrade value")
        else:
            raise ValueError("Not a valid t_ value")


class NormalComponent(object):
    def __init__(self):
        self.upgrades = {"t1": False,
                         "t2": False,
                         "t3": None}

    def __getitem__(self, item):
        return self.upgrades[item]

    def __setitem__(self, item, value):
        pass


class MinorComponent(object):
    def __init__(self):
        self.upgrade_level = 0

    def set_upgrade_level(self, lvl):
        self.upgrade_level = lvl
