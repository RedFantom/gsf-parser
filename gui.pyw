# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import Tkinter
import ttk
import tkMessageBox
import tkFileDialog
import re
import vars
import parse
import client
from datetime import datetime

def sendCombatLog():
    vars.userName = nameEntry.get()
    if vars.statisticsFile == True:
        tkMessageBox.showinfo("Notice", "A statistics file can not be shared.")
        return
    if vars.fileName == None:
        tkMessageBox.showinfo("Notice", "No file has been selected yet.")
        return
    if(vars.userName == "" or vars.userName == "Enter your name for sending here"
        or vars.userName == " "):
        tkMessageBox.showinfo("Notice", "No user name has been entered yet.")
        return
    client.send(vars.fileName, vars.userName)
    return

# Call back fuction for the Open CombatLog menu item
# Parses the file and places the results in the variables in vars.py
# Then adds a new menu cascade, of which all items call the setStatistics() function with lambda
def openCombatLog():
    # First try to delete the pervious menu cascade. Will fail if it doesn't yet exist.
    try:
        menuBar.delete("Matches")
    except:
        pass
    # Create file-opening dialog and show it.
    types = [("SWTOR CombatLog", "*.txt"), ("All files", "*")]
    openDialog = tkFileDialog.Open(filetypes = types)
    vars.fileName = openDialog.show()
    # Try to create a fileObject with this file
    try:
        fileObject = open(vars.fileName, "r")
        lines = fileObject.readlines()
    # Since the user has to choose an existing file, the IOError will only occur when the dialog was canceled, and the program must end.
    except IOError:
        return

    # -- Parsing starts --

    # This is not a statistics file, and setStatistics() must be able to determine that
    vars.statisticsFile = False
    # First split the lines of the file into matches
    vars.matches, vars.timings = parse.splitter(lines)
    # Then determine the playerName
    vars.playerName = parse.determinePlayerName(lines)
    # Determine the player's ID numbers
    vars.playerNumbers = parse.determinePlayer(lines)
    # Then get the useful information out of the matches
    (vars.damageDealt, vars.damageTaken, vars.healingReceived, vars.selfdamage, vars.abilitiesOccurrences, vars.datetimes, 
     vars.enemyMatrix, vars.enemyDamageDealt, vars.enemyDamageTaken, vars.criticalLuck) = parse.parseMatches(vars.matches, vars.timings, vars.playerNumbers)
    # Get the amount of deaths from another function
    vars.deaths = parse.determineDeaths(vars.matches)
    # Add a new menu cascade for the matches
    logMenu = Tkinter.Menu(menuBar, tearoff = 0)
    # Start iterating through the matches and add items to the menu cascade
    index = 0
    amountOfMatches = 0
    for match in vars.matches:
        # This can only be done with a lambda function with a static argument for setStatistics()
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
            # If the user has more than twenty matches in one combatLog, there are not enough menu items. Display a warning.
            tkMessageBox.showinfo("Notice", "More than twenty matches in a single CombatLog are not suppuported. Only your first twenty matches have been added.")
            break
        amountOfMatches += 1
        index += 1
    # Show the user how many matches were added
    tkMessageBox.showinfo("Notice", str(amountOfMatches) + " matches were added.")
    menuBar.add_cascade(label = "Matches", menu = logMenu)


