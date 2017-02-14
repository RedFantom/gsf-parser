# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

import re
from datetime import datetime
from decimal import Decimal
from abilities import *


# Function that splits the lines it gets into new lists of lines according
# to the matches and returns the timings of these matches along with them
def splitter(lines, playerList):
    # Create empty lists for appending
    file_cube = []
    match = []
    spawn = []
    spawn_timingsMatrix = []
    spawn_timingsList = []
    match_timingsList = []
    matchStarted = False
    currentPlayer = None
    index = 0
    # Start looping through the lines
    for line in lines:
        # Split the line into elements
        elements = re.split(r"[\[\]]", line)
        # Take the relevant information from these elements
        timestring = elements[1]
        source = elements[3]
        target = elements[5]
        # If "@" is not in source, then the ability is an in-match ability
        if ("@" not in source and "@" not in target):
            # If the match hadn't started, it has now started and the the spawn
            # must be saved. The time of the spawn and the time the match has
            # started are also saved.
            if not matchStarted:
                matchStarted = True
                # Set the currentPlayer to be either the source or the target,
                # if the player is in the list of player ID numbers
                if source in playerList:
                    currentPlayer = source
                elif target in playerList:
                    currentPlayer = target
                # Add the line to the current spawn listdir
                spawn.append(line)
                # Add the spawntime and the matchtime to the lists
                spawn_timingsList.append(timestring)
                match_timingsList.append(timestring)
            # If the match had started, then the match continues
            else:
                # If the source is in the playerlist, but the source is not the
                # same as the current player, then the player has respawned and
                # the currentPlayer must change to the new value. The current
                # spawn list must be appended to the match matrix and emptied to
                # hold a new spawn.
                if source in playerList:
                    # If currentPlayer != source, the player has respawned
                    if currentPlayer != source:
                        # Add the spawn list to the match matrix
                        match.append(spawn)
                        # Empty the spawn list
                        spawn = []
                        # Add the current line to the now empty list
                        spawn.append(line)
                        # Add the time of the spawn to the list
                        spawn_timingsList.append(timestring)
                        # Set the new currentPlayer to the new ID number
                        currentPlayer = source
                    # Else, the match and spawn continue
                    else:
                        # Add the line to the list and continue
                        spawn.append(line)
                # If the target is in the playerList, but the target is not the
                # same as the current player, then the player has respawned and
                # the currentPlayer must change to the new value. The current
                # spawn list must be appended to the match matrix and emptied to
                # hold a new spawn.
                elif target in playerList:
                    # If currentPlayer != target, the player has respawned
                    if currentPlayer != target:
                        # Add the spawn list to the match matrix
                        match.append(spawn)
                        # Empty the spawn list
                        spawn = []
                        # Add the current line to the now empty list
                        spawn.append(line)
                        # Add the time of the spawn to the list
                        spawn_timingsList.append(timestring)
                        # Set the new currentPlayer to the new ID number
                        currentPlayer = target
                    # Else, the match and spawn continue
                    else:
                        # Add the line to the list and continue
                        spawn.append(line)
        # "@" is in the line, then it is a normal ability
        else:
            # If the previous line was a match-line and the next line is a match line,
            # The match continues and the line gets skipped altogether
            try:
                if (not "@" in re.split(r"[\[\]]", lines[index - 1])[3] and
                        not "@" in re.split(r"[\[\]]", lines[index + 1])[3] and
                        not "Safe Login" in re.split(r"[\[\]]", line)[7]):
                    continue
            except IndexError:
                continue
            # If a match had started, then now it has ended
            if matchStarted:
                # End of the match
                matchStarted = False
                match.append(spawn)
                # Add the match matrix to the file_cube
                file_cube.append(match)
                # Add the endtime of the match to the list
                match_timingsList.append(timestring)
                # Add the spawn_timingsList to the matrix with [match][spawn]
                spawn_timingsMatrix.append(spawn_timingsList)
                # Clear the lists
                spawn_timingsList = []
                spawn = []
                match = []
                # Clear the currentPlayer
                currentPlayer = None
        index += 1
    if matchStarted == True:
        # End of the file
        matchStarted = False
        match.append(spawn)
        # Add the match matrix to the file_cube
        file_cube.append(match)
        # Add the endtime of the match to the list
        match_timingsList.append(timestring)
        # Add the spawn_timingsList to the matrix with [match][spawn]
        spawn_timingsMatrix.append(spawn_timingsList)
        # Clear the lists
        spawn_timingsList = []
        spawn = []
        match = []
        # Clear the currentPlayer
        currentPlayer = None
    match_timings = []
    spawn_timings = []
    spawn_timingstemp = []
    # Create a list of datetime variables from the timings list returned by the splitter()
    for time in match_timingsList:
        # The last part of each item of the list contains .xxx, with the x's meaning
        # thousands of a second. These can not be stored in datetime variables.
        time = time[:-4]
        match_timings.append(datetime.strptime(time, '%H:%M:%S'))
    for list in spawn_timingsMatrix:
        for time in list:
            time = time[:-4]
            spawn_timingstemp.append(datetime.strptime(time, '%H:%M:%S'))
        spawn_timings.append(spawn_timingstemp)
        spawn_timingstemp = []

    # Return a 3D-matrix/cube of the lines of the file_cube with [match][spawn][line]
    # and a timingslist for the matches and a timings matrix for the spawns with
    # [match][spawn]. For the spawns, only the start times are recorded.
    return file_cube, match_timings, spawn_timings


