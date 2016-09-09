# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import re
import os
from datetime import datetime
from decimal import Decimal

# Function that splits the lines it gets into new lists of lines according
# to the matches and returns the timings of these matches along with them
def splitter(lines):
    # No match has yet started
    matchStarted = False
    # The matchNumber starts at 0. 0 is the first match.
    matchNumber = 0
    matches = []
    match = []
    timings = []
    # Loop through the lines supplied to identify the matches and split them.
    for line in lines:
        elements = re.split(r"[\[\]]", line)
        timestring = elements[1]
        # If @ is not in the line, it is a GSF ability
        if "@" not in line:
            # If a match had not started, then it has now started
            if matchStarted == False:
                matchStarted = True
                added = False
                timings.append(timestring)
                match.append(line)
            elif matchStarted == True:
                match.append(line)
                added = False
            else:
                raise ValueError("matchStarted is neither True nor False")
        # If @ is in the line, then it is a normal ability
        elif "@" in line:
            # If a match had started, then the match has now ended and the next
            # lines must be appended to the second match list.
            if matchStarted == True:
                matchStarted = False
                matches.append(match)
                timings.append(timestring)
                match = []
        # If @ is neither in the line nor not in the line, then an error has occurred
        else:
            raise ValueError("@ not in line and @ not not in line")
    # Return the list of lists of matches
    return matches, timings


# Function that reads the file supplied by the user and parses them accordingly
def parseMatches(matches, timings, player):
    # Declare the values that are needed for parsing
    playersOccurrences = []
    abilitiesOccurrences = []
    copilotCooldown = 60
    damageTaken = [0 for match in matches]
    damageDealt = [0 for match in matches]
    selfdamage = [0 for match in matches]
    healingReceived = [0 for match in matches]
    abilities = {}
    enemyMatrix = []
    enemies = []
    enemyDamageDealt = {}
    enemyDamageTaken = {}
    criticalLuck = []
    criticals, hits = 0, 0

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

    # Create a list of datetime variables from the timings list returned by the splitter()
    datetimes = []
    for time in timings:
        # The last part of each item of the list contains .xxx, with the x's meaning
        # thousands of a second. These can not be stored in datetime variables.
        time = time[:-4]
        datetimes.append(datetime.strptime(time, '%H:%M:%S'))

    # Here parsing starts, loop through the matches. Individual matchDamage must be possible by using more lists.
    # For now, all matches in a file are parsed.
    currentMatch = 0

    # Start looping through the matches to be able to return separate results for each match
    # matches is a matrix, match becomes a list
    for match in matches:
        # match is a list, event becomes a string
        for event in match:
            # Split the event string into smaller strings containing the information we want.
            elements = re.split(r"[\[\]]", event)
            # Assign those elements to individual variables to keep things clear.
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


            # Put the ability in the dictionary if it was used by the player and is not in it.
            # Otherwise, add one to the abilities count.
            # The abilities count is not accurate, because different abilities have periodic
            # effects and appear multiple times after activation.
            # Ion Railgun effect Reactor Disruption is activated by the player
            if source in player:
                
                if "Ion Railgun" in ability:
                    if source != target:
                        if ability not in abilities:
                            abilities[ability] = 1
                        else:
                            abilities[ability] += 1
                else:
                    if ability not in abilities:
                        abilities[ability] = 1
                    else:
                        abilities[ability] += 1

            # If Damage is in the effect string, damage was dealt
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

                # If the source is in the player list, which contains all the player's ID numbers, the damage is
                # inflicted BY the player
                if source in player:
                    # If "*" is in the damgegestring, then the hit was a critical hit
                    if '*' in damagestring:
                        criticals += 1
                    # Remove the "*" from the damagestring, as it has no use anymore and will generate an error
                    # when using int() and then add the damage to the total
                    damageDealt[currentMatch] += int(damagestring.replace('*', ''))
                    hits += 1
                    # If the target was not yet in the enemies list, and the target is not in the player list,
                    # which would mean the damage is selfdamage, then add the target to the list
                    if(target not in enemies and target not in player):
                        enemies.append(target)
                    # The same goes here, but here the damage is also assigned to the enemy in the dictionary
                    if(target not in enemyDamageTaken and target not in player):
                        enemyDamageTaken[target] = int(damagestring.replace('*', ''))
                    # If the target was already in the dictionary, then it should still be added,
                    # and the damage must be added to its total, but again only if the ID number was not in
                    # the player list
                    else:
                        if target not in player:
                            enemyDamageTaken[target] += int(damagestring.replace('*', ''))
                    # If the target was not yet in the damage dealt dictionary, then it should be added anyway,
                    # so as not to produce errors when looping through it for display.
                    if(target not in enemyDamageDealt and target not in player):
                        enemyDamageDealt[target] = 0
                # If this is not the case, the damage is inflicted to the player
                else:
                    # The damage must be added to the total of damage taken during the match
                    damageTaken[currentMatch] += int(damagestring.replace('*', ''))
                    # If the source of the damage was not yet in enemies, then the ID number must be added
                    # to the list. No checking for whether the ID is an ID in the player list is necessary,
                    # because it can't be selfdamage because the else statement concludes that source is not
                    # in the player list anyway.
                    if source not in enemies:
                        enemies.append(source)
                    # If the source ID was not yet in enemyDamageDealt, it must be added with the damage
                    if source not in enemyDamageDealt:
                        enemyDamageDealt[source] = int(damagestring.replace('*', ''))
                    # If it was, then the damage must be added to the total
                    else:
                        enemyDamageDealt[source] += int(damagestring.replace('*', ''))
                    # If the source ID was not yet in enemyDamageTaken, then it must be added to prevent anyway
                    # errors while looping through the variables when displaying the results.
                    if source not in enemyDamageTaken:
                        enemyDamageTaken[source] = 0
            # If Heal is in the event, then the player is healed for a certain amount. This number is plainly between
            # brackets: (35) for Hydro Spanner
            elif "Heal" in event:
                # Turn it into an integer and add it to the total
                damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                damagestring = damagestring.split(None, 1)[0]
                healingReceived[currentMatch] += int(damagestring.replace('*', ''))
            # Selfdamage occurs when a player crashes into something, or self-destructs.
            elif "Selfdamage" in event:
                damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                damagestring = damagestring.split(None, 1)[0]
                selfdamage[currentMatch] += int(damagestring.replace('*', ''))

        # Up the index by one to get to the next match
        currentMatch += 1
        # Append the abilities-dictionary to the list of dictionaries
        abilitiesOccurrences.append(abilities)

        # Calculate the percentage of the hits that was a critical hit
        try:
            criticalPercentage = Decimal(float(criticals) / hits)
        # If hits = 0, then there is an error. If hits = 0, crits = 0 too.
        except ZeroDivisionError:
            criticalPercentage = 0

        # Round the critical percentage of to one decimal
        criticalPercentage = round(criticalPercentage * 100, 1)
        # Add both the absolute amount of criticals and the percentage to the list as a tuple
        criticalLuck.append((criticals, criticalPercentage))
        # Make the abilities-dictionary empty
        abilities = {}
        # Clear the criticals and the thits
        criticals, hits = 0, 0
        # Add the enemies list to the enemies matrix
        enemyMatrix.append(enemies)
        # And then clear the list of enemies
        enemies = []

        # The enemyDamageDealt and enemyDamageTaken dictionaries contain all the ID numbers of all the CombatLog,
        # instead of having them in separate dictionaries contained in a list. This is because the player ID
        # numbers are at least unique within a CombatLog.

    # Return the values calculated
    return damageDealt, damageTaken, healingReceived, selfdamage, abilitiesOccurrences, datetimes, enemyMatrix, enemyDamageDealt, enemyDamageTaken, criticalLuck


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


