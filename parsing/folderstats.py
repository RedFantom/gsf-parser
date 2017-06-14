# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import os
import decimal
from . import abilities
from . import parse
from toplevels.splashscreens import SplashScreen
import variables


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
    for file_name in os.listdir(variables.settings_obj["parsing"]["cl_path"]):
        if file_name.endswith(".txt") and parse.check_gsf(os.path.join(variables.settings_obj["parsing"]["cl_path"], file_name)):
            file_list.append(os.path.join(variables.settings_obj["parsing"]["cl_path"], file_name))

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
    splash = SplashScreen(variables.main_window, len(file_list))
    # Start looping through the files
    files_done = 0
    for name in file_list:
        files_done += 1
        # Update the progress of the progress bar of the splash screen
        splash.update_progress(files_done)
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
                for key, value in spawn_abs.items():
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
        for key, value in enemydamaged.items():
            if key in total_enemydamaged:
                total_enemydamaged[key] += value
            else:
                total_enemydamaged[key] = value
        # And enemy damage taken...
        for key, value in enemydamaget.items():
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
    for value in total_enemydamaget.values():
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
