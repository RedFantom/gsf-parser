# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter.messagebox
import datetime
from . import abilities
from . import parse
from .lineops import line_to_dictionary
import os
import variables


def spawn_statistics(file_name, spawn, spawn_timing):
    """
    Does the same as match_statistics but for a spawn

    :param spawn: A parse.splitter(...)[match][spawn] list of events
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
    player_numbers = parse.determinePlayer(spawn)
    (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
     criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn, player_numbers)

    with open(os.path.join(variables.settings_obj["parsing"]["cl_path"], file_name), "r") as fi:
        name = parse.determinePlayerName(fi.readlines())
    killsassists = 0
    for enemy in enemies:
        if enemydamaget[enemy] > 0:
            killsassists += 1
    ship_components = []
    for key in abilitiesdict:
        if key in abilities.components:
            ship_components.append(key)
    comps = ["Primary", "Secondary", "Engine", "Shield", "System"]
    for component in ship_components:
        if component in abilities.primaries:
            if "Rycer" in ships_list:
                if comps[0] == "Primary":
                    comps[0] = component
                else:
                    comps[0] += "/" + component
            else:
                comps[0] = component
        elif component in abilities.secondaries:
            if "Quell" in ships_list:
                if comps[1] == "Secondary":
                    comps[1] = component
                else:
                    comps[1] += "/" + component
            else:
                comps[1] = component
        elif component in abilities.engines:
            comps[2] = component
        elif component in abilities.shields:
            comps[3] = component
        elif component in abilities.systems:
            comps[4] = component
        else:
            tkinter.messagebox.showinfo("WHAT?!", "DID GSF GET AN UPDATE?!")
    if "Primary" in comps:
        del comps[comps.index("Primary")]
    if "Secondary" in comps:
        del comps[comps.index("Secondary")]
    if "Engine" in comps:
        del comps[comps.index("Engine")]
    if "Shield" in comps:
        del comps[comps.index("Shield")]
    if "System" in comps:
        del comps[comps.index("System")]
    last_line_dict = line_to_dictionary(spawn[len(spawn) - 1])
    timing = datetime.datetime.strptime(last_line_dict['time'][:-4], "%H:%M:%S")
    delta = timing - spawn_timing
    elapsed = divmod(delta.total_seconds(), 60)
    string = "%02d:%02d" % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
    try:
        dps = round(damagedealt / delta.total_seconds(), 1)
    except ZeroDivisionError:
        dps = 0
    try:
        damage_ratio_string = str(str(round(float(damagedealt) / float(damagetaken), 1)) + " : 1") + "\n"
    except ZeroDivisionError:
        damage_ratio_string = "0.0 : 1\n"
    statistics_string = (
        name + "\n" +
        str(killsassists) + " enemies" + "\n" +
        str(damagedealt) + "\n" +
        str(damagetaken) + "\n" +
        damage_ratio_string +
        str(selfdamage) + "\n" +
        str(healingreceived) + "\n" +
        str(hitcount) + "\n" +
        str(criticalcount) + "\n" +
        str(criticalluck) + "%" + "\n" + "-\n" + string + "\n" +
        str(dps)
    )
    return abilitiesdict, statistics_string, ships_list, comps, enemies, enemydamaged, enemydamaget
