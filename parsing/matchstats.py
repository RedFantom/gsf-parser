# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import decimal
import datetime
import variables
import parse
import realtime


def match_statistics(match):
    """
    Does the same as file_statistics but for a match

    :param match: a parse.splitter(...)[match] matrix of spawns
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
    total_abilitiesdict = {}
    total_damagetaken = 0
    total_damagedealt = 0
    total_healingrecv = 0
    total_selfdamage = 0
    total_enemies = []
    total_criticalcount = 0
    total_hitcount = 0
    total_shipsdict = {}
    total_enemydamaged = {}
    total_enemydamaget = {}
    total_killsassists = 0
    ships_uncounted = 0
    for spawn in match:
        (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
         criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn,
                                                                                             variables.player_numbers)
        total_abilitiesdict.update(abilitiesdict)
        total_damagetaken += damagetaken
        total_damagedealt += damagedealt
        total_healingrecv += healingreceived
        total_selfdamage += selfdamage
        for enemy in enemies:
            if enemy not in total_enemies:
                total_enemies.append(enemy)
        total_criticalcount += criticalcount
        total_hitcount += hitcount
        for key, value in enemydamaged.iteritems():
            if key in total_enemydamaged:
                total_enemydamaged[key] += value
            else:
                total_enemydamaged[key] = value
        for key, value in enemydamaget.iteritems():
            if key in total_enemydamaget:
                total_enemydamaget[key] += value
            else:
                total_enemydamaget[key] = value
        if len(ships_list) != 1:
            ships_uncounted += 1
            ships_list = []
        for ship in ships_list:
            if ship in total_shipsdict:
                total_shipsdict[ship] += 1
            else:
                total_shipsdict[ship] = 1
    for enemy in total_enemies:
        if total_enemydamaget[enemy] > 0:
            total_killsassists += 1
    try:
        total_criticalluck = decimal.Decimal(float(total_criticalcount) / float(total_hitcount))
        total_criticalluck = round(total_criticalluck * 100, 2)
    except ZeroDivisionError:
        total_criticalluck = 0
    total_shipsdict["Uncounted"] = ships_uncounted
    delta = datetime.datetime.strptime(
        realtime.line_to_dictionary(match[len(match) - 1][len(match[len(match) - 1]) - 1])
        ['time'][:-4].strip(), "%H:%M:%S") - \
            datetime.datetime.strptime(variables.match_timing.strip(), "%H:%M:%S")
    elapsed = divmod(delta.total_seconds(), 60)
    string = "%02d:%02d" % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
    try:
        dps = round(total_damagedealt / delta.total_seconds(), 1)
    except ZeroDivisionError:
        dps = 0
    try:
        damage_ratio_string = str(
            str(round(float(total_damagedealt) / float(total_damagetaken), 1)) + " : 1") + "\n"
    except ZeroDivisionError:
        damage_ratio_string = "0.0 : 1\n"
    statistics_string = (str(total_killsassists) + " enemies" + "\n" + str(total_damagedealt) + "\n" +
                         str(total_damagetaken) + "\n" + damage_ratio_string +
                         str(total_selfdamage) + "\n" + str(total_healingrecv) + "\n" +
                         str(total_hitcount) + "\n" + str(total_criticalcount) + "\n" +
                         str(total_criticalluck) + "%" + "\n" + str(len(match) - 1) + "\n" + string + "\n" + str(
        dps))
    return (total_abilitiesdict, statistics_string, total_shipsdict, total_enemies, total_enemydamaged,
            total_enemydamaget)