# This is basically the main function
if __name__ == "__main__":
    print "Welcome to the Thranta Squadron GSF CombatLog parser"
    # Ask the user for a working directory so the user does not have to enter a long filepath for every new file
    print "Please enter a working directory to continue"
    print "Format: C:\Users\...\... on Windows"
    print "Format: /home/.../... on Linux/Unix"
    print "Enter q to quit."

    # Comment out this part on Linux

    # Change the working directory to this specified the directory

    # Open an infinite loop
    while True:
        # Ask the user for a directory and try to change it
        try:
            workingDir = raw_input()
            # DEBUG: use for debugging purpose
            # workingDir = os.getcwd()  # gets the current directory
            # If "q" is entered, then quit the application
            if workingDir == "q":
                exit(0)
            else:
                os.chdir(workingDir)
        # If an error occurs while changing the directory, print the error and try again
        except OSError as e:
            print "Error changing directory"
            print e
            print "\nEnter a new directory..."
            continue
        break

    while True:
        print ""
        print "Please enter a filename to continue. The file must be a valid SWTOR CombatLog."
        print "Do not forget to include the file extension. Type q to quit."
        fileName = raw_input()
        # DEBUG: use this for debug purpose
        # fileName = 'CombatLog.txt'

        # If 'q' is entered, break the loop and quit the program
        if fileName == "q":
            break
        # If this is not the case, continue reading the file in another function
        else:
            # Open the file specified by the user.
            try:
                fileObject = open(fileName, "r")
            except IOError:
                print "File '" + fileName + "' does not exists."
                break

            if fileObject is None:
                print "File '" + fileName + "' does not exists."
                print "Null pointer exception"
            else:
                # Read the lines into a variable
                lines = fileObject.readlines()
                # Determine the player's name by passing the lines to special function
                playerName = determinePlayerName(lines)
                # Determine the player's ID numbers by passing the lines to a special function
                player = determinePlayer(lines)
                print "The name of your character is ", playerName
                # Retrieve the match and timings for those matches from splitter()
                try:
                    matches, timings = splitter(lines)
                except Exception as e:
                    print "splitter(lines) failed"
                    print e
                    break
                # Pass these variables on to parseMatches() to parse them
                try:
                    damageDealt, damageTaken, healingReceived, selfdamage,  abilitiesUsed, datetimes, enemyMatrix, enemyDamageDealt, enemyDamageTaken, amountOfCriticals = parseMatches(matches, timings, player)
                except Exception as e:
                    print "parseMatches(matches, timings) failed"
                    print e
                    break
                # Then print these variables for every match separately to give more of an overview for the user
                index = 0
                for match in matches:
                    # print index, damageDealt[index], damageTaken[index], healingReceived[index], selfdamage[index], \
                    #     amountOfCriticals[index]
                    print "In match number", index + 1, "that started at", datetimes[index * 2].time(), \
                        "you achieved the follwing statistics:"
                    print "You dealt", damageDealt[index], "damage"
                    print "You took", damageTaken[index], "damage"
                    print "You received", healingReceived[index], "healing"
                    print "You did", selfdamage[index], "damage to yourself"
                    print "You had", amountOfCriticals[index], "criticalPercentage"
                    print "You used the following abilities:\n"
                    print abilitiesUsed[index], "\n"
                    index += 1

            fileObject.close()

    # When the user wants to quit and the loop breaks, then the function continues
    print "Thank you for using the Thranta Squadron GSF CombatLog Parser"
    # Wait for the user to press enter to exit
    raw_input()
