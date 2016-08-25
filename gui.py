# Written by RedFantom, Wing Commander of Thranta Squadron, thrantasquadron.tk
# Contributed to by Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import Tkinter
import tkMessageBox
import tkFileDialog
import re
import vars
from datetime import datetime


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
            # If a match had started, then the match has now ended and the next lines must be appended to the second
            # match list.
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
    healingReceived = [0 for match in matches]
    abilities = {}

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
        time = time[:-4]
        datetimes.append(datetime.strptime(time, '%H:%M:%S'))

    # Here parsing starts, loop through the matches. Individual matchDamage must be possible by using more lists.
    # For now, all matches in a file are parsed.
    currentMatch = 0

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

            # The ability always has an ID number behind it between {}, it must be removed
            ability = ability[:-18]
            ability.strip()
            # Put the ability in the dictionary
            if ability not in abilities:
                abilities[ability] = 1
            else:
                abilities[ability] += 1
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
                # Get an integer from the damagestring, which now only contains a number
                try:
                    damage = int(damagestring)
                except:
                    pass
                # If the source is in the player list, which contains all the player's ID numbers, the damage is
                # inflicted BY the player
                if source in player:
                    damageDealt[currentMatch] += damage
                # If this is not the case, the damage is inflicted TO the player
                else:
                    damageTaken[currentMatch] += damage
            # If Heal is in the event, then the player is healed for a certain amount. This number is plainly between
            # brackets: (35) for Hydro Spanner
            elif "Heal" in event:
                # Remove the brackets
                healstring = re.sub("[^0-9]", "", damagestring)
                # Turn it into an integer and add it to the total
                heal = int(healstring)
                healingReceived[currentMatch] += heal
        # Up the index by one to get to the next match
        currentMatch += 1
        # Append the abilities-dictionary to the list of dictionaries
        abilitiesOccurrences.append(abilities)
        # Make the abilities-dictionary empty
        abilities = {}
    # Return the values calculated
    return damageDealt, damageTaken, healingReceived, abilitiesOccurrences, datetimes


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
    

# Call back fuction for the Open CombatLog menu item
# Parses the file and places the results in the variables in vars.py
# Then adds a new menu cascade, of which all items call the setStatistics() function with lambda
def openCombatLog():
    # First try to delete the pervious menu cascad. Will fail if it doesn't yet exist.
    try:
        menuBar.delete("Matches")
    except:
        pass
    types = [("SWTOR CombatLog", "*.txt"), ("All files", "*")]
    openDialog = tkFileDialog.Open(filetypes = types)
    fileName = openDialog.show()
    try:
        fileObject = open(fileName, "r")
        lines = fileObject.readlines()
    except IOError:
        return
    vars.statisticsFile = False
    vars.matches, vars.timings = splitter(lines)
    vars.playerName = determinePlayerName(lines)
    vars.playerNumbers = determinePlayer(lines)
    vars.damageDealt, vars.damageTaken, vars.healingReceived, vars.abilitiesOccurrences, vars.datetimes = parseMatches(vars.matches, vars.timings, vars.playerNumbers)
    logMenu = Tkinter.Menu(menuBar, tearoff = 0)
    index = 0
    amountOfMatches = 0
    for match in vars.matches:
        if index == 0:
            logMenu.add_command(label = vars.timings[0], command = lambda : setStatistics(0))
        elif index == 1:
            logMenu.add_command(label = vars.timings[2], command = lambda : setStatistics(1))
        elif index == 2:
            logMenu.add_command(label = vars.timings[4], command = lambda : setStatistics(2))
        elif index == 3:
            logMenu.add_command(label = vars.timings[6], command = lambda : setStatistics(3))
        elif index == 4:
            logMenu.add_command(label = vars.timings[8], command = lambda : setStatistics(4))
        elif index == 5:
            logMenu.add_command(label = vars.timings[10], command = lambda : setStatistics(5))
        elif index == 6:
            logMenu.add_command(label = vars.timings[12], command = lambda : setStatistics(6))
        elif index == 7:
            logMenu.add_command(label = vars.timings[14], command = lambda : setStatistics(7))
        elif index == 8:
            logMenu.add_command(label = vars.timings[16], command = lambda : setStatistics(8))
        elif index == 9:
            logMenu.add_command(label = vars.timings[18], command = lambda : setStatistics(9))
        elif index == 10:
            logMenu.add_command(label = vars.timings[20], command = lambda : setStatistics(10))
        elif index == 11:
            logMenu.add_command(label = vars.timings[22], command = lambda : setStatistics(11))
        elif index == 12:
            logMenu.add_command(label = vars.timings[24], command = lambda : setStatistics(12))
        elif index == 13:
            logMenu.add_command(label = vars.timings[26], command = lambda : setStatistics(13))
        elif index == 14:
            logMenu.add_command(label = vars.timings[28], command = lambda : setStatistics(14))
        elif index == 15:
            logMenu.add_command(label = vars.timings[30], command = lambda : setStatistics(15))
        elif index == 16:
            logMenu.add_command(label = vars.timings[32], command = lambda : setStatistics(16))
        elif index == 17:
            logMenu.add_command(label = vars.timings[34], command = lambda : setStatistics(17))
        elif index == 18:
            logMenu.add_command(label = vars.timings[36], command = lambda : setStatistics(18))
        elif index == 19:
            logMenu.add_command(label = vars.timings[38], command = lambda : setStatistics(19))
        else:
            tkMessageBox.showinfo("Notice", "More than twenty matches in a single CombatLog are not suppuported. Only your first twenty matches have been added.")
            break
        amountOfMatches += 1
        index += 1
    tkMessageBox.showinfo("Notice", str(amountOfMatches) + " matches were added.")
    menuBar.add_cascade(label = "Matches", menu = logMenu)


