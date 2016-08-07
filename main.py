# Written by RedFantom, WingCommander of Thranta Squadron, thrantasquadron.tk
# (c) by RedFantom, for license see LICENSE

import os
import re
from datetime import datetime

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
            # If a match had started, then the match has now ended and the next lines must be appended to the second match list.
            if matchStarted == True:
                matchStarted = False
                matches.append(match)
                timings.append(timestring)
                match = []
        # If @ is neither in the line nor not in the line, then an error has occurred
        else:
            raise ValueError("@ not in line and @ not not in line")
    # Return the list of lists of matches and print it for debugging purposes
    return matches, timings

# Function that reads the file supplied by the user and parses them accordingly
def readFile(fileName):

    # Declare the values that are needed for parsing
    playersOccurrences = {}
    abilitiesOccurences = {}
    copilotCooldown = 60
    damageReceived = 0
    damageDealt = 0
    # For all the cooldowns the maximum (default) cooldown is used. These variables are for future features.
    engineCooldowns = {'Retro Thrusters' : 20, 'Koiogran Turn' : 20, 'Snap Turn' : 20, 'Power Dive' : 15, 'Barrel Roll' : 30, 'Shield Power Converter' : 9, 'Weapon Power Converter' : 9, 'Interdiction Drive' : 60,
                       'Rotational Thrusters' : 10, 'Hyperspace Beacon' : 180}
    shieldCooldowns = {'Charged Plating' : 30, 'Overcharged Shield'  : 60, 'Shield Projector' : 30, 'Directional Shield' : 0, 'Distortion Field' : 30, 'Feedback Shield' : 30, 'Repair Drone' : 90, 'Fortress Shield' : 30}
    systemCooldowns = {'Combat Command' : 90, 'Repair Probes' : 90, 'Remote Slicing' : 60, 'Interdiction Mine' : 20, 'Concussion Mine' : 20, 'Ion Mine' : 20, 'Booster Recharge' : 60, 'Targeting Telemetry' : 45,
                       'Blaster Overcharge' : 60, 'EMP Field' : 60}
    # Open the file specified by the user.
    fileObject = open(fileName, "r")
    # Read the lines into a variable
    lines = fileObject.readlines()
    # Determine the player's name by passing the lines to special function
    playerName = determinePlayerName(lines)
    # Determine the player's ID numbers by passing the lines to a special function
    player = determinePlayer(lines)
    # Retrieve the match and timings for those matches from splitter()
    matches, timings = splitter(lines)
    # Create a list of datetime variables from the timings list returned by the splitter()
    datetimes = []
    for time in timings:
        time = time[:-4]
        datetimes.append(datetime.strptime(time, '%H:%M:%S'))
    # Specify variables for damage and healing
    damageDealt = 0
    damageTaken = 0
    healingReceived = 0
    # Here parsing starts, loop through the matches. Individual matchDamage must be possible by using more lists. For now, all matches in a file are parsed.
    for match in matches:
        for event in match:
            # Split the event string into other strings containing the information we want.
            elements = re.split(r"[\[\]]", event)
            # Assign those elements to individual variables to keep things clear.
            timestring = elements[1]
            source = elements[3]
            target = elements[5]
            ability = elements[7]
            effect = elements[9]
            damagestring = elements[10]
            # If "kinetic" is in the event, it is a line where damage is the effect of an ability
            if "kinetic" in event:
                # Remove any unwanted characters from the string
                ability = ability[:-18]
                ability.strip()
                damagestring = damagestring[2:-27]
                re.sub("[^0-9]", "", damagestring)
                # Sometimes the string is empty, even while there is "kinetic" in the line. Then 0 damage is added.
                if damagestring == "":
                    damagestring = "0"
                # Some strings have a * in them. The function is currently unknown, but for now the damage is plainly added to the total by removing the *
                # Using damagestring.replace("\*", "") does not work for some reason.
                if "*" in damagestring:
                    damagestring= damagestring[:-2]
                # Get an integer from the damagestring, which now only contains a number
                damage = int(damagestring)
                # If the source is in the player list, which contains all the player's ID numbers, the damage is inflicted BY the player
                if source in player:
                    damageDealt = damage + damageDealt
                # If this is not the case, the damage is inflicted TO the player
                else:
                    damageTaken = damage + damageTaken
            # If Heal is in the event, then the player is healed for a certain amount. This number is plainly between brackets: (35) for Hydro Spanner
            elif "Heal" in event:
                # Remove the brackets
                healstring = re.sub("[^0-9]", "", damagestring)
                # Turn it into an integer and add it to the total
                heal = int(healstring)
                healingReceived += heal
    # Print the totals on the screen for the user's convenience and debugging purposes
    print "You dealt ", damageDealt, " damage"
    print "You took ", damageTaken, " damage"
    print "You received ", healingReceived, " healing"
    print "Your playerName is ", playerName
    print "Your numbers were: ", player

def determinePlayer(lines):
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

def determinePlayerName(lines):
    # Split the first line
    elements = re.split(r"[\[\]]", lines[0])
    # elements[3] is the source. The first line contains the safe-login ability which is always a self-targeted ability
    # Remove the @ from the name
    elements[3].replace("@","")
    playerName = elements[3]
    # Return the name
    return playerName

# This is basically the main function
if __name__ == "__main__":
    print "Welcome to the Thranta Squadron GSF CombatLog parser"
    # Ask the user for a working directory so the user does not have to enter a long filepath for every new file
    print "Please enter a working directory to continue"
    print "Format: C:\Users\...\..."
    workingDir = raw_input()
    # Change the working directory to this specified the directory
    os.chdir(workingDir)
    while True:
        print ""
        print "Please enter a filename to continue. The file must be a valid SWTOR CombatLog."
        print "Do not forget to include the file extension. Type q to quit."
        fileName = raw_input()
        # If 'q' is entered, break the loop and quit the program
        if(fileName == "q"):
            break
        # If this is not the case, continue reading the file in another function
        else:
            readFile(fileName)
    # When the user wants to quit and the loop breaks, then the function continues
    print "Thank you for using the Thranta Squadron GSF CombatLog Parser"
    # Wait for the user to press enter to exit
    raw_input()