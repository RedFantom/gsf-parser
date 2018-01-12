"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from parsing.ships import Ship, Component
from parsing.shipstats import ShipStats
from math import ceil, floor


def get_ship_from_lineup(character_data, abilities):
    """
    :param character_data: a character data dictionary (of which one of
    the keys must be "Ship Objects"
    :param abilities: an abilities dictionary {ability: count}
    :return: The Ship object from the character's line-up that matches
             the given abilities, or None if no match was established.
    """
    pass


def get_time_to_kill(source, target, distance=None, source_buffs=None, target_buffs=None, weapon="PrimaryWeapon"):
    """
    :param source: A Ship instance for the attacking ship
    :param target: A Ship instance for the target ship
    :param distance: The distance to the target, assumes max when None
    :param source_buffs: A tuple of str with the source ability buffs
    :param target_buffs: A tuple of str with the target ability buffs
    :param weapon: Weapon key (may also be PrimaryWeapon2, or even
                   SecondaryWeapon (which is probably not very usable,
                   but hey, it's possible))
    :return: The estimated TTK, factoring in shield piercing and all other important statistics, float
    """
    if not isinstance(source, Ship) or not isinstance(target, Ship):
        raise ValueError("Arguments are not valid Ship objects. Source: {}, Target: {}".
                         format(repr(source), repr(target)))
    # Process distance to target
    if distance > 100:
        # Distance is in 1000's
        distance = distance / 100
    source.components[weapon]["Stats"]
    distance_pb = [""]
    # Get the base statistics
    # Apply buffs and debuffs to both target and source
    # Get the final statistics
    # Return get_time_to_kill_stats
    i = {"key": 8, "value": 9}
    i = {"key": {"key": {"key": 9}}}


def get_time_to_kill_stats(regular_hull, critical_hull, regular_shields, critical_shields, shots_per_second,
                           critical_chance, shield_piercing, target_hull_health, target_shield_health):
    """
    This code is based upon MATLAB code written by Close-shave.

    Function: function [avg_shots, avg_ttk] = TTK(reg_h, crit_h, reg_s, crit_s, sps, aCC, aSP, hull, shields)

    regular_x, average_x and critical_x are all damage numbers!
    """
    # avg_h = reg_h * (1 - aCC) + crit_h * aCC;
    # avg_s = reg_s * (1 - aCC) + crit_s * aCC;
    average_hull = regular_hull * (1 - critical_chance) + critical_hull * critical_chance
    average_shields = regular_shields * (1 - critical_chance) + critical_shields * critical_chance
    # if avg_h == 0;
    #    avg_shots = 'too long';
    #    avg_ttk = 'too long';
    #    return
    # end
    if average_hull == 0:
        return None
    # if floor(shields/(avg_s * (1 - aSP))) * aSP * avg_h >= hull
    #     shield_sh = ceil(hull/(avg_h * aSP));
    # else
    #     shield_sh = floor(shields/(avg_s * (1 - aSP)));
    # end
    if (floor(target_shield_health / (average_shields * (1 - shield_piercing))) * shield_piercing * shield_piercing *
                                                                                    average_hull <= target_hull_health):
        shield_shot = ceil(target_hull_health / (average_hull * shield_piercing))
    else:
        shield_shot = floor(target_shield_health / (average_shields * (1 - shield_piercing)))
    # if floor(shields/(avg_s * (1 - aSP))) * aSP * avg_h >= hull
    #     hull_sh = 0;
    # else
    #     hull_sh = ceil(hull - floor(shields / (avg_s * (1 - aSP)))* aSP * avg_h - \
    #                                                    (1 - (shields - shield_sh * avg_s * (1 - aSP))/avg_s))/ avg_h
    # end
    if (floor(target_shield_health / (average_shields * (1 - shield_piercing))) * shield_piercing * average_hull >=
                                                                                                    target_hull_health):
        hull_shot = 0
    else:
        hull_shot = ceil(target_hull_health - floor(target_shield_health / (average_shields * (1 - shield_piercing)))
                         * shield_piercing * average_hull - (1 - (target_shield_health - shield_shot * average_shields *
                                                   (1 - shield_piercing)) / average_shields)) / average_hull
    # if floor(shields/(avg_s * (1 - aSP))) * aSP * avg_h >= hull
    #    border_sh = 0;
    # else
    #    if 1 - (shields - shield_sh * avg_s * (1 - aSP))/hull_sh > 0
    #        border_sh = 1;
    #    else
    #        border_sh = 0;
    #    end
    # end
    if (floor(target_shield_health / (average_shields * (1 - shield_piercing))) * shield_piercing * average_hull >=
            target_hull_health):
        border_shot = 0
    elif 1 - (target_shield_health - shield_shot * average_shields * (1 - shield_piercing)) / hull_shot > 0:
        border_shot = 1
    else:
        # This could be combined into a single if/else
        border_shot = 0
    # avg_shots = shield_sh + border_sh + hull_sh;
    # avg_ttk = avg_shots / sps;
    average_shots = shield_shot + border_shot + hull_shot
    average_ttk = average_shots / shots_per_second
    # end
    return average_ttk