def parse_spawn(spawn, player):
    abilities = {}
    damagetaken = 0
    damagedealt = 0
    healingreceived = 0
    selfdamage = 0
    enemies = []
    criticalcount = 0
    criticalluck = 0.0000
    hitcount = 0

    enemydamaget = {}
    enemydamaged = {}
    line = 0
    for event in spawn:
        # Split the event string into smaller strings containing the information we want.
        elements = re.split(r"[\[\]]", event)
        # sign those elements to individual variables to keep things clear.
        timestring = elements[1]
        source = elements[3]
        target = elements[5]
        ability = elements[7]
        effect = elements[9]
        damagestring = elements[10]
        # The ability always has an ID number behind it between {}, it must be removed
        # This ID number is for recognition between languages. The ID number is always the same,
        # even where the ability name is not. Only English is supported at this time.
        ability = ability.split(' {', 1)[0]

        if source == "":
            source = ability

        if source in player:
            if "AbilityActivate" in effect:
                if "Hull Cutter" in ability:
                    if source != target:
                        if ability not in abilities:
                            abilities[ability] = 1
                        else:
                            abilities[ability] += 1
                elif ability != "" and "Ion Railgun" not in ability:
                    if ability not in abilities:
                        abilities[ability] = 1
                    else:
                        abilities[ability] += 1
            if "Damage" in effect and "Ion Railgun" in ability and line > 0 and "AbilityActivate" in spawn[
                        line - 1] and "Ion Railgun" in spawn[line - 1]:
                if source != target:
                    if ability not in abilities:
                        abilities[ability] = 1
                    else:
                        abilities[ability] += 1

        if "kinetic" in event:
            # Takes damagestring and split after the pattern (stuff in here) and take the second element
            # containing the "stuff in here"
            # example: (436 kinetic {836045448940873}) => ['', '436 kinetic {836045448940873}', '']
            damagestring = re.split(r"\((.*?)\)", damagestring)[1]
            # now split it and take only the number
            damagestring = damagestring.split(None, 1)[0]
            # Sometimes the string is empty, even while there is "Damage" in the line. Then 0 damage is added.
            if damagestring == "":
                damagestring = "0"
            if source in player:
                if "*" in damagestring:
                    criticalcount += 1
                damagedealt += int(damagestring.replace("*", ""))
                hitcount += 1
                if target not in enemies and target not in player:
                    enemies.append(target)
                if target not in enemydamaget and target not in player:
                    enemydamaget[target] = int(damagestring.replace("*", ""))
                elif target in enemydamaget and target not in player:
                    enemydamaget[target] += int(damagestring.replace("*", ""))
                if target not in enemydamaged and target not in player:
                    enemydamaged[target] = 0
            else:
                damagetaken += int(damagestring.replace("*", ""))
                if source not in enemies:
                    enemies.append(source)
                if source not in enemydamaged:
                    enemydamaged[source] = int(damagestring.replace("*", ""))
                else:
                    enemydamaged[source] += int(damagestring.replace("*", ""))
                if source not in enemydamaget:
                    enemydamaget[source] = 0
        elif "Heal" in event:
            damagestring = re.split(r"\((.*?)\)", damagestring)[1]
            damagestring = damagestring.split(None, 1)[0]
            healingreceived += int(damagestring.replace("*", ""))
        elif "Selfdamage" in event:
            damagestring = re.split(r"\((.*?)\)", damagestring)[1]
            damagestring = damagestring.split(None, 1)[0]
            selfdamage += int(damagestring.replace("*", ""))
        line += 1
    ships_list = ["Legion", "Razorwire", "Decimus",
                  "Mangler", "Dustmaker", "Jurgoran",
                  "Bloodmark", "Blackbolt", "Sting",
                  "Imperium", "Quell", "Rycer"]
    amount_secondaries = 0
    for key in abilities:
        if key.strip() not in excluded_abilities:
            if key.strip() in secondaries:
                amount_secondaries += 1
            if "Legion" in ships_list:
                if key.strip() not in legionAbilities:
                    print "[DEBUG] Legion removed for: ", key.strip()
                    ships_list.remove("Legion")
            if "Razorwire" in ships_list:
                if key.strip() not in razorwireAbilities:
                    print "[DEBUG] Razorwire removed for: ", key.strip()
                    ships_list.remove("Razorwire")
            if "Decimus" in ships_list:
                if key.strip() not in decimusAbilities:
                    print "[DEBUG] Decimus removed for: ", key.strip()
                    ships_list.remove("Decimus")
            if "Mangler" in ships_list:
                if key.strip() not in manglerAbilities:
                    print "[DEBUG] Mangler removed for: ", key.strip()
                    ships_list.remove("Mangler")
            if "Jurgoran" in ships_list:
                if key.strip() not in jurgoranAbilities:
                    print "[DEBUG] Jurgoran removed for: ", key.strip()
                    ships_list.remove("Jurgoran")
            if "Dustmaker" in ships_list:
                if key.strip() not in dustmakerAbilities:
                    print "[DEBUG] Dustmaker removed for: ", key.strip()
                    ships_list.remove("Dustmaker")
            if "Bloodmark" in ships_list:
                if key.strip() not in bloodmarkAbilities:
                    print "[DEBUG] Bloodmark removed for: ", key.strip()
                    ships_list.remove("Bloodmark")
            if "Blackbolt" in ships_list:
                if key.strip() not in blackboltAbilities:
                    print "[DEBUG] Blackbolt removed for: ", key.strip()
                    ships_list.remove("Blackbolt")
            if "Sting" in ships_list:
                if key.strip() not in stingAbilities:
                    print "[DEBUG] Sting removed for: ", key.strip()
                    ships_list.remove("Sting")
            if "Imperium" in ships_list:
                if key.strip() not in imperiumAbilities:
                    print "[DEBUG] Imperium removed for: ", key.strip()
                    ships_list.remove("Imperium")
            if "Quell" in ships_list:
                if key.strip() not in quellAbilities:
                    print "[DEBUG] Quell removed for: ", key.strip()
                    ships_list.remove("Quell")
            if "Rycer" in ships_list:
                if key.strip() not in rycerAbilities:
                    print "[DEBUG] Rycer removed for: ", key.strip()
                    ships_list.remove("Rycer")
    if amount_secondaries == 2:
        for ship in ships_list:
            if ship != "Quell" and ship != "Mangler" and ship != "Dustmaker" and ship != "Jurgoran":
                ships_list.remove(ship)
    try:
        criticalluck = Decimal(float(criticalcount) / float(hitcount))
        criticalluck = round(criticalluck * 100, 2)
    except ZeroDivisionError:
        criticalluck = float(0)
    return (abilities, damagetaken, damagedealt, healingreceived, selfdamage,
            enemies, criticalcount, criticalluck, hitcount, ships_list, enemydamaged,
            enemydamaget)


