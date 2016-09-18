# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import re
import os
import vars
from datetime import datetime
from decimal import Decimal

# Function that splits the lines it gets into new lists of lines according
# to the matches and returns the timings of these matches along with them
def splitter(lines, playerList):
    # Create empty lists for appending
    file = []
    match = []
    spawn = []
    spawn_timingsMatrix = []
    spawn_timingsList = []
    match_timingsList = []
    matchStarted = False
    currentPlayer = None
    # Start looping through the lines
    for line in lines:
        # Split the line into elements
        elements = re.split(r"[\[\]]", line)
        # Take the relevant information from these elements
        timestring = elements[1]
        source = elements[3]
        target = elements[5]
        # If "@" is not in source, then the ability is an in-match ability
        if "@" not in source:
            # If the match hadn't started, it has now started and the the spawn
            # must be saved. The time of the spawn and the time the match has
            # started are also saved.
            if matchStarted == False:
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
            # If a match had started, then now it has ended
            if matchStarted == True:
                # End of the match
                matchStarted = False
                # Add the match matrix to the file Cube
                file.append(match)
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

    # Return a 3D-matrix/cube of the lines of the file with [match][spawn][line]
    # and a timingslist for the matches and a timings matrix for the spawns with
    # [match][spawn]. For the spawns, only the start times are recorded.
    return file, match_timingsList, spawn_timingsMatrix

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

                        if(target not in enemies and target not in player):
                            enemies_spawn.append(target)
                        if(target not in enemydamaget and target not in player):
                            enemydamaget[target] = int(damagestring.replace("*", ""))
                        elif(target in enemydamaget and target not in player):
                            enemydamaget[target] += int(damagestring.replace("*", ""))
                        if(target not in enemydamaged and target not in player):
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
    # These lists were made with the help of Yellowbird
    legionAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                       "Proton Torpedoe", "Concussion Missile", "Seeker Mine",
                       "Shield Power Converter", "Interdiction Drive",
                       "Railgun Sentry Drone", "Interdiction Sentry Drone", "Missile Sentry Drone",
                       "Shield Projector", "Repair Drone", "Overcharged Shield"]
    razorwireAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                          "Seismic Mine", "Proton Torpedoe", "Seeker Mine",
                          "Shield Power Converter", "Interdiction Drive", "Hyperspace Beacon",
                          "Interdiction Mine", "Concussion Mine", "Ion Mine",
                          "Charged Plating", "Overcharged Shield", "Shield Projector"]
    decimusAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon",
                        "Cluster Missiles", "Concussion Missile", "Proton Torpedoe"
                        "Shield Power Converter", "Power Dive", "Interdiction Drive",
                        "Ion Mine", "Concussion Mine", "Interdiction Sentry Drone"]
    jurgoranAbilities = ["Burst Laser Cannon", "Light Laser Cannon", "Laser Cannon",
                         "Cluster Missiles", "Slug Railgun", "Interdiction Missile", "EMP Missile"
                         "Koiogran Turn", "Retro Thrusters", "Power Dive", "Interdiction Drive",
                         "Directional Shield", "Feedback Shield", "Distortion Field", "Fortress Shield"]
    dustmakerAbilities = ["Laser Cannon", "Heavy Laser Cannon",
                          "Proton Torpedoe", "Thermite Torpedoe", "Plasma Railgun", "Slug Railgun",
                          "Weapon Power Converter", "Rotational Thrusters", "Interdiction Drive", "Barrel Roll",
                          "Fortress Shield", "Directional Shield", "Feedback Shield"]
    manglerAbilities = ["Light Laser Cannon", "Burst Laser Cannon",
                        "Plasma Railgun", "Slug Railgun", "Ion Railgun",
                        "Rotational Thrusters", "Barrel Roll", "Interdiction Drive", "Weapon Power Converter",
                        "Feedback Shield", "Fortress Shield", "Distortion Field"]
    bloodmarkAbilities = ["Light Laser Cannon", "Laser Cannon", "Rapid-fire Laser Cannon",
                          "Ion Missile", "EMP Missile", "Thermite Torpedoe",
                          "Snap Turn", "Power Dive", "Interdiction Drive", "Koiogran Turn"
                          "Combat Command", "Tensor Field", "Sensor Beacon", "Targeting Telemetry",
                          "Shield Projector", "Repair Drone", "Distortion Field"]
    blackboltAbilities = ["Rapid-fire Laser Cannon", "Light Laser Cannon", "Laser Cannon",
                          "Rocket Pod", "Thermite Torpedoe", "Sabotage Probe",
                          "Power Dive", "Snap Turn", "Barrel Roll", "Koiogran Turn",
                          "Targeting Telemetry", "EMP Field", "Booster Recharge", "Sensor Beacon",
                          "Distortion Field", "Quick-charge Shield", "Engine Power Converter"]
    stingAbilities = ["Burst Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon", "Rapid-fire Laser Cannon",
                      "Rocket Pod", "Cluster Missiles", "Sabotage Probe"
                      "Koiogran Turn", "Retro Thrusters", "Power Dive", "Barrel Roll",
                      "Targeting Telemetry", "Blaster Overcharge", "Booster Recharge",
                      "Distortion Field", "Quick-charge Shield", "Directional Shield"]
    imperiumAbilities = ["Quad Laser Cannon", "Rapid-fire Laser Cannon", "Light Laser Cannon",
                         "Thermite Torpedoe", "EMP Missile", "Proton Torpedoe", "Ion Missile",
                         "Koiogran Turn", "Shield Power Converter", "Power Dive", "Interdiction Drive",
                         "Combat Command", "Remote Slicing", "Repair Probes",\
                         "Charged Plating", "Directional Shield", "Shield Projector"]
    rycerAbilities = ["Quad Laser Cannon", "Ion Cannon", "Rapid-fire Laser Cannon", "Heavy Laser Cannon", "Laser Cannon",
                      "Concussion Missile", "Cluster Missiles", "Proton Torpedoe",
                      "Weapon Power Converter", "Retro Thrusters", "Barrel Roll", "Koiogran Turn",
                      "Charged Plating", "Quick-charge Shield", "Directional Shield"]
    quellAbilities = ["Heavy Laser Cannon", "Quad Laser Cannon", "Light Laser Cannon",
                      "Cluster Missiles", "Ion Missile", "Proton Torpedoe", "Concussion Missile", "EMP Missile",
                      "Weapon Power Converter", "Shield Power Converter", "Koiogran Turn", "Barrel Roll",
                      "Quick-charge Shield", "Directional Shield", "Charged Plating"]
    shipsList = ["Legion", "Razorwire", "Decimus",
                 "Mangler", "Dustmaker", "Jurgoran",
                 "Bloodmark", "Blackbolt", "Sting",
                 "Imperium", "Quell", "Rycer"]
    excluded_abilities = ["Wingman", "Hydro Spanner", "In Your Sights", "Slicer's Loop",
                         "Servo Jammer", "Lockdown", "Concentrated Fire", "Lingering Effect",
                         "Bypass", "Running Interference", "Suppression", "Nullify", "Hull Cutter",
                         "Selfdamage", "Secondary Weapon Swap", "Primary Weapon Swap", "Sabotage Probe"]

    for key in abilitiesDictionary:
        if key not in excluded_abilities:
            if "Legion" in shipsList:
                if key not in legionAbilities:
                    shipsList.remove("Legion")
            if "Razorwire" in shipsList:
                if key not in razorwireAbilities:
                    shipsList.remove("Razorwire")
            if "Decimus" in shipsList:
                if key not in decimusAbilities:
                    shipsList.remove("Decimus")
            if "Mangler" in shipsList:
                if key not in manglerAbilities:
                    shipsList.remove("Mangler")
            if "Jurgoran" in shipsList:
                if key not in jurgoranAbilities:
                    shipsList.remove("Jurgoran")
            if "Dustmaker" in shipsList:
                if key not in dustmakerAbilities:
                    shipsList.remove("Dustmaker")
            if "Bloodmark" in shipsList:
                if key not in bloodmarkAbilities:
                    shipsList.remove("Bloodmark")
            if "Blackbolt" in shipsList:
                if key not in blackboltAbilities:
                    shipsList.remove("Blackbolt")
            if "Sting" in shipsList:
                if key not in stingAbilities:
                    shipsList.remove("Sting")
            if "Imperium" in shipsList:
                if key not in imperiumAbilities:
                    shipsList.remove("Imperium")
            if "Quell" in shipsList:
                if key not in quellAbilities:
                    shipsList.remove("Quell")
            if "Rycer" in shipsList:
                if key not in rycerAbilities:
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
    elements = re.split(r"[\[\]]", lines[0])  # Split line
    return elements[3][1:]

# Debugging purposes
if __name__ == "__main__":

    fileObject = open("CombatLog.txt", "r")
    lines = fileObject.readlines()
    player = determinePlayer(lines)
    file, match_timingsList, spawn_timingsMatrix = splitter(lines, player)
    (abilities, damagetaken, damagedealt, selfdamage, healingreceived, enemies,
    criticalcount, criticalluck, hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings) = parse_file(file, player, match_timingsList, spawn_timingsMatrix)
        
    for list in abilities:
        for dict in list:
            print determineShip(dict)