# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import decimal
from . import parse
from parsing import abilities
import os
import variables


def file_statistics(filename, file_cube):
    """
     Puts the statistics found in a file_cube from parse.splitter() into a
     format that is usable by the file_frame to display them to the user
     :param file_cube: An already split file into a file_cube
     :return: abilities_string, a string for in the abilities tab
              statistics_string, a string for in the statistics label in the
                                 statistics tab
              total_shipsdict, a dictionary with ships as keys and the amount
                               of times they occurred as values
              total_enemies, a list of all enemies encountered in the whole
                             folder
              total_enemydamaged, a dictionary with the enemies as keys and
                                  their respective damage taken from you as
                                  values
              total_enemydamaget, a dictionary with the enemies as keys and
                                  their respective damage dealt to you as
                                  values
              uncounted, the amount of ships that was not counted in the
                         total_shipsdict, if there was more than one
                         possibility
    """
    lines = []
    for match in file_cube:
        for spawn in match:
            for line in spawn:
                lines.append(line)
    player_list = parse.determinePlayer(lines)
    _, match_timings, spawn_timings = parse.splitter(lines, player_list)
    with open(os.path.join(variables.settings_obj["parsing"]["cl_path"], filename), "r") as fi:
        name = parse.determinePlayerName(fi.readlines())
    (abs, damagetaken, damagedealt, selfdamage, healingreceived, enemies, criticalcount, criticalluck,
     hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings) = \
        parse.parse_file(file_cube, player_list, match_timings, spawn_timings)
    total_abilities = {}
    total_enemies = []

    for mat in abs:
        for dic in mat:
            for (key, value) in dic.items():
                if key not in total_abilities:
                    total_abilities[key] = value
                else:
                    total_abilities[key] += value
    total_damagetaken = sum(sum(lst) for lst in damagetaken)
    total_damagedealt = sum(sum(lst) for lst in damagedealt)
    total_selfdamage = sum(sum(lst) for lst in selfdamage)
    total_healingrecv = sum(sum(lst) for lst in healingreceived)
    total_criticalcount = sum(sum(lst) for lst in criticalcount)
    total_hitcount = sum(sum(lst) for lst in hitcount)
    for matrix in enemies:
        for lst in matrix:
            for enemy in lst:
                if enemy not in total_enemies:
                    total_enemies.append(enemy)
    try:
        total_criticalluck = decimal.Decimal(total_criticalcount / total_hitcount)
    except ZeroDivisionError:
        total_criticalluck = 0
    total_enemydamaged = enemydamaged
    total_enemydamaget = enemydamaget
    total_shipsdict = {}
    uncounted = 0
    for ship in abilities.ships:
        total_shipsdict[ship] = 0
    for match in file_cube:
        for spawn in match:
            ships_possible = parse.parse_spawn(spawn, player_list)[9]
            if len(ships_possible) == 1:
                total_shipsdict[ships_possible[0]] += 1
            else:
                uncounted += 1
    total_killsassists = 0
    for enemy in total_enemies:
        if total_enemydamaget[enemy] > 0:
            total_killsassists += 1
    total_criticalluck = round(total_criticalluck * 100, 2)
    deaths = 0
    for match in file_cube:
        deaths += len(match)
    try:
        damage_ratio_string = str(
            str(round(float(total_damagedealt) / float(total_damagetaken), 1)) + " : 1") + "\n"
    except ZeroDivisionError:
        damage_ratio_string = "0.0 : 1\n"
    statistics_string = (name + "\n" +
        str(total_killsassists) + " enemies" + "\n" + str(total_damagedealt) + "\n" +
        str(total_damagetaken) + "\n" + damage_ratio_string + str(total_selfdamage) + "\n" +
        str(total_healingrecv) + "\n" + str(total_hitcount) + "\n" +
        str(total_criticalcount) + "\n" + str(total_criticalluck) + "%" +
        "\n" + str(deaths) + "\n-\n-")
    return (total_abilities, statistics_string, total_shipsdict, total_enemies, total_enemydamaged,
            total_enemydamaget, uncounted)