def parse_file(file, player, match_timingsList, spawn_timingsMatrix):
    # Per spawn variables
    abilities_spawn = {}
    damagetaken_spawn = 0
    damagedealt_spawn = 0
    selfdamage_spawn = 0
    healingreceived_spawn = 0
    enemies_spawn = []
    criticalcount_spawn = 0
    criticalluck_spawn = 0
    hitcount_spawn = 0

    # Per match variables, enemiesMatch is a matrix
    abilities_match = []
    damagetaken_match = []
    damagedealt_match = []
    selfdamage_match = []
    healingreceived_match = []
    enemies_match = []
    criticalcount_match = []
    criticalluck_match = []
    hitcount_match = []

    # Per file variables
    abilities = []
    damagetaken = []
    damagedealt = []
    selfdamage = []
    healingreceived = []
    enemies = []
    criticalcount = []
    criticalluck = []
    hitcount = []

    # File-wide dictionaries
    enemydamaged = {}
    enemydamaget = {}

    match_timings = []
    spawn_timings = []
    spawn_timingstemp = []

    # For all the cooldowns the maximum (default) cooldown is used. These variables are for future features.
    engine_cooldowns = {'Retro Thrusters': 20, 'Koiogran Turn': 20, 'Snap Turn': 20, 'Power Dive': 15,
                        'Barrel Roll': 30, 'Shield Power Converter': 9, 'Weapon Power Converter': 9,
                        'Interdiction Drive': 60, 'Rotational Thrusters': 10, 'Hyperspace Beacon': 180}
    shield_cooldowns = {'Charged Plating': 30, 'Overcharged Shield': 60, 'Shield Projector': 30,
                        'Directional Shield': 0, 'Distortion Field': 30, 'Feedback Shield': 30, 'Repair Drone': 90,
                        'Fortress Shield': 30}
    system_cooldowns = {'Combat Command': 90, 'Repair Probes': 90, 'Remote Slicing': 60, 'Interdiction Mine': 20,
                        'Concussion Mine': 20, 'Ion Mine': 20, 'Booster Recharge': 60, 'Targeting Telemetry': 45,
                        'Blaster Overcharge': 60, 'EMP Field': 60}

    for match in file:
        for spawn in match:
            for event in spawn:
                # Split the event string into smaller strings containing the information we want.
                elements = re.split(r"[\[\]]", event)
                # sign those elements to individual variables to keep things clear.
                timestring = elements[1]
                source = elements[3]
                target = elements[5]
                ability = elements[7]
                effect = elements[9]
                damagestring = elements[10]

                # The ability always has an ID number behind it between {}, it must be removed
                # This ID number is for recognition between languages. The ID number is always the same,
                # even where the ability name is not. Only English is supported at this time.
                ability = ability.split(' {', 1)[0]

                if source == "":
                    source = ability

                if source in player:
                    if "Ion Railgun" in ability:
                        if source != target:
                            if ability not in abilities_spawn:
                                abilities_spawn[ability] = 1
                            else:
                                abilities_spawn[ability] += 1
                    elif "Hull Cutter" in ability:
                        if source != target:
                            if ability not in abilities_spawn:
                                abilities_spawn[ability] = 1
                            else:
                                abilities_spawn[ability] += 1
                    elif ability != "":
                        if ability not in abilities_spawn:
                            abilities_spawn[ability] = 1
                        else:
                            abilities_spawn[ability] += 1

                if "kinetic" in event:
                    # Takes damagestring and split after the pattern (stuff in here) and take the second element
                    # containing the "stuff in here"
                    # example: (436 kinetic {836045448940873}) => ['', '436 kinetic {836045448940873}', '']
                    damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                    # now split it and take only the number
                    damagestring = damagestring.split(None, 1)[0]

                    # Sometimes the string is empty, even while there is "Damage" in the line. Then 0 damage is added.
                    if damagestring == "":
                        damagestring = "0"

                    if source in player:
                        if "*" in damagestring:
                            criticalcount_spawn += 1
                        damagedealt_spawn += int(damagestring.replace("*", ""))
                        hitcount_spawn += 1

                        if target not in enemies and target not in player:
                            enemies_spawn.append(target)
                        if target not in enemydamaget and target not in player:
                            enemydamaget[target] = int(damagestring.replace("*", ""))
                        elif target in enemydamaget and target not in player:
                            enemydamaget[target] += int(damagestring.replace("*", ""))
                        if target not in enemydamaged and target not in player:
                            enemydamaged[target] = 0
                    else:
                        damagetaken_spawn += int(damagestring.replace("*", ""))
                        if source not in enemies_spawn:
                            enemies_spawn.append(source)
                        if source not in enemydamaged:
                            enemydamaged[source] = int(damagestring.replace("*", ""))
                        else:
                            enemydamaged[source] += int(damagestring.replace("*", ""))
                        if source not in enemydamaget:
                            enemydamaget[source] = 0
                elif "Heal" in event:
                    damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                    damagestring = damagestring.split(None, 1)[0]
                    healingreceived_spawn += int(damagestring.replace("*", ""))
                elif "Selfdamage" in event:
                    damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                    damagestring = damagestring.split(None, 1)[0]
                    selfdamage_spawn += int(damagestring.replace("*", ""))

            try:
                criticalluck_spawn = Decimal(float(criticalcount_spawn / hitcount_spawn))
            except ZeroDivisionError:
                criticalluck_spawn = 0
            criticalluck_spawn = round(criticalluck_spawn * 100, 1)

            abilities_match.append(abilities_spawn)
            damagetaken_match.append(damagetaken_spawn)
            damagedealt_match.append(damagedealt_spawn)
            selfdamage_match.append(selfdamage_spawn)
            healingreceived_match.append(healingreceived_spawn)
            enemies_match.append(enemies_spawn)
            criticalcount_match.append(criticalcount_spawn)
            criticalluck_match.append(criticalluck_spawn)
            hitcount_match.append(hitcount_spawn)

            abilities_spawn = {}
            damagetaken_spawn = 0
            damagedealt_spawn = 0
            selfdamage_spawn = 0
            healingreceived_spawn = 0
            enemies_spawn = []
            criticalcount_spawn = 0
            criticalluck_spawn = 0
            hitcount_spawn = 0

        abilities.append(abilities_match)
        damagetaken.append(damagetaken_match)
        damagedealt.append(damagedealt_match)
        selfdamage.append(selfdamage_match)
        healingreceived.append(healingreceived_match)
        enemies.append(enemies_match)
        criticalcount.append(criticalcount_match)
        criticalluck.append(criticalluck_match)
        hitcount.append(hitcount_match)
        abilities_match = []

        damagetaken_match = []
        damagedealt_match = []
        selfdamage_match = []
        healingreceived_match = []
        enemies_match = []
        criticalcount_match = []
        criticalluck_match = []
        hitcount_match = []

    # abilities is a matrix of dictionaries
    # damagetaken is a matrix of numbers
    # damagedealt is a matrix of numbers
    # selfdamage is a matrix of numbers
    # healingreceived is a matrix of numbers
    # enemies is a cube of strings
    # criticalcount is matrix of numbers
    # criticalluck is a matrix of numbers
    # hitcount is matrix of numbers
    # enemydamaged is a dictionary
    # enemydamaget is a dictionary
    # match_timings is a list of datetimes
    # spawn_timings is a matrix of datetimes
    return (abilities, damagetaken, damagedealt, selfdamage, healingreceived, enemies,
            criticalcount, criticalluck, hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings)