# Function that displays the statistics for each match
def setStatistics(index):
    playerNameLabelVar.set(vars.playerName)
    damageDealtLabelVar.set(vars.damageDealt[index])
    damageTakenLabelVar.set(vars.damageTaken[index])
    healingReceivedLabelVar.set(vars.healingReceived[index])
    try:
        abilitiesOccurrencesLabelVar.set(vars.abilitiesOccurrences[index])
    except:
        if vars.statisticsFile == True:
            pass
        else:
            tkMessageBox.showerror("Error", "The abilities are missing.")


# Function that opens a saved statistics file
def openStatisticsFile():
    types = [("GSF Stastics file", "*.gsf"), ("All files", "*")]
    openDialog = tkFileDialog.Open(filetypes = types)
    fileName = openDialog.show()
    try:
        fileObject = open(fileName, "r")
    except IOError:
        return
    indexFile = 0
    vars.damageDealt = []
    vars.damageTaken = []
    vars.healingReceived = []
    vars.playerName = None
    vars.abilitiesOccurrences = {}
    vars.statisticsFile = True
    lines = fileObject.readlines()
    for line in lines:
        if line == "":
            indexFile += 1
            break
        elif line == "\n":
            indexFile += 1
            break
        else:
            vars.damageDealt.append(int(line))
            indexFile +=1
    for line in lines[indexFile:]:
        if line == "":
            indexFile += 1
            break
        elif line == "\n":
            indexFile += 1
            break
        else:
            vars.damageTaken.append(int(line))
            indexFile += 1
    for line in lines[indexFile:]:
        if line == "":
            indexFile += 1
            break
        elif line == "\n":
            indexFile += 1
            break
        else:
            vars.healingReceived.append(int(line))
            indexFile += 1
    vars.playerName = lines[indexFile]
    try:
        menuBar.delete("Matches")
    except:
        pass
    logMenu = Tkinter.Menu(menuBar, tearoff = 0)
    index = 0
    amountOfMatches = 0
    for damage in vars.damageDealt:
        if index == 0:
            logMenu.add_command(label = vars.timings[0], command = lambda : setStatistics(0))
        elif index == 1:
            logMenu.add_command(label = vars.timings[2], command = lambda : setStatistics(1))
        elif index == 2:
            logMenu.add_command(label = vars.timings[4], command = lambda : setStatistics(2))
        elif index == 3:
            logMenu.add_command(label = vars.timings[6], command = lambda : setStatistics(3))
        elif index == 4:
            logMenu.add_command(label = vars.timings[8], command = lambda : setStatistics(4))
        elif index == 5:
            logMenu.add_command(label = vars.timings[10], command = lambda : setStatistics(5))
        elif index == 6:
            logMenu.add_command(label = vars.timings[12], command = lambda : setStatistics(6))
        elif index == 7:
            logMenu.add_command(label = vars.timings[14], command = lambda : setStatistics(7))
        elif index == 8:
            logMenu.add_command(label = vars.timings[16], command = lambda : setStatistics(8))
        elif index == 9:
            logMenu.add_command(label = vars.timings[18], command = lambda : setStatistics(9))
        elif index == 10:
            logMenu.add_command(label = vars.timings[20], command = lambda : setStatistics(10))
        elif index == 11:
            logMenu.add_command(label = vars.timings[22], command = lambda : setStatistics(11))
        elif index == 12:
            logMenu.add_command(label = vars.timings[24], command = lambda : setStatistics(12))
        elif index == 13:
            logMenu.add_command(label = vars.timings[26], command = lambda : setStatistics(13))
        elif index == 14:
            logMenu.add_command(label = vars.timings[28], command = lambda : setStatistics(14))
        elif index == 15:
            logMenu.add_command(label = vars.timings[30], command = lambda : setStatistics(15))
        elif index == 16:
            logMenu.add_command(label = vars.timings[32], command = lambda : setStatistics(16))
        elif index == 17:
            logMenu.add_command(label = vars.timings[34], command = lambda : setStatistics(17))
        elif index == 18:
            logMenu.add_command(label = vars.timings[36], command = lambda : setStatistics(18))
        elif index == 19:
            logMenu.add_command(label = vars.timings[38], command = lambda : setStatistics(19))
        else:
            tkMessageBox.showinfo("Notice", "More than twenty matches in a single CombatLog are not suppuported. Only your first twenty matches have been added.")
            break
        amountOfMatches += 1
        index += 1
    tkMessageBox.showinfo("Notice", str(amountOfMatches) + " matches were added.")
    menuBar.add_cascade(label = "Matches", menu = logMenu)
    
