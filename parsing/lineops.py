"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI imports
import datetime
import variables
from data import abilities
import re

# Name of the columns for the pretty event printing functions
colnames = ('time', 'source', 'destination', 'ability', 'effect', 'amount')


def pretty_event(line_dict, start_of_match, active_id):
    """
    Turns a line_dict from realtime.line_to_dictionary() into a formatted line that can be
    inserted into the real-time events Listbox. Also provides the appropriate back- and
    foreground colors based on the settings found in the variables.color_scheme dictionary-like
    object. Function output is like this:
    xx:xx   source  target  ability effect
    timestamp ID    ID      name    damage/activate
    :param line_dict: The return of a realtime.line_to_dictionary()
    :param start_of_match: A datetime object containing the time of the start of the match
    :param active_id: A string containing the active ID number of the player
    :return: Does not return anything, but does put the line into the queue for adding
             to the listbox
    """
    timing = datetime.datetime.strptime(line_dict['time'][:-4], "%H:%M:%S")
    bg_color = None
    fg_color = None
    try:
        delta = timing - start_of_match
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d    " % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
    except TypeError:
        string = "00:00" + 4 * " "
    # If the player name is too long, shorten it
    if variables.rt_name:
        if len(variables.rt_name) > 14:
            variables.rt_name = variables.rt_name[:14]
    if line_dict['source'] == active_id:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['source'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["source"] + (4 + 14 - len(line_dict['source'])) * " "
    if line_dict['destination'] == active_id:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['destination'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["destination"] + (4 + 14 - len(line_dict['destination'])) * " "
    ability = line_dict['ability'].split(' {', 1)[0].strip()
    if ability == "":
        return
    string += ability + (26 - len(ability)) * " "
    if "Damage" in line_dict['effect']:
        if "*" in line_dict['amount']:
            string += "Damage  " + line_dict['amount'].replace("\n", "").replace("*", "") + \
                      (8 - len(line_dict['amount'])) * " " + "Critical"
        else:
            string += "Damage  " + line_dict['amount'].replace("\n", "")
        if line_dict['destination'] == active_id:
            if variables.settings["gui"]["event_colors"] == "basic":
                if line_dict['source'] == active_id:
                    bg_color = variables.colors['selfdmg'][0]
                    fg_color = variables.colors['selfdmg'][1]
                else:
                    bg_color = variables.colors['dmgt_pri'][0]
                    fg_color = variables.colors['dmgt_pri'][1]
            else:
                if line_dict['source'] == active_id:
                    bg_color = variables.colors['selfdmg'][0]
                    fg_color = variables.colors['selfdmg'][1]
                else:
                    if ability in abilities.primaries:
                        bg_color = variables.colors['dmgt_pri'][0]
                        fg_color = variables.colors['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        bg_color = variables.colors['dmgt_sec'][0]
                        fg_color = variables.colors['dmgt_sec'][1]
                    else:
                        bg_color = variables.colors['dmgt_pri'][0]
                        fg_color = variables.colors['dmgt_pri'][1]
        else:
            if ability in abilities.primaries:
                bg_color = variables.colors['dmgd_pri'][0]
                fg_color = variables.colors['dmgd_pri'][1]
            elif ability in abilities.secondaries:
                bg_color = variables.colors['dmgd_sec'][0]
                fg_color = variables.colors['dmgd_sec'][1]
            else:
                bg_color = variables.colors['dmgd_pri'][0]
                fg_color = variables.colors['dmgd_pri'][1]
    elif "Heal" in line_dict['effect']:
        string += "Heal    " + line_dict['amount'].replace("\n", "")
        if line_dict['source'] == active_id:
            bg_color = variables.colors['selfheal'][0]
            fg_color = variables.colors['selfheal'][1]
        else:
            bg_color = variables.colors['healing'][0]
            fg_color = variables.colors['healing'][1]
    elif "AbilityActivate" in line_dict['effect']:
        string += "AbilityActivate"
        if variables.settings["gui"]["event_colors"] == "advanced":
            for engine in abilities.engines:
                if engine in string:
                    bg_color = variables.colors['engine'][0]
                    fg_color = variables.colors['engine'][1]
                    break
            for shield in abilities.shields:
                if shield in string:
                    bg_color = variables.colors['shield'][0]
                    fg_color = variables.colors['shield'][1]
                    break
            for system in abilities.systems:
                if system in string:
                    bg_color = variables.colors['system'][0]
                    fg_color = variables.colors['system'][1]
                    break
            if not bg_color:
                bg_color = variables.colors['other'][0]
                fg_color = variables.colors['other'][1]
        elif variables.settings["gui"]["event_colors"] == "basic":
            bg_color = variables.colors['other'][0]
            fg_color = variables.colors['other'][1]
    else:
        return
    if not bg_color:
        bg_color = variables.colors['default'][0]
        fg_color = variables.colors['default'][1]
    variables.insert_queue.put((string, bg_color, fg_color))


def print_event(line_dict, start_of_match, player):
    """
    Turns a line_dict from realtime.line_to_dictionary() into a formatted line that can be
    inserted into the events Listbox of the Toplevel. Also provides the appropriate back- and
    foreground colors based on the settings found in the variables.color_scheme dictionary-like
    object. Function output is like this:
    xx:xx   source  target  ability effect
    timestamp ID    ID      name    damage/activate
    :param line_dict: dictionary of realtime.line_to_dictionary()
    :param start_of_match: datetime object that represents the start of the match
    :param player: LIST of ID numbers of the player
    :return: string, bg_color (string) and fg_color (string)
    """
    line_dict_new = None
    try:
        line_dict_new = line_to_dictionary(line_dict)
    except TypeError:
        pass
    if not line_dict_new:
        pass
    else:
        line_dict = line_dict_new
    timing = datetime.datetime.strptime(line_dict['time'][:-4], "%H:%M:%S")
    start_of_match = datetime.datetime.strptime(start_of_match, "%H:%M:%S")
    bg_color = None
    fg_color = None
    try:
        delta = timing - start_of_match
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d    " % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
    except TypeError:
        string = "00:00" + 4 * " "
    except:
        print("[DEBUG] An unknown error occurred while doing the delta thing")
        return
    # If the player name is too long, shorten it
    if variables.rt_name:
        if len(variables.rt_name) > 14:
            variables.rt_name = variables.rt_name[:14]
    if line_dict['source'] in player:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['source'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["source"] + (4 + 14 - len(line_dict['source'])) * " "
    if line_dict['destination'] in player:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['destination'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["destination"] + (4 + 14 - len(line_dict['destination'])) * " "
    ability = line_dict['ability'].split(' {', 1)[0].strip()
    if ability == "":
        return
    string += ability + (26 - len(ability)) * " "
    if "Damage" in line_dict['effect']:
        if "*" in line_dict['amount']:
            string += "Damage  " + line_dict['amount'].replace("\n", "").replace("*", "") + \
                      (8 - len(line_dict['amount'])) * " " + "Critical"
        else:
            string += "Damage  " + line_dict['amount'].replace("\n", "")
        if line_dict['destination'] in player:
            if variables.settings["gui"]["event_colors"] == "basic":
                if line_dict['source'] in player:
                    bg_color = variables.colors['selfdmg'][0]
                    fg_color = variables.colors['selfdmg'][1]
                else:
                    bg_color = variables.colors['dmgt_pri'][0]
                    fg_color = variables.colors['dmgt_pri'][1]
            else:
                if line_dict['source'] in player:
                    bg_color = variables.colors['selfdmg'][0]
                    fg_color = variables.colors['selfdmg'][1]
                else:
                    if ability in abilities.primaries:
                        bg_color = variables.colors['dmgt_pri'][0]
                        fg_color = variables.colors['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        bg_color = variables.colors['dmgt_sec'][0]
                        fg_color = variables.colors['dmgt_sec'][1]
                    else:
                        bg_color = variables.colors['dmgt_pri'][0]
                        fg_color = variables.colors['dmgt_pri'][1]
        else:
            if ability in abilities.primaries:
                bg_color = variables.colors['dmgd_pri'][0]
                fg_color = variables.colors['dmgd_pri'][1]
            elif ability in abilities.secondaries:
                bg_color = variables.colors['dmgd_sec'][0]
                fg_color = variables.colors['dmgd_sec'][1]
            else:
                bg_color = variables.colors['dmgd_pri'][0]
                fg_color = variables.colors['dmgd_pri'][1]
    elif "Heal" in line_dict['effect']:
        string += "Heal    " + line_dict['amount'].replace("\n", "")
        if line_dict['source'] in player:
            bg_color = variables.colors['selfheal'][0]
            fg_color = variables.colors['selfheal'][1]
        else:
            bg_color = variables.colors['healing'][0]
            fg_color = variables.colors['healing'][1]
    elif "AbilityActivate" in line_dict['effect']:
        string += "AbilityActivate"
        if variables.settings["gui"]["event_colors"] == "advanced":
            for engine in abilities.engines:
                if engine in string:
                    bg_color = variables.colors['engine'][0]
                    fg_color = variables.colors['engine'][1]
                    break
            for shield in abilities.shields:
                if shield in string:
                    bg_color = variables.colors['shield'][0]
                    fg_color = variables.colors['shield'][1]
                    break
            for system in abilities.systems:
                if system in string:
                    bg_color = variables.colors['system'][0]
                    fg_color = variables.colors['system'][1]
                    break
            if not bg_color:
                bg_color = variables.colors['other'][0]
                fg_color = variables.colors['other'][1]
        elif variables.settings["gui"]["event_colors"] == "basic":
            bg_color = variables.colors['other'][0]
            fg_color = variables.colors['other'][1]
    else:
        return
    if not bg_color:
        bg_color = variables.colors['default'][0]
        fg_color = variables.colors['default'][1]
    return string, bg_color, fg_color


def line_to_dictionary(line):
    logpaths = r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \((.*?)\)'
    logpath = re.compile(logpaths)

    group = logpath.match(line) if isinstance(line, str) else logpath.match(line.decode('cp1252'))
    try:
        tuple_ = group.groups()
    except AttributeError as err:
        print(
            ("[DEBUG] line_to_dictionary(): arg:", line, "'tuple = group.groups()' error raised, with group: ", group))
        print(err)
        return

    colnames = ('time', 'source', 'destination', 'ability', 'effect', 'amount')
    log = dict(list(zip(colnames, tuple_)))

    """
    if not log['ability'] is '':
        log['ability'] = log['ability'].rsplit(None, 1)[1][1:-1]
    """

    if not log['amount'] is '':
        log['amount'] = log['amount'].split(None, 1)[0]

    return log