def abilityUsage(abilitiesOccurrences, match_timingsList, spawn_timingsMatrix):
    # For all the cooldowns the maximum (default) cooldown is used. These variables are for future features.
    engineCooldowns = {'Retro Thrusters': 20, 'Koiogran Turn': 20, 'Snap Turn': 20, 'Power Dive': 15,
                       'Barrel Roll': 30, 'Shield Power Converter': 9, 'Weapon Power Converter': 9,
                       'Interdiction Drive': 60, 'Rotational Thrusters': 10, 'Hyperspace Beacon': 180}
    shieldCooldowns = {'Charged Plating': 30, 'Overcharged Shield': 60, 'Shield Projector': 30,
                       'Directional Shield': 0, 'Distortion Field': 30, 'Feedback Shield': 30, 'Repair Drone': 90,
                       'Fortress Shield': 30}
    systemCooldowns = {'Combat Command': 90, 'Repair Probes': 90, 'Remote Slicing': 60, 'Interdiction Mine': 20,
                       'Concussion Mine': 20, 'Ion Mine': 20, 'Booster Recharge': 60, 'Targeting Telemetry': 45,
                       'Blaster Overcharge': 60, 'EMP Field': 60}
    print "Ability usage: "
    # return a dictionary with abilities and percentage of the possible usage