# Function that displays the statistics for each match
def setStatistics(index):
    # Set the labels to display the data from the variables
    playerNameLabelVar.set(vars.playerName)
    damageDealtLabelVar.set(vars.damageDealt[index])
    damageTakenLabelVar.set(vars.damageTaken[index])
    healingReceivedLabelVar.set(vars.healingReceived[index])
    (absolute, percent) = vars.criticalLuck[index]
    try:
        amountOfCritsLabelVar.set(absolute)
        percentOfCritsLabelVar.set(str(percent) + "%")
    except:
        if vars.statisticsFile == True:
            amountOfCritsLabelVar.set("Unavailable for a statistics file.")
            percentOfCritsLabelVar.set("Unavailable for a statistics file.")
        else:
            tkMessageBox.showerror("Error", "The critical count is missing")
    try:
        deathsLabelVar.set(vars.deaths[index])
    except:
        if vars.statisticsFile == True:
            deathsLabelVar.set("Unavailable for a statistics file.")
        else:
            tkMessageBox.showerror("Error", "The amount of deaths is missing")
    try:
        selfdamageLabelVar.set(vars.selfdamage[index])
    except:
        if vars.statisticsFile == True:
            selfdamageLabelVar.set("Unavailable for a statistics file.")
        else:
            tkMessageBox.showerror("Error", "The selfdamage is missing.")
    # If there are no abilities, it must be a statistics file and the abilities must be empty. Otherwise, display an error message.
    try:
        abilitiesOccurrencesLabelVar.set(vars.abilitiesOccurrences[index])
    except:
        if vars.statisticsFile == True:
            abilitiesOccurrencesLabelVar.set("Unavailable for a statistics file.")
        else:
            tkMessageBox.showerror("Error", "The abilities are missing.")
    if vars.statisticsFile == True:
        enemyListLabelText.set("Unavailable for a statistics file.")
    else:
        tempTextList = ""
        tempTextDealt = ""
        tempTextTaken = ""
        enemyList = vars.enemyMatrix[index]
        for enemy in enemyList:
            tempTextList = tempTextList + enemy + "\n"
            tempTextDealt = tempTextDealt + str(vars.enemyDamageDealt[enemy]) + "\n"
            tempTextTaken = tempTextTaken + str(vars.enemyDamageTaken[enemy]) + "\n"
        enemyListLabelText.set(tempTextList)
        enemyDealtLabelText.set(tempTextDealt)
        enemyTakenLabelText.set(tempTextTaken)
    return



# Function that opens a saved statistics file
def openStatisticsFile():
    # Open a dialog to open a statistics file.
    types = [("GSF Stastics file", "*.gsf"), ("All files", "*")]
    openDialog = tkFileDialog.Open(filetypes = types)
    vars.fileName = openDialog.show()
    # Try to create a fileObject with this file. If the dialog is cancelled, the method must exit.
    try:
        fileObject = open(vars.fileName, "r")
    except IOError:
        return
    # Clear the variables.
    indexFile = 0
    vars.damageDealt = []
    vars.damageTaken = []
    vars.healingReceived = []
    vars.playerName = None
    vars.abilitiesOccurrences = {}
    vars.statisticsFile = True
    # Read the lines from the file
    lines = fileObject.readlines()
    # Iterate over the lines and put them in the right variables
    '''
    The statistics file is layed-out as follows:

    Damage dealt in the first match
    Damage dealt in the second match
    Damage dealt in the third match
    ...
    \n
    Damage taken in the first match
    Damage taken in the second match
    ...
    \n
    And so on for the other variables.
    Backwards compatibility for future versions with extra data by adding new information to the end of the file.
    '''
    for line in lines:
        # If a line is empty or contains a newline-character, the section has ended.
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
    # Works the same as in openCombatLog()
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
    # Open a dialog to save with .gsf as the default file type
    types = [("GSF Stastics file", "*.gsf"), ("All files", "*")]
    saveDialog = tkFileDialog.SaveAs(defaultextension = ".gsf", filetypes = types)
    fileName = saveDialog.show()
    # Create the fileObject before reference
    fileObject = None
    # Try to save the file and display a warning if not possible
    try:
        fileObject = open(fileName, "w")
    except IOError:
        tkMessageBox.showerror("Error", "This file could not be saved")
    # Create the statisticsFile according to the description in openStatisticsFile()
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
    tkMessageBox.showinfo("About", "Thranta Squadron GSF CombatLog Parser by RedFantom and Daethyra, version 1.3.0")
    return

def info():
    tkMessageBox.showinfo("Server info", "The server for sending CombatLog is currently set to: " + vars.serverAddress + " over port " + str(vars.serverPort))
    return


