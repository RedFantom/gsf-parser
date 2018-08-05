"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
import _pickle as pickle
# Project Modules
from data.components import COMPONENT_TYPES, COMP_TYPES_REVERSE, COMPONENTS
from parsing.ships import Ship, Component
from utils.directories import get_assets_directory


class ShipStats(object):
    """
    Class to calculate the statistics for a given ship object. Uses the
    data found in the databases to calculate statistics for the main
    ship and each component.
    """

    ALIASES = {
        "Cooldown_Time": "Cooldown",
    }

    PRIMARY_WEAPON = ("PrimaryWeapon", "PrimaryWeapon2")
    SECONDARY_WEAPON = ("SecondaryWeapon", "SecondaryWeapon2")

    MODE_CORRECTED = [
        ("Shield_Strength_{}", "Shield_Strength_Modifier_at_{}_Power", "Shields_Max_Power_(Capacity)"),
        ("Engine_Speed_{}", "Engine_Speed_Modifier_at_{}_Power", "Engine_Base_Speed")
    ]

    POWER_POOLS = ["Engine", "Weapon", "Shield"]

    def __init__(self, ship: Ship, ships_data: dict, companions_data: dict):
        """
        :param ship: Ship object
        """
        self.stats = dict()
        self.ship = ship
        if ships_data is None:
            with open(os.path.join(get_assets_directory(), "ships.db"), "rb") as fi:
                ships_data = pickle.load(fi)
        if companions_data is None:
            with open(os.path.join(get_assets_directory(), "companions.db"), "rb") as fi:
                companions_data = pickle.load(fi)
        self.ships_data = ships_data.copy()
        self.companions_data = companions_data.copy()
        self.calc_ship_stats()

    def calc_ship_stats(self):
        """Calculate the statistics of the Ship Object"""
        self.stats.clear()
        self.stats["Ship"] = self.ships_data[self.ship.ship_name]["Stats"].copy()
        for key, value in self.stats["Ship"].copy().items():
            key = key.replace("_(OBSOLETE?)", "")
            self.stats["Ship"][key] = value
        self.calc_comp_stats()
        self.calc_crew_stats()

    def calc_comp_stats(self):
        """Calculate component stats and apply them"""
        for category in COMPONENTS:
            category = COMP_TYPES_REVERSE[category]
            if category not in self.ship.components:
                continue
            component = self.ship.components[category]
            if component is None:  # Component not set for this ship
                continue
            self.apply_comp_stats(component)
        self.calc_compound_stats()

    def apply_comp_stats(self, comp: Component):
        """Apply the stats of a component in a category"""
        data = self.ships_data[self.ship.ship_name][comp.category][comp.index].copy()
        # Get the base statistics for this component
        base = data["Base"]["Stats"].copy()
        base.update(data["Stats"])
        base["Cooldown"] = data["Base"]["Cooldown"]
        self.stats[comp.category] = base.copy()
        # Apply enabled upgrades
        for u in (u for u in comp.upgrades.keys() if comp.upgrades[u] is True):
            try:  # Backwards compatibility
                i, s = u  # index, side
            except TypeError:
                i, s = u, 0
            upgrade = data["TalentTree"][i][s].copy()
            upgrade["Target"] = upgrade["Target"].replace("0x00", "")  # Inconsistency in data files
            # Apply statistics found in this upgrade
            target = upgrade.pop("Target", None)
            target = target if target != "Self" else comp.category
            upgrade.update(upgrade.pop("Stats", {}))
            self.apply_stats(target, upgrade)
        # Apply statistics of the base component
        self.apply_stats("Ship", base)

    def calc_crew_stats(self):
        """Apply Crew Passive ability stats to self"""
        for category, companion in self.ship.crew.items():
            if category == "CoPilot" or companion is None:
                continue
            member_data = self.get_crew_member_data(*companion)
            for stats in (member_data["PassiveStats"], member_data["SecondaryPassiveStats"]):
                self.apply_stats(None, stats)

    def apply_stats(self, target: (str, None), stats: dict):
        """Apply a dictionary of statistics"""
        for stat, val in stats.items():
            self.apply_stat(target, stat, val)

    def apply_stat(self, target: (str, None), stat: str, val: float):
        """Apply a statistic to a specific target"""
        if stat in self.ALIASES:
            stat = self.ALIASES[stat]
        if target is None:
            self.apply_stat_guess(stat, val)
        else:
            self.apply_stat_ctg(target, stat, val)

    def apply_stat_guess(self, stat: str, val: float):
        """Guess the correct dictionary for a statistic to be applied to"""
        stat, mul = self.is_multiplicative(stat)
        # Weapons
        applied = False
        for key in ("PrimaryWeapon", "PrimaryWeapon2"):
            if key not in self.stats:
                continue
            if stat in self.stats[key]:
                self.stats[key] = self.update_stat(self.stats[key], stat, mul, val)
                applied = True
        if applied is True:
            return
        # Ship Statistics
        if stat in self["Ship"]:
            self.stats["Ship"] = self.update_stat(self.stats["Ship"], stat, mul, val)
            return

    def apply_stat_ctg(self, category: str, stat: str, val: float):
        """Apply a statistic to a given category"""
        if category == "":
            category = "Ship"
        elif category[-1] == "s":
            category = category[:-1]
            for ctg in (category, category + "2"):
                self.apply_stat_ctg(ctg, stat, val)
            return
        if category not in self.stats:
            return
        stat, mul = self.is_multiplicative(stat)
        self.stats[category] = self.update_stat(self.stats[category], stat, mul, val)

    def calc_compound_stats(self):
        """Calculate a set of specific weapon statistics"""
        for weapon in ShipStats.PRIMARY_WEAPON + ShipStats.SECONDARY_WEAPON:
            if weapon not in self.stats or "Mine" in self.ship[weapon].name:
                continue
            stats = self.stats[weapon].copy()
            base_dmg = stats["Weapon_Base_Damage"]
            hull_mul = stats["Weapon_Hull_Damage_Multiplier"]
            shield_mul = stats["Weapon_Shield_Damage_Multiplier"]
            self.calc_primary_stats_range(
                weapon, "Weapon_Damage_{}_Shields", base_dmg * shield_mul, "{}RangeDamMulti")
            self.calc_primary_stats_range(
                weapon, "Weapon_Damage_{}_Hull", base_dmg * hull_mul, "{}RangeDamMulti")
            base_acc = stats["Weapon_Base_Accuracy"]
            self.calc_primary_stats_range(
                weapon, "Weapon_Accuracy_{}", base_acc, "{}RangeAccMulti")
        for args in ShipStats.MODE_CORRECTED:
            self.calc_power_mode_corrected_stats(*args)
        self.calc_engine_stats()
        self.calc_high_regen_rates()
        self.calc_turning_rates()
        self.calc_mine_stats()

    def calc_mine_stats(self):
        """Calculate Mine statistics"""
        for category in ("Systems", "SecondaryWeapon"):
            if category not in self:
                return
            if not self.ship[category].name.__contains__("Mine"):
                continue
            if "Mine_Shield_Damage" not in self[category]:
                self[category]["Mine_Explosion_Damage_Shields"] = \
                    self[category]["Mine_Explosion_Damage_Hull"] = \
                    self[category]["Mine_Explosion_Damage"]
            self[category]["Mine_Explosion_Damage_Shields"] = \
                self[category]["Mine_Explosion_Damage"] * \
                self[category]["Mine_Shield_Damage"]
            self[category]["Mine_Explosion_Damage_Hull"] = \
                self[category]["Mine_Explosion_Damage"] * \
                self[category]["Mine_Hull_Damage"]

    def calc_engine_stats(self):
        """Calculate custom engine statistics"""
        self.stats["Ship"]["Booster_Speed"] = \
            self.stats["Ship"]["Booster_Speed_Multiplier"] * \
            self.stats["Ship"]["Engine_Base_Speed"]

    def calc_turning_rates(self):
        """Calculate turning rates for pitch and yaw"""
        base = self.stats["Ship"]["Turn_Rate_Modifier"]
        self.stats["Ship"]["Turning_Rate_Pitch"] = base * self.stats["Ship"]["Pitch"]
        self.stats["Ship"]["Turning_Rate_Yaw"] = base * self.stats["Ship"]["Yaw"]

    def calc_high_regen_rates(self):
        """Calculate the high regeneration rates of the power pools"""
        for pool in ShipStats.POWER_POOLS:
            self.stats["Ship"]["Power_{}_Regen_Rate_High".format(pool)] = \
                self.stats["Ship"]["Power_{}_Regen_Rate".format(pool)] * \
                self.stats["Ship"]["Power_{}_Regen_High_Power_Multiplier".format(pool)]

    def calc_primary_stats_range(self, weapon: str, key: str, base: float, mul_key: str):
        """Apply a set of statistics with multipliers"""
        range_muls = map(lambda x: self.stats[weapon].get(mul_key.format(x)), ("pb", "mid", "long"))
        for range_key, range_mul in zip(("Pb", "Mid", "Long"), range_muls):
            value = base * range_mul if "Acc" not in key else base + range_mul
            if "Dam" in key and value == 0.0:
                value = base
            self.stats[weapon][key.format(range_key)] = value

    def calc_power_mode_corrected_stats(self, key: str, mod: str, base: str):
        """Create power mode corrected stats"""
        base = self.stats["Ship"][base]
        for mode in ("Default", "Max", "Min"):
            mode_key = mod.format(mode)
            mode_mod = self.stats["Ship"][mode_key] if mode_key in self.stats["Ship"] else 1.0
            self.stats["Ship"][key.format(mode)] = mode_mod * base

    @staticmethod
    def update_stat(statistics: dict, statistic: str, multiplicative: bool, value: float):
        """
        Update a statistic in a dictionary
        :param statistics: statistics dictionary
        :param statistic: statistic name
        :param multiplicative: bool statistic is multiplicative
        :param value: value to update with
        :return: new statistics dictionary
        """
        if statistic not in statistics:
            return statistics
        if multiplicative is True:
            statistics[statistic] *= value + 1
        else:
            statistics[statistic] += value
        return statistics

    @staticmethod
    def is_multiplicative(statistic):
        """
        Determine whether a statistic is multiplicative or not
        :param statistic: statistic name
        :return: real statistic name str,  multiplicative bool
        """
        multiplicative = "[Pc]" in statistic
        statistic = statistic.replace("[Pc]", "").replace("[Pb]", "")
        return statistic, multiplicative

    def get_crew_member_data(self, faction, category, name):
        faction_data = self.companions_data[faction]
        category_data = [item for item in faction_data if category in item][0][category]
        member_data = [item for item in category_data if item["Name"] == name][0]
        return member_data.copy()

    # Dictionary like functions

    def __getitem__(self, item):
        return self.stats[item]

    def __setitem__(self, item, value):
        self.stats[item] = value

    def __contains__(self, item):
        return item in self.stats

    def __iter__(self):
        """Iterator for all of the statistics and their values"""
        for key, value in self.stats.items():
            yield key, value