# Function to determine the ship of the player with a dictionary from the
# abilitiesOccurrencesMatrix from parseFile()
def determineShip(abilitiesDictionary):
    shipsList = ["Legion", "Razorwire", "Decimus",
                 "Mangler", "Dustmaker", "Jurgoran",
                 "Bloodmark", "Blackbolt", "Sting",
                 "Imperium", "Quell", "Rycer"]
    for key in abilitiesDictionary:
        if key.strip() not in excluded_abilities:
            if "Legion" in shipsList:
                if key.strip() not in legionAbilities:
                    shipsList.remove("Legion")
            if "Razorwire" in shipsList:
                if key.strip() not in razorwireAbilities:
                    shipsList.remove("Razorwire")
            if "Decimus" in shipsList:
                if key.strip() not in decimusAbilities:
                    shipsList.remove("Decimus")
            if "Mangler" in shipsList:
                if key.strip() not in manglerAbilities:
                    shipsList.remove("Mangler")
            if "Jurgoran" in shipsList:
                if key.strip() not in jurgoranAbilities:
                    shipsList.remove("Jurgoran")
            if "Dustmaker" in shipsList:
                if key.strip() not in dustmakerAbilities:
                    shipsList.remove("Dustmaker")
            if "Bloodmark" in shipsList:
                if key.strip() not in bloodmarkAbilities:
                    shipsList.remove("Bloodmark")
            if "Blackbolt" in shipsList:
                if key.strip() not in blackboltAbilities:
                    shipsList.remove("Blackbolt")
            if "Sting" in shipsList:
                if key.strip() not in stingAbilities:
                    shipsList.remove("Sting")
            if "Imperium" in shipsList:
                if key.strip() not in imperiumAbilities:
                    shipsList.remove("Imperium")
            if "Quell" in shipsList:
                if key.strip() not in quellAbilities:
                    shipsList.remove("Quell")
            if "Rycer" in shipsList:
                if key.strip() not in rycerAbilities:
                    shipsList.remove("Rycer")

    return shipsList


