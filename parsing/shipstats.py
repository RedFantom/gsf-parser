# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from parsing.ships import component_types, Ship, Component


class ShipStats(object):
    """
    Class to calculate the statistics for a given ship object. Uses the data found in the databases to calculate
    statistics for the main ship and each component.
    """

    def __init__(self, ship, ships_data, companions_data):
        """
        :param ship: Ship object
        :param ships_data: ships.db contents
        :param companions_data: companions.db contents
        """
        if not isinstance(ship, Ship):
            raise ValueError("ShipStats can only be initialized with a Ship object")
        self.stats = {}
        self.ship = ship
        self.ships_data = ships_data
        self.companions_data = companions_data
        self.calculate_ship_statistics()

    def calculate_ship_statistics(self):
        """
        Calculate the statistics of the Ship Object
        """
        self.stats["Ship"] = self.ships_data[self.ship.ship_name]["Stats"]
        # Go over components
        for category in component_types.keys():
            # The categories are gone over in a certain order
            if category not in self.ship.components:
                continue
            component = self.ship.components[category]
            # If component is None, then the component is not correctly set
            if component is None:
                continue
            if not isinstance(component, Component):
                raise ValueError()
            category = component_types[category]
            # Get the data belonging to the component
            component_data = self.ships_data[self.ship.ship_name][category][component.index]
            # Go over the upgrades for the component first
            base_stats = {}
            self.stats[category] = component_data["Stats"]
            for upgrade, state in component.upgrades.items():
                # Check the state first for efficiency
                if state is False:
                    continue
                # The upgrade can either be an index, or a tuple of indexes
                # The TalentTree of the component is built of lists
                if isinstance(upgrade, tuple):
                    # Tuple (upgrade_index, side_index)
                    upgrade_index, side_index = upgrade
                    upgrade_data = component_data["TalentTree"][upgrade_index][side_index]
                else:
                    # upgrade_index
                    upgrade_data = component_data["TalentTree"][upgrade][0]
                if not isinstance(upgrade_data, dict):
                    raise ValueError(
                        "upgrade_data was not a dict for category '{}' and upgrade index '{}': {}".format(
                            category, upgrade, upgrade_data
                        )
                    )
                # upgrade_data now contains a dictionary of data of the upgrade
                if upgrade_data["Target"] == "":
                    # Go over the statistics of the upgrade
                    for stat, value in upgrade_data["Stats"].items():
                        statistic, multiplicative = ShipStats.is_multiplicative(stat)
                        base_stats = ShipStats.update_statistic(
                            component_data["Base"]["Stats"], statistic, multiplicative, value
                        )
                        self.stats[category] = ShipStats.update_statistic(
                            self.stats[category], statistic, multiplicative, value
                        )
                else:
                    print("Target of upgrade for {} was {}".format(component.name, upgrade_data["Target"]))
            # These are the statistics to go over
            component_stats = base_stats
            for stat, value in component_stats.items():
                # Process the statistic name
                statistic, multiplicative = ShipStats.is_multiplicative(stat)
                # All statistics in component["Base"]["Stats"] are expected to be found in the ship statistics as well.
                if statistic not in self.stats["Ship"]:
                    raise ValueError(
                        "Invalid statistic '{}' found for category '{}'\n{}".format(stat, category, self.stats["Ship"])
                    )
                # Perform the calculation
                self.stats["Ship"] = ShipStats.update_statistic(self.stats["Ship"], statistic, multiplicative, value)
        # Go over Crew
        for category, companion in self.ship.crew.items():
            print(category, ":", companion)
            pass

    """
    Functions to process statistics
    """

    @staticmethod
    def update_statistic(statistics, statistic, multiplicative, value):
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
        statistic = statistic.replace("[Pc]", "")
        return statistic, multiplicative

    # Dictionary like functions

    def __getitem__(self, item):
        return self.stats[item]

    def __setitem__(self, item, value):
        self.stats[item] = value

    def __contains__(self, item):
        return item in self.stats

    def __iter__(self):
        """
        Iterator for all of the statistics and their values
        """
        for key, value in self.stats.items():
            yield key, value