# Main function to start the GUI and add most of the items in it
if __name__ == "__main__":
    # Create the mainWindow and set it's parameters before adding any widgets
    mainWindow = Tkinter.Tk()
    mainWindow.geometry('{}x{}'.format(500, 600))
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
    fileMenu.add_command(label = "About", command = about)
    fileMenu.add_command(label = "Server info", command = info)
    fileMenu.add_separator()
    fileMenu.add_command(label = "Exit", command = quitApplication)
    # Add the fileMenu to the menuBar
    menuBar.add_cascade(label = "File", menu = fileMenu)

    # Configure mainWindow with this menuBar
    mainWindow.config(menu = menuBar)

    # Add a notebook widget to the mainWindow and add its tabs
    notebook = ttk.Notebook(mainWindow, height = 575, width = 498)
    statisticsTab = ttk.Frame(notebook)
    abilitiesTab = ttk.Frame(notebook)
    enemiesTab = ttk.Frame(notebook)
    alliesTab = ttk.Frame(notebook)
    shareTab = ttk.Frame(notebook)
    notebook.add(statisticsTab, text = "Statistics")
    notebook.add(abilitiesTab, text = "Abilities")
    notebook.add(enemiesTab, text = "Enemies")
    # notebook.add(alliesTab, text = "Allies")
    notebook.add(shareTab, text = "Share")
    notebook.grid(column = 0, row = 0)

    # Add the variables to show the statistics
    damageDealtLabelVar = Tkinter.StringVar()
    damageTakenLabelVar = Tkinter.StringVar()
    healingReceivedLabelVar = Tkinter.StringVar()
    playerNameLabelVar = Tkinter.StringVar()
    abilitiesOccurrencesLabelVar = Tkinter.StringVar()
    selfdamageLabelVar = Tkinter.StringVar()
    amountOfCritsLabelVar = Tkinter.StringVar()
    percentOfCritsLabelVar = Tkinter.StringVar()
    deathsLabelVar = Tkinter.StringVar()

    # Add the labels to show the variables that were just created
    damageDealtLabel = Tkinter.Label(statisticsTab, textvariable = damageDealtLabelVar)
    damageTakenLabel = Tkinter.Label(statisticsTab, textvariable = damageTakenLabelVar)
    healingReceivedLabel = Tkinter.Label(statisticsTab, textvariable = healingReceivedLabelVar)
    playerNameLabel = Tkinter.Label(statisticsTab, textvariable = playerNameLabelVar)
    abilitiesOccurrencesLabel = Tkinter.Label(abilitiesTab, textvariable = abilitiesOccurrencesLabelVar, justify = Tkinter.LEFT, wraplength = 450)
    selfdamageLabel = Tkinter.Label(statisticsTab, textvariable = selfdamageLabelVar)
    amountOfCritsLabel = Tkinter.Label(statisticsTab, textvariable = amountOfCritsLabelVar)
    percentOfCritsLabel = Tkinter.Label(statisticsTab, textvariable = percentOfCritsLabelVar)
    deathsLabel = Tkinter.Label(statisticsTab, textvariable = deathsLabelVar)

    # Add the labels to show what is displayed in each label with a variable
    damageDealtTextLabel = Tkinter.Label(statisticsTab, text = "Damage dealt: ")
    damageTakenTextLabel = Tkinter.Label(statisticsTab, text = "Damage taken: ")
    healingReceivedTextLabel = Tkinter.Label(statisticsTab, text = "Healing received: ")
    abilitiesLabel = Tkinter.Label(abilitiesTab, text = "Abilities used: ")
    playerLabel = Tkinter.Label(statisticsTab, text = "Character name: ")
    selfdamageTextLabel = Tkinter.Label(statisticsTab, text = "Selfdamage: ")
    amountOfCritsTextLabel = Tkinter.Label(statisticsTab, text = "Critical count: ")
    percentOfCritsTextLabel = Tkinter.Label(statisticsTab, text = "Critical percentage: ")
    deathsTextLabel = Tkinter.Label(statisticsTab, text = "Amount of deaths: ")

    # Add a label to show a description in the Share tab
    descriptionLabel = Tkinter.Label(shareTab, text = """You can send your CombatLog to the Thranta Squadron database server for analysis. This would help the developers and you could earn a spot in the Holocron Vault with your CombatLog. This functionality is still in beta.""",
                                     justify = Tkinter.LEFT, wraplength = 450)
    descriptionLabel.grid(column = 0, row = 0, columnspan = 2)

    # Add a progress bar and a button to the Share tab that is accessible for client.py
    vars.progressBar = ttk.Progressbar(shareTab, orient = "horizontal", length = 350, mode = "determinate")
    vars.progressBar.grid(column = 0, row = 3, columnspan = 1)

    # Add a label to show a warning
    warningLabelText = Tkinter.StringVar()
    warningLabel = Tkinter.Label(shareTab, textvariable = warningLabelText, justify = Tkinter.LEFT, wraplength = 450)
    warningLabel.grid(column = 0, row = 4, columnspan = 2)
    checkConnectionObject = client.initConnection()
    if checkConnectionObject == None:
        warningLabelText.set("The server for sending is not available. Sending CombatLogs has been disabled.")
        # Add a button to start sending the file but disable it
        sendButton = Tkinter.Button(shareTab, text = "Send CombatLog", command = sendCombatLog, state = Tkinter.DISABLED)
        sendButton.grid(column = 1, row = 3)
    else:
        checkConnectionObject.close()
        warningLabelText.set("The server is available.")
        # Add a button to start sending the file
        sendButton = Tkinter.Button(shareTab, text = "Send CombatLog", command = sendCombatLog)
        sendButton.grid(column = 1, row = 3)

    # Lay out the labels in a grid
    playerLabel.grid(column = 0, row = 0, sticky = Tkinter.W)
    playerNameLabel.grid(column = 1, row = 0, sticky = Tkinter.W)
    damageDealtTextLabel.grid(column = 0, row = 1, sticky = Tkinter.W)
    damageTakenTextLabel.grid(column = 0, row = 2, sticky = Tkinter.W)
    healingReceivedTextLabel.grid(column = 0, row = 3, sticky = Tkinter.W)
    damageDealtLabel.grid(column = 1, row = 1, sticky = Tkinter.W)
    damageTakenLabel.grid(column = 1, row = 2, sticky = Tkinter.W)
    healingReceivedLabel.grid(column = 1, row = 3, sticky = Tkinter.W)
    selfdamageTextLabel.grid(column = 0, row = 4, sticky = Tkinter.W)
    selfdamageLabel.grid(column = 1, row = 4, sticky = Tkinter.W)
    amountOfCritsTextLabel.grid(column = 0, row = 5, sticky = Tkinter.W)
    amountOfCritsLabel.grid(column = 1, row = 5, sticky = Tkinter.W)
    percentOfCritsTextLabel.grid(column = 0, row = 6, sticky = Tkinter.W)
    percentOfCritsLabel.grid(column = 1, row = 6, sticky = Tkinter.W)
    deathsTextLabel.grid(column = 0, row = 7, sticky = Tkinter.W)
    deathsLabel.grid(column = 1, row = 7, sticky = Tkinter.W)

    # The abilities are in the grid, but take up two columns
    abilitiesLabel.grid(column = 0, columnspan = 2, row = 0, rowspan = 1, sticky = Tkinter.W)
    abilitiesOccurrencesLabel.grid(column = 0, columnspan = 2, row = 1, rowspan = 6, sticky = Tkinter.W)

    # Add an Entry-bar to let the user enter his/her name for sending with the CombatLog
    nameEntry = Tkinter.Entry(shareTab, width = 80)
    nameEntry.grid(column = 0, row = 2, columnspan = 2, sticky = Tkinter.W)
    nameEntry.insert(0, "Enter your name for sending here")

    # Add the elements for the enemiesTab
    topLabelOne = Tkinter.Label(enemiesTab, text = "Enemy ID number   ")
    topLabelTwo = Tkinter.Label(enemiesTab, text = "Damage dealt to you   ")
    topLabelThree = Tkinter.Label(enemiesTab, text = "Damage taken from you   ")
    topLabelOne.grid(column = 0, row = 0)
    topLabelTwo.grid(column = 1, row = 0)
    topLabelThree.grid(column = 2, row = 0)
    enemyListLabelText = Tkinter.StringVar()
    enemyListLabel = Tkinter.Label(enemiesTab, textvariable = enemyListLabelText, justify = Tkinter.LEFT)
    enemyListLabel.grid(column = 0, row = 1, columnspan = 1, rowspan = 20, sticky = Tkinter.W)
    enemyDealtLabelText = Tkinter.StringVar()
    enemyDealtLabel = Tkinter.Label(enemiesTab, textvariable = enemyDealtLabelText, justify = Tkinter.LEFT)
    enemyDealtLabel.grid(column = 1, row = 1, columnspan = 1, rowspan =20, sticky = Tkinter.W)
    enemyTakenLabelText = Tkinter.StringVar()
    enemyTakenLabel = Tkinter.Label(enemiesTab, textvariable = enemyTakenLabelText, justify = Tkinter.LEFT)
    enemyTakenLabel.grid(column = 2, row = 1, columnspan = 1, rowspan = 20, sticky = Tkinter.W)


    # Start the loop
    mainWindow.mainloop()