# Returns the player's ID numbers
def determinePlayer(lines):
    """
    Takes a list of strings (lines of a combat log) and extract all player engaged into battle. Save those in a
    dictionary with player ID as key and its occurrence as value.

    :param lines: lines of a combat log, as a list of string
    :return: dictionary of player ID and its occurrence
    """
    # Create dictionary to store the players in
    playerOccurrences = {}
    # Start a for loop to loop through the lines
    for action in lines:
        # Split the elements, just as in ReadFile()
        elements = re.split(r"[\[\]]", action)
        # Only source and target are important here
        source = elements[3]
        target = elements[5]
        # If the target is also the source, then it's a self-targeted ability
        if target == source:
            # Only if @ is not in the source it is a GSF ability
            if "@" not in source:
                # If the ID is not yet in the dictionary, add it and set the amount of occurrences to 1
                if source not in playerOccurrences:
                    playerOccurrences[source] = 1
                # If the ID is already in the dictionary, add 1 to the amount of occurrences for this ID
                else:
                    playerOccurrences[source] += 1
    # Return the playerOccurrences dictionary with the ID's and their respective occurrences
    return playerOccurrences


# TODO: make ready for file_cube
def determineDeaths(matches):
    playerIDs = []
    deaths = []
    for match in matches:
        for event in match:
            elements = re.split(r"[\[\]]", event)
            source = elements[3]
            target = elements[5]
            if target == source:
                if "@" not in source:
                    if source not in playerIDs:
                        playerIDs.append(source)
        tempDeaths = len(playerIDs) - 1
        playerIDs = []
        deaths.append(tempDeaths)
        tempDeaths = []
    return deaths


# Returns the player name
def determinePlayerName(lines):
    """
    Takes the first line of the combat log, which always contains the safe-login ability, which is a self-targeted
    ability. The 4th element of the line is the player name with the form: '@Name'. Return the name without '@'

    :param lines: List of strings, each elements are a line of the combat log
    :return: Player name, string
    """
    # In an unmodified file, lines[0] will always have this format
    for line in lines:
        elements = re.split(r"[\[\]]", line)  # Split line
        if elements[3] == elements[5]:
            return elements[3][1:]
        else:
            continue


# Debugging purposes
if __name__ == "__main__":

    with open("CombatLog.txt", "r") as fileObject:
        lines = fileObject.readlines()
    player = determinePlayer(lines)
    file, match_timingsList, spawn_timingsMatrix = splitter(lines, player)
    (abilities, damagetaken, damagedealt, selfdamage, healingreceived, enemies,
     criticalcount, criticalluck, hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings) = parse_file(file,
                                                                                                                   player,
                                                                                                                   match_timingsList,
                                                                                                                   spawn_timingsMatrix)
    for list in abilities:
        for dict in list:
            print determineShip(dict)