# Function to save a statistics file containing only the statistics of a CombatLog and the name of the player
def saveStatisticsFile():
    types = [("GSF Stastics file", "*.gsf"), ("All files", "*")]
    saveDialog = tkFileDialog.SaveAs(filetypes = types)
    fileName = saveDialog.show()
    fileObject = None
    try:
        fileObject = open(fileName, "w")
    except IOError:
        tkMessageBox.showerror("Error", "This file could not be saved")
    for damage in vars.damageDealt:
        fileObject.write(str(damage) + "\n")
    fileObject.write("\n")
    for damage in vars.damageTaken:
        fileObject.write(str(damage) + "\n")
    fileObject.write("\n")
    for heal in vars.healingReceived:
        fileObject.write(str(heal) + "\n")
    fileObject.write("\n")
    fileObject.write(vars.playerName)


# Function to quit the application on user request
def quitApplication():
    try:
        mainWindow.quit()
    except:
        tkMessageBox.showerror("Error", "Exiting the application failed.")

# Function to open a messagebox that displays the information about the parser
def about():
    tkMessageBox.showinfo("About", "Thranta Squadron GSF CombatLog Parser by RedFantom, version 1.1")


# Main function to start the GUI and add most of the items in it
if __name__ == "__main__":
    # Create the mainWindow and set it's parameters before adding any widgets
    mainWindow = Tkinter.Tk()
    mainWindow.geometry('{}x{}'.format(500, 300))
    mainWindow.resizable(width = False, height = False)
    mainWindow.wm_title("Thranta Squadron GSF CombatLog Parser")

    # Create a menu bar for mainWindow
    menuBar = Tkinter.Menu(mainWindow)

    # Add a File menu to the menu bar
    fileMenu = Tkinter.Menu(menuBar, tearoff = 0)
    # Add the commands to the fileMenu
    fileMenu.add_command(label = "Open CombatLog", command = openCombatLog)
    fileMenu.add_command(label = "Open Statistics file", command = openStatisticsFile)
    fileMenu.add_command(label = "Save Statistics file", command = saveStatisticsFile)
    fileMenu.add_separator()
    fileMenu.add_command(label = "Exit", command = quitApplication)
    # Add the fileMenu to the menuBar
    menuBar.add_cascade(label = "File", menu = fileMenu)

    # Add an about button to the menuBar
    menuBar.add_command(label = "About", command = about)

    # Configure mainWindow with this menuBar
    mainWindow.config(menu = menuBar)

    # Add the Labels to show the statistics
    damageDealtLabelVar = Tkinter.StringVar()
    damageTakenLabelVar = Tkinter.StringVar()
    healingReceivedLabelVar = Tkinter.StringVar()
    playerNameLabelVar = Tkinter.StringVar()
    abilitiesOccurrencesLabelVar = Tkinter.StringVar()

    damageDealtLabel = Tkinter.Label(mainWindow, textvariable = damageDealtLabelVar)
    damageTakenLabel = Tkinter.Label(mainWindow, textvariable = damageTakenLabelVar)
    healingReceivedLabel = Tkinter.Label(mainWindow, textvariable = healingReceivedLabelVar)
    playerNameLabel = Tkinter.Label(mainWindow, textvariable = playerNameLabelVar)
    abilitiesOccurrencesLabel = Tkinter.Label(mainWindow, textvariable = abilitiesOccurrencesLabelVar, justify = Tkinter.LEFT, wraplength = 450)

    damageDealtTextLabel = Tkinter.Label(mainWindow, text = "Damage dealt: ")
    damageTakenTextLabel = Tkinter.Label(mainWindow, text = "Damage taken: ")
    healingReceivedTextLabel = Tkinter.Label(mainWindow, text = "Healing received: ")
    abilitiesLabel = Tkinter.Label(mainWindow, text = "Abilities used: ")
    playerLabel = Tkinter.Label(mainWindow, text = "Character name: ")

    playerLabel.grid(column = 0, row = 0, sticky = Tkinter.W)
    playerNameLabel.grid(column = 1, row = 0, sticky = Tkinter.W)
    damageDealtTextLabel.grid(column = 0, row = 1, sticky = Tkinter.W)
    damageTakenTextLabel.grid(column = 0, row = 2, sticky = Tkinter.W)
    healingReceivedTextLabel.grid(column = 0, row = 3, sticky = Tkinter.W)
    damageDealtLabel.grid(column = 1, row = 1, sticky = Tkinter.W)
    damageTakenLabel.grid(column = 1, row = 2, sticky = Tkinter.W)
    healingReceivedLabel.grid(column = 1, row = 3, sticky = Tkinter.W)

    abilitiesLabel.grid(column = 0, columnspan = 2, row = 4, rowspan = 1, sticky = Tkinter.W)
    abilitiesOccurrencesLabel.grid(column = 0, columnspan = 2, row = 5, rowspan = 6, sticky = Tkinter.W)

    # Start the loop
    mainWindow.mainloop()
