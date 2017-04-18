# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkMessageBox
import os
import decimal
import datetime

import variables
import abilities
import parse
import realtime
import toplevels


# Function that returns True if a file contains any GSF events
def check_gsf(file_name):
    with open(file_name, "r") as file_obj:
        for line in file_obj:
            if "@" not in line:
                file_obj.close()
                return True
            else:
                continue
    if not file_obj.closed:
        raise
    return False


# Class to calculate various statistics from files, and even folders
class statistics:
    # Calculate the statistics for a whole folder
    @staticmethod
    def folder_statistics():
        """
        Parses all files in the Current Working Directory by getting al .txt
        files in the folder and then returns the results in formats that can be
        used by the file_frame to set all the required strings to show the
        results to the user.

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

        # Add a CombatLogs in a folder with GSF matches to a list of names
        file_list = []
        for file_name in os.listdir(variables.settings_obj.cl_path):
            if file_name.endswith(".txt") and check_gsf(variables.settings_obj.cl_path + "/" + file_name):
                file_list.append(variables.settings_obj.cl_path + "/" + file_name)

        # Define all variables needed to store the statistics
        total_ddealt = 0
        total_dtaken = 0
        total_hrecvd = 0
        total_selfdmg = 0
        match_count = 0
        total_hitcount = 0
        total_criticalcount = 0
        total_deaths = 0
        total_shipsdict = {}
        for ship in abilities.ships:
            total_shipsdict[ship] = 0
        total_abilities = {}
        total_enemies = []
        total_enemydamaged = {}
        total_enemydamaget = {}
        total_timeplayed = None
        start_time = None
        uncounted = 0
        # TODO: Add the names of all GSF characters found in the folder to the fileframe
        # TODO: interface as an addtional statistic
        player_names = []
        # Create a splash screen for the user to see the progress of parsing
        splash = toplevels.splash_screen(variables.main_window, max=len(file_list))
        # Start looping through the files
        variables.files_done = 0
        for name in file_list:
            variables.files_done += 1
            # Update the progress of the progress bar of the splash screen
            splash.update_progress()
            # Open the file and read the lines into memory (up to ~2MiB)
            with open(name, "r") as file_object:
                lines = file_object.readlines()
            # Determine the player name
            name = parse.determinePlayerName(lines)
            # Add the player name to the list of player names
            if name not in player_names:
                player_names.append(name)
            # Determine the ID numbers used by the player
            player_numbers = parse.determinePlayer(lines)
            # Split the file into matches and the matches into spawns
            file_cube, match_timings, spawn_timings = parse.splitter(lines, player_numbers)
            first = True
            # Calculate how long the matches lasted in this file and add them to the total
            for timing in match_timings:
                if first:
                    first = False
                    start_time = timing
                elif not first:
                    first = True
                    end_time = timing
                    if not total_timeplayed:
                        total_timeplayed = (end_time - start_time)
                    else:
                        total_timeplayed += (end_time - start_time)
            # Then get the useful information out of the matches and spawns
            (abilitiesdict, damagetaken, damagedealt, selfdamage, healingreceived, enemies,
             criticalcount, criticalluck, hitcount, enemydamaged, enemydamaget, match_timings,
             spawn_timings) = parse.parse_file(file_cube, player_numbers, match_timings, spawn_timings)
            # Start looping through the matrix of abilities dictionaries with [match][spawn][key]
            for match in abilitiesdict:
                match_count += 1
                # spawn_abs = spawn_abilities with [key]
                for spawn_abs in match:
                    # Get the ships that could have been flown
                    ships_possible = parse.determineShip(spawn_abs)
                    # Add the abilities to the total dictionary of abilities and their amount of
                    # occurrences to display in the abilities tab eventually
                    for key, value in spawn_abs.iteritems():
                        if key not in total_abilities:
                            total_abilities[key] = value
                        else:
                            total_abilities[key] += value
                    # If more than one ship is possible, do not count it
                    if len(ships_possible) == 1:
                        # Start counting the ships in the total_shipsdict
                        if ships_possible[0] == "Razorwire":
                            total_shipsdict["Razorwire"] += 1
                        elif ships_possible[0] == "Legion":
                            total_shipsdict["Legion"] += 1
                        elif ships_possible[0] == "Decimus":
                            total_shipsdict["Decimus"] += 1
                        elif ships_possible[0] == "Bloodmark":
                            total_shipsdict["Bloodmark"] += 1
                        elif ships_possible[0] == "Sting":
                            total_shipsdict["Sting"] += 1
                        elif ships_possible[0] == "Blackbolt":
                            total_shipsdict["Blackbolt"] += 1
                        elif ships_possible[0] == "Mangler":
                            total_shipsdict["Mangler"] += 1
                        elif ships_possible[0] == "Dustmaker":
                            total_shipsdict["Dustmaker"] += 1
                        elif ships_possible[0] == "Jurgoran":
                            total_shipsdict["Jurgoran"] += 1
                        elif ships_possible[0] == "Imperium":
                            total_shipsdict["Imperium"] += 1
                        elif ships_possible[0] == "Quell":
                            total_shipsdict["Quell"] += 1
                        elif ships_possible[0] == "Rycer":
                            total_shipsdict["Rycer"] += 1
                        # If a ship is not one of these twelve, raise an error
                        # Did GSF get an update? Probably not.
                        else:
                            raise ValueError("Ship is not valid: %s" % ships_possible[0])
                    # Add 1 to uncounted if multiple possibilities
                    else:
                        uncounted += 1
            # Loop through the enemies to add them to the whole list
            # TODO: Build checks to check if one ID number occurs multiple times in the same folder
            # TODO: If so, the user must check if those were on the same server
            # TODO: If so, that should be reported somehow, as that can have impact on the workings
            # TODO: Of the GSF-Server. Currently, I (RedFantom) do not think this is the case.
            for matrix in enemies:
                for list in matrix:
                    for item in list:
                        if item not in total_enemies:
                            # TODO: The hooks of the client.py connection go here to identify enemies
                            total_enemies.append(item)
            # Add the totals of enemy damage dealt
            for key, value in enemydamaged.iteritems():
                if key in total_enemydamaged:
                    total_enemydamaged[key] += value
                else:
                    total_enemydamaged[key] = value
            # And enemy damage taken...
            for key, value in enemydamaget.iteritems():
                if key in total_enemydamaget:
                    total_enemydamaget[key] += value
                else:
                    total_enemydamaget[key] = value
            # And own damage taken...
            for list in damagetaken:
                for number in list:
                    total_dtaken += number
            # Own damage dealt...
            for list in damagedealt:
                for number in list:
                    total_ddealt += number
            # Own healing received...
            for list in healingreceived:
                for number in list:
                    total_hrecvd += number
            # Own selfdamage...
            for list in selfdamage:
                for number in list:
                    total_selfdmg += number
            # DEPRECATED
            # This is already done in line 247-248 and 249-250
            # Technically doing it twice does not affect the criticalluck,
            # But still it's not a good idea.
            '''
            for list in criticalluck:
                for number in list:
                    criticalnumber += 1
                    criticaltotal += number
            '''
            # DEPRECATED
            # This already done in the abilities matrixes loop
            '''
            for list in abilitiesdict:
                for dict in list:
                    for key, value in dict.iteritems():
                        if key in total_abilities:
                            total_abilities[key] += value
                        else:
                            total_abilities[key] = value
            '''
            # Add the hitcount to totals for the criticalluck
            for list in hitcount:
                total_hitcount += sum(list)
            for list in criticalcount:
                total_criticalcount += sum(list)
                # Add the amount of deaths to the total by counting spawns
            total_deaths += sum([(len(list) - 1) for list in criticalluck])
            # End of file loop!

        # Use a divmod to get both the minutes and seconds played
        (total_timeplayed_minutes, total_timeplayed_seconds) = divmod(total_timeplayed.seconds, 60)
        # Try to get the average DPS
        # Set to zero if no files are in the folder
        try:
            total_dps = round(total_ddealt / total_timeplayed.seconds, 1)
        except ZeroDivisionError as e:
            if len(file_list) == 0:
                total_dps = 0
            else:
                raise e
        # Try to get the total criticalluck with a Decimal and a float division
        try:
            total_criticalluck = decimal.Decimal(float(total_criticalcount / total_hitcount))
        except ZeroDivisionError as e:
            if len(file_list) == 0:
                total_criticalluck = 0
            else:
                raise e
        # Update the criticalluck to the right format for in the string
        total_criticalluck = round(total_criticalluck * 100, 2)
        try:
            damage_ratio_string = str(str(round(float(total_ddealt) / float(total_dtaken), 1)) + " : 1") + "\n"
        except ZeroDivisionError as e:
            if len(file_list) == 0:
                damage_ratio_string = "0.0 : 1\n"
            else:
                raise e
        # Calculate the amount of enemies damage was dealt to
        # This is not actually kills+assits, but more like
        # kills+assists+assists_on_enemies_that_didnt_die
        total_killassists = 0
        for value in total_enemydamaget.itervalues():
            if value > 0:
                total_killassists += 1
        splash.destroy()
        # Return all statistics calculated in a nice format
        statistics_string = (
            str(total_killassists) + " enemies" + "\n" + str(total_ddealt) + "\n" + str(total_dtaken) + "\n" +
            damage_ratio_string + str(total_selfdmg) + "\n" + str(total_hrecvd) + "\n" +
            str(total_hitcount) + "\n" + str(total_criticalcount) + "\n" +
            str(total_criticalluck) + "%\n" + str(total_deaths) + "\n" +
            str(total_timeplayed_minutes) + ":" + str(total_timeplayed_seconds) + "\n" +
            str(total_dps))
        # Return all the stuff
        return (total_abilities, statistics_string, total_shipsdict, total_enemies, total_enemydamaged,
                total_enemydamaget, uncounted)

    @staticmethod
    def file_statistics(file_cube):
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
        player_list = []
        for match in file_cube:
            for spawn in match:
                player = parse.determinePlayer(spawn)
                for id in player:
                    player_list.append(id)

        (abs, damagetaken, damagedealt, selfdamage, healingreceived, enemies, criticalcount, criticalluck,
         hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings) = \
            parse.parse_file(file_cube, player_list, variables.match_timings, variables.spawn_timings)
        total_abilities = {}
        total_damagetaken = 0
        total_damagedealt = 0
        total_selfdamage = 0
        total_healingrecv = 0
        total_enemies = []
        total_criticalcount = 0
        total_hitcount = 0

        for mat in abs:
            for dic in mat:
                for (key, value) in dic.iteritems():
                    if key not in total_abilities:
                        total_abilities[key] = value
                    else:
                        total_abilities[key] += value
        for lst in damagetaken:
            for amount in lst:
                total_damagetaken += amount
        for lst in damagedealt:
            for amount in lst:
                total_damagedealt += amount
        for lst in selfdamage:
            for amount in lst:
                total_selfdamage += amount
        for lst in healingreceived:
            for amount in lst:
                total_healingrecv += amount
        for matrix in enemies:
            for lst in matrix:
                for enemy in lst:
                    if enemy not in total_enemies:
                        total_enemies.append(enemy)
        for lst in criticalcount:
            for amount in lst:
                total_criticalcount += amount
        for lst in hitcount:
            for amount in lst:
                total_hitcount += amount
        try:
            total_criticalluck = decimal.Decimal(float(total_criticalcount / total_hitcount))
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
                    if ships_possible[0] == "Razorwire":
                        total_shipsdict["Razorwire"] += 1
                    elif ships_possible[0] == "Legion":
                        total_shipsdict["Legion"] += 1
                    elif ships_possible[0] == "Decimus":
                        total_shipsdict["Decimus"] += 1
                    elif ships_possible[0] == "Bloodmark":
                        total_shipsdict["Bloodmark"] += 1
                    elif ships_possible[0] == "Sting":
                        total_shipsdict["Sting"] += 1
                    elif ships_possible[0] == "Blackbolt":
                        total_shipsdict["Blackbolt"] += 1
                    elif ships_possible[0] == "Mangler":
                        total_shipsdict["Mangler"] += 1
                    elif ships_possible[0] == "Dustmaker":
                        total_shipsdict["Dustmaker"] += 1
                    elif ships_possible[0] == "Jurgoran":
                        total_shipsdict["Jurgoran"] += 1
                    elif ships_possible[0] == "Imperium":
                        total_shipsdict["Imperium"] += 1
                    elif ships_possible[0] == "Quell":
                        total_shipsdict["Quell"] += 1
                    elif ships_possible[0] == "Rycer":
                        total_shipsdict["Rycer"] += 1
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
        statistics_string = (
            str(total_killsassists) + " enemies" + "\n" + str(total_damagedealt) + "\n" +
            str(total_damagetaken) + "\n" + damage_ratio_string + str(total_selfdamage) + "\n" +
            str(total_healingrecv) + "\n" + str(total_hitcount) + "\n" +
            str(total_criticalcount) + "\n" + str(total_criticalluck) + "%" +
            "\n" + str(deaths) + "\n-\n-")
        return (total_abilities, statistics_string, total_shipsdict, total_enemies, total_enemydamaged,
                total_enemydamaget, uncounted)

    @staticmethod
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

    @staticmethod
    def spawn_statistics(spawn):
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
        (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
         criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn,
                                                                                             variables.player_numbers)
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
                tkMessageBox.showinfo("WHAT?!", "DID GSF GET AN UPDATE?!")
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
        last_line_dict = realtime.line_to_dictionary(spawn[len(spawn) - 1])
        timing = datetime.datetime.strptime(last_line_dict['time'][:-4], "%H:%M:%S")
        delta = timing - datetime.datetime.strptime(variables.spawn_timing.strip(), "%H:%M:%S")
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
        statistics_string = (str(killsassists) + " enemies" + "\n" + str(damagedealt) + "\n" + str(damagetaken) + "\n" +
                             damage_ratio_string +
                             str(selfdamage) + "\n" + str(healingreceived) + "\n" +
                             str(hitcount) + "\n" + str(criticalcount) + "\n" +
                             str(criticalluck) + "%" + "\n" + "-\n" + string + "\n" + str(dps))
        return abilitiesdict, statistics_string, ships_list, comps, enemies, enemydamaged, enemydamaget


# Name of the columns for the pretty event printing functions
# TODO: make them visible for the user in some good format
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
    except:
        print "[DEBUG] An unknown error occurred while doing the delta thing"
        return
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
            if variables.settings_obj.event_colors == "basic":
                if line_dict['source'] == active_id:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    bg_color = variables.color_scheme['dmgt_pri'][0]
                    fg_color = variables.color_scheme['dmgt_pri'][1]
            else:
                if line_dict['source'] == active_id:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    if ability in abilities.primaries:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        bg_color = variables.color_scheme['dmgt_sec'][0]
                        fg_color = variables.color_scheme['dmgt_sec'][1]
                    else:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
        else:
            if ability in abilities.primaries:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
            elif ability in abilities.secondaries:
                bg_color = variables.color_scheme['dmgd_sec'][0]
                fg_color = variables.color_scheme['dmgd_sec'][1]
            else:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
    elif "Heal" in line_dict['effect']:
        string += "Heal    " + line_dict['amount'].replace("\n", "")
        if line_dict['source'] == active_id:
            bg_color = variables.color_scheme['selfheal'][0]
            fg_color = variables.color_scheme['selfheal'][1]
        else:
            bg_color = variables.color_scheme['healing'][0]
            fg_color = variables.color_scheme['healing'][1]
    elif "AbilityActivate" in line_dict['effect']:
        string += "AbilityActivate"
        if variables.settings_obj.event_colors == "advanced":
            for engine in abilities.engines:
                if engine in string:
                    bg_color = variables.color_scheme['engine'][0]
                    fg_color = variables.color_scheme['engine'][1]
                    break
            for shield in abilities.shields:
                if shield in string:
                    bg_color = variables.color_scheme['shield'][0]
                    fg_color = variables.color_scheme['shield'][1]
                    break
            for system in abilities.systems:
                if system in string:
                    bg_color = variables.color_scheme['system'][0]
                    fg_color = variables.color_scheme['system'][1]
                    break
            if not bg_color:
                bg_color = variables.color_scheme['other'][0]
                fg_color = variables.color_scheme['other'][1]
        elif variables.settings_obj.event_colors == "basic":
            bg_color = variables.color_scheme['other'][0]
            fg_color = variables.color_scheme['other'][1]
    else:
        return
    if not bg_color:
        bg_color = variables.color_scheme['default'][0]
        fg_color = variables.color_scheme['default'][1]
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
        line_dict_new = realtime.line_to_dictionary(line_dict)
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
        print "[DEBUG] An unknown error occurred while doing the delta thing"
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
            if variables.settings_obj.event_colors == "basic":
                if line_dict['source'] in player:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    bg_color = variables.color_scheme['dmgt_pri'][0]
                    fg_color = variables.color_scheme['dmgt_pri'][1]
            else:
                if line_dict['source'] in player:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    if ability in abilities.primaries:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        bg_color = variables.color_scheme['dmgt_sec'][0]
                        fg_color = variables.color_scheme['dmgt_sec'][1]
                    else:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
        else:
            if ability in abilities.primaries:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
            elif ability in abilities.secondaries:
                bg_color = variables.color_scheme['dmgd_sec'][0]
                fg_color = variables.color_scheme['dmgd_sec'][1]
            else:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
    elif "Heal" in line_dict['effect']:
        string += "Heal    " + line_dict['amount'].replace("\n", "")
        if line_dict['source'] in player:
            bg_color = variables.color_scheme['selfheal'][0]
            fg_color = variables.color_scheme['selfheal'][1]
        else:
            bg_color = variables.color_scheme['healing'][0]
            fg_color = variables.color_scheme['healing'][1]
    elif "AbilityActivate" in line_dict['effect']:
        string += "AbilityActivate"
        if variables.settings_obj.event_colors == "advanced":
            for engine in abilities.engines:
                if engine in string:
                    bg_color = variables.color_scheme['engine'][0]
                    fg_color = variables.color_scheme['engine'][1]
                    break
            for shield in abilities.shields:
                if shield in string:
                    bg_color = variables.color_scheme['shield'][0]
                    fg_color = variables.color_scheme['shield'][1]
                    break
            for system in abilities.systems:
                if system in string:
                    bg_color = variables.color_scheme['system'][0]
                    fg_color = variables.color_scheme['system'][1]
                    break
            if not bg_color:
                bg_color = variables.color_scheme['other'][0]
                fg_color = variables.color_scheme['other'][1]
        elif variables.settings_obj.event_colors == "basic":
            bg_color = variables.color_scheme['other'][0]
            fg_color = variables.color_scheme['other'][1]
    else:
        return
    if not bg_color:
        bg_color = variables.color_scheme['default'][0]
        fg_color = variables.color_scheme['default'][1]
    return string, bg_color, fg_color
