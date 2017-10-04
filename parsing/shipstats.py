# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from parsing.ships import component_types


class ShipStats(object):
    def __init__(self, ship, ships_data, companions_data):
        self.stats = ship.data["Stats"]
        self.components = {}
        print("Opening ShipStats object for ship {}".format(ship.name))
        print("Ship components: {}".format(ship.components))
        for category, component in ship.components.items():
            category = component_types[category] if category in component_types else category
            if category not in ship.data:
                print("Category {} not found for ship {}".format(category, ship.name))
                print("Keys for this ship: {}".format(ship.data.keys()))
                continue
            print("Reading category {} for ship {}".format(category, ship.name))
            if component is None:
                continue
            component_stats = ship.data[category][component.index]["Stats"]
            talent_tree = ship.data[category][component.index]["TalentTree"]
            for upgrade, enabled in component.upgrades.items():
                print("Checking upgrade {} of component {}: {}".format(upgrade, component.name, enabled))
                if enabled is False:
                    continue
                side = None
                if isinstance(upgrade, tuple):
                    upgrade, side = upgrade
                if side:
                    upgrade_stats = talent_tree[upgrade][side]["Stats"]
                else:
                    upgrade_stats = talent_tree[upgrade][0]["Stats"]
                for stat, value in upgrade_stats.items():
                    print("Updating stat {} of component {}".format(stat, component.name))
                    multiplicative = "[Pc]" in stat
                    stat_names = [stat, stat.replace("[Pc]", "")]
                    for stat in stat_names:
                        if stat in component_stats:
                            if multiplicative:
                                value += 1
                                component_stats[stat] = component_stats[stat] * value
                            else:
                                component_stats[stat] += value
                        elif stat in self.stats:
                            if multiplicative:
                                value += 1
                                self.stats[stat] = self.stats[stat] * value
                            else:
                                self.stats[stat] += value
                        else:
                            print("Unknown statistic found: {}".format(stat))
            for stat, value in component_stats.items():
                multiplicative = "[Pc]" in stat
                stat_names = [stat, stat.replace("[Pc]", "")]
                for stat in stat_names:
                    if stat in self.stats:
                        print("Updating component stat {} for component {} in ship {}".format(stat, component.name, ship.name))
                        if multiplicative:
                            value += 1
                            self.stats[stat] = self.stats[stat] * value
                        else:
                            self.stats[stat] += value
                    else:
                        print("Could not find {} in ship statistics".format(stat))
            ship.data[category][component.index]["Stats"] = component_stats
        for category, companion in ship.crew.items():
            # {faction: [{category: [{companion}, {companion}]], [category: []}]}
            if not companion:
                continue
            if category == "CoPilot":
                continue
            faction, category, name = companion
            index = 0
            companion_stats = None
            for index, dictionary in enumerate(companions_data[faction]):
                if category in dictionary:
                    break
            for member in companions_data[faction][index][category]:
                one = member["Name"].strip().lower()
                two = name.strip().lower()
                if one == two:
                    companion_stats = member["PassiveStats"]
                    companion_stats.update(member["SecondaryPassiveStats"])
                    print("Updated companion_stats")
                    break
            for stat, value in companion_stats.items():
                multiplicative = "[Pc]" in stat
                stat_names = [stat, stat.replace("[Pc]", "")]
                for stat in stat_names:
                    if stat in self.stats:
                        if multiplicative:
                            value += 1
                            self.stats[stat] = self.stats[stat] * value
                        else:
                            self.stats[stat] += value

    def __getitem__(self, item):
        return self.stats[item]

    def __setitem__(self, item, value):
        self.stats[item] = value

    def __iter__(self):
        for key, value in self.stats.items():
            yield key, value

