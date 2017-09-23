# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
from archive import parse, vars, client


def sendCombatLog():
    vars.userName = nameEntry.get()
    if vars.statisticsFile:
        tkinter.messagebox.showinfo("Notice", "A statistics file can not be shared.")
        return
    if not vars.fileName:
        tkinter.messagebox.showinfo("Notice", "No file has been selected yet.")
        return
    if (vars.userName == "" or vars.userName == "Enter your name for sending here"
        or vars.userName == " "):
        tkinter.messagebox.showinfo("Notice", "No user name has been entered yet.")
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
    openDialog = tkinter.filedialog.Open(filetypes=types)
    vars.fileName = openDialog.show()
    # Try to create a fileObject with this file
    try:
        fileObject = open(vars.fileName, "r")
        lines = fileObject.readlines()
    # Since the user has to choose an existing file, the IOError will only occur when the dialog was canceled, and the
    # program must end.
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
    (vars.damageDealt, vars.damageTaken, vars.healingReceived, vars.selfdamage, vars.abilitiesOccurrences,
     vars.datetimes,
     vars.enemyMatrix, vars.enemyDamageDealt, vars.enemyDamageTaken, vars.criticalLuck) = parse.parseMatches(
        vars.matches, vars.timings, vars.playerNumbers)
    # Get the amount of deaths from another function
    vars.deaths = parse.determineDeaths(vars.matches)
    # Add a new menu cascade for the matches
    logMenu = tkinter.Menu(menuBar, tearoff=0)
    # Start iterating through the matches and add items to the menu cascade
    index = 0
    amountOfMatches = 0
    for index, match in enumerate(vars.matches):
        # This can only be done with a lambda function with a static argument for setStatistics()
        logMenu.add_command(label=vars.timings[index * 2], command=lambda index=index: setStatistics(index))
        amountOfMatches += 1
    # Show the user how many matches were added
    tkinter.messagebox.showinfo("Notice", str(amountOfMatches) + " matches were added.")
    menuBar.add_cascade(label="Matches", menu=logMenu)


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
            tkinter.messagebox.showerror("Error", "The critical count is missing")
    try:
        deathsLabelVar.set(vars.deaths[index])
    except:
        if vars.statisticsFile == True:
            deathsLabelVar.set("Unavailable for a statistics file.")
        else:
            tkinter.messagebox.showerror("Error", "The amount of deaths is missing")
    try:
        selfdamageLabelVar.set(vars.selfdamage[index])
    except:
        if vars.statisticsFile == True:
            selfdamageLabelVar.set("Unavailable for a statistics file.")
        else:
            tkinter.messagebox.showerror("Error", "The selfdamage is missing.")
    # If there are no abilities, it must be a statistics file and the abilities must be empty. Otherwise,
    # display an error message.
    abilities_string = ""
    for key, value in vars.abilitiesOccurrences[index].items():
        abilities_string += key + "  :  " + str(value) + "\n"
    try:
        abilitiesOccurrencesLabelVar.set(abilities_string)
    except:
        if vars.statisticsFile == True:
            abilitiesOccurrencesLabelVar.set("Unavailable for a statistics file.")
        else:
            tkinter.messagebox.showerror("Error", "The abilities are missing.")
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
    openDialog = tkinter.filedialog.Open(filetypes=types)
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
            indexFile += 1
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
    logMenu = tkinter.Menu(menuBar, tearoff=0)
    index = 0
    amountOfMatches = 0
    for damage in vars.damageDealt:
        logMenu.add_command(label=vars.timings[index * 2], command=lambda num=index: setStatistics(num))
        amountOfMatches += 1
        index += 1
    tkinter.messagebox.showinfo("Notice", str(amountOfMatches) + " matches were added.")
    menuBar.add_cascade(label="Matches", menu=logMenu)


# Function to save a statistics file containing only the statistics of a CombatLog and the name of the player
def saveStatisticsFile():
    # Open a dialog to save with .gsf as the default file type
    types = [("GSF Stastics file", "*.gsf"), ("All files", "*")]
    saveDialog = tkinter.filedialog.SaveAs(defaultextension=".gsf", filetypes=types)
    fileName = saveDialog.show()
    # Create the fileObject before reference
    fileObject = None
    # Try to save the file and display a warning if not possible
    try:
        fileObject = open(fileName, "w")
    except IOError:
        tkinter.messagebox.showerror("Error", "This file could not be saved")
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
        tkinter.messagebox.showerror("Error", "Exiting the application failed.")


# Function to open a messagebox that displays the information about the parser
def about():
    tkinter.messagebox.showinfo("About",
                                "Thranta Squadron GSF CombatLog Parser by RedFantom and Daethyra, version 1.4.0")
    return


def info():
    tkinter.messagebox.showinfo("Server info",
                                "The server for sending CombatLog is currently set to: " + vars.serverAddress +
                                " over port " + str(vars.serverPort))
    return


# Main function to start the GUI and add most of the items in it
# Create the mainWindow and set it's parameters before adding any widgets
mainWindow = tkinter.Tk()
mainWindow.geometry('{}x{}'.format(500, 300))
mainWindow.wm_title("Thranta Squadron GSF CombatLog Parser")

# Create a menu bar for mainWindow
menuBar = tkinter.Menu(mainWindow)

# Add a File menu to the menu bar
fileMenu = tkinter.Menu(menuBar, tearoff=0)
# Add the commands to the fileMenu
fileMenu.add_command(label="Open CombatLog", command=openCombatLog)
fileMenu.add_command(label="Open Statistics file", command=openStatisticsFile)
fileMenu.add_command(label="Save Statistics file", command=saveStatisticsFile)
fileMenu.add_separator()
fileMenu.add_command(label="About", command=about)
fileMenu.add_command(label="Server info", command=info)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=quitApplication)
# Add the fileMenu to the menuBar
menuBar.add_cascade(label="File", menu=fileMenu)

# Configure mainWindow with this menuBar
mainWindow.config(menu=menuBar)

# Add a notebook widget to the mainWindow and add its tabs
notebook = tkinter.ttk.Notebook(mainWindow, height=575, width=498)
statisticsTab = tkinter.ttk.Frame(notebook)
abilitiesTab = tkinter.ttk.Frame(notebook)
enemiesTab = tkinter.ttk.Frame(notebook)
alliesTab = tkinter.ttk.Frame(notebook)
shareTab = tkinter.ttk.Frame(notebook)
notebook.add(statisticsTab, text="Statistics")
notebook.add(abilitiesTab, text="Abilities")
notebook.add(enemiesTab, text="Enemies")
# notebook.add(alliesTab, text = "Allies")
notebook.add(shareTab, text="Share")
notebook.grid(column=0, row=0)

# Add the variables to show the statistics
damageDealtLabelVar = tkinter.StringVar()
damageTakenLabelVar = tkinter.StringVar()
healingReceivedLabelVar = tkinter.StringVar()
playerNameLabelVar = tkinter.StringVar()
abilitiesOccurrencesLabelVar = tkinter.StringVar()
selfdamageLabelVar = tkinter.StringVar()
amountOfCritsLabelVar = tkinter.StringVar()
percentOfCritsLabelVar = tkinter.StringVar()
deathsLabelVar = tkinter.StringVar()

# Add the labels to show the variables that were just created
damageDealtLabel = tkinter.Label(statisticsTab, textvariable=damageDealtLabelVar)
damageTakenLabel = tkinter.Label(statisticsTab, textvariable=damageTakenLabelVar)
healingReceivedLabel = tkinter.Label(statisticsTab, textvariable=healingReceivedLabelVar)
playerNameLabel = tkinter.Label(statisticsTab, textvariable=playerNameLabelVar)
abilitiesOccurrencesLabel = tkinter.Label(abilitiesTab, textvariable=abilitiesOccurrencesLabelVar,
                                          justify=tkinter.LEFT, wraplength=450)
selfdamageLabel = tkinter.Label(statisticsTab, textvariable=selfdamageLabelVar)
amountOfCritsLabel = tkinter.Label(statisticsTab, textvariable=amountOfCritsLabelVar)
percentOfCritsLabel = tkinter.Label(statisticsTab, textvariable=percentOfCritsLabelVar)
deathsLabel = tkinter.Label(statisticsTab, textvariable=deathsLabelVar)

# Add the labels to show what is displayed in each label with a variable
damageDealtTextLabel = tkinter.Label(statisticsTab, text="Damage dealt: ")
damageTakenTextLabel = tkinter.Label(statisticsTab, text="Damage taken: ")
healingReceivedTextLabel = tkinter.Label(statisticsTab, text="Healing received: ")
abilitiesLabel = tkinter.Label(abilitiesTab, text="Abilities used: ")
playerLabel = tkinter.Label(statisticsTab, text="Character name: ")
selfdamageTextLabel = tkinter.Label(statisticsTab, text="Selfdamage: ")
amountOfCritsTextLabel = tkinter.Label(statisticsTab, text="Critical count: ")
percentOfCritsTextLabel = tkinter.Label(statisticsTab, text="Critical percentage: ")
deathsTextLabel = tkinter.Label(statisticsTab, text="Amount of deaths: ")

# Add a label to show a description in the Share tab
descriptionLabel = tkinter.Label(shareTab,
                                 text="""You can send your CombatLog to the Thranta Squadron database server for
                                         analysis. This would help the developers and you could earn a spot in the
                                         Holocron Vault with your CombatLog. This functionality is still in
                                         beta.""",
                                 justify=tkinter.LEFT, wraplength=450)
descriptionLabel.grid(column=0, row=0, columnspan=2)

# Add a progress bar and a button to the Share tab that is accessible for client.py
vars.progressBar = tkinter.ttk.Progressbar(shareTab, orient="horizontal", length=350, mode="determinate")
vars.progressBar.grid(column=0, row=3, columnspan=1)

# Add a label to show a warning
warningLabelText = tkinter.StringVar()
warningLabel = tkinter.Label(shareTab, textvariable=warningLabelText, justify=tkinter.LEFT, wraplength=450)
warningLabel.grid(column=0, row=4, columnspan=2)
checkConnectionObject = client.initConnection()
if not checkConnectionObject:
    warningLabelText.set("The server for sending is not available. Sending CombatLogs has been disabled.")
    # Add a button to start sending the file but disable it
    sendButton = tkinter.Button(shareTab, text="Send CombatLog", command=sendCombatLog, state=tkinter.DISABLED)
    sendButton.grid(column=1, row=3)
else:
    checkConnectionObject.close()
    warningLabelText.set("The server is available.")
    # Add a button to start sending the file
    sendButton = tkinter.Button(shareTab, text="Send CombatLog", command=sendCombatLog)
    sendButton.grid(column=1, row=3)

# Lay out the labels in a grid
playerLabel.grid(column=0, row=0, sticky=tkinter.W)
playerNameLabel.grid(column=1, row=0, sticky=tkinter.W)
damageDealtTextLabel.grid(column=0, row=1, sticky=tkinter.W)
damageTakenTextLabel.grid(column=0, row=2, sticky=tkinter.W)
healingReceivedTextLabel.grid(column=0, row=3, sticky=tkinter.W)
damageDealtLabel.grid(column=1, row=1, sticky=tkinter.W)
damageTakenLabel.grid(column=1, row=2, sticky=tkinter.W)
healingReceivedLabel.grid(column=1, row=3, sticky=tkinter.W)
selfdamageTextLabel.grid(column=0, row=4, sticky=tkinter.W)
selfdamageLabel.grid(column=1, row=4, sticky=tkinter.W)
amountOfCritsTextLabel.grid(column=0, row=5, sticky=tkinter.W)
amountOfCritsLabel.grid(column=1, row=5, sticky=tkinter.W)
percentOfCritsTextLabel.grid(column=0, row=6, sticky=tkinter.W)
percentOfCritsLabel.grid(column=1, row=6, sticky=tkinter.W)
deathsTextLabel.grid(column=0, row=7, sticky=tkinter.W)
deathsLabel.grid(column=1, row=7, sticky=tkinter.W)

# The abilities are in the grid, but take up two columns
abilitiesLabel.grid(column=0, columnspan=2, row=0, rowspan=1, sticky=tkinter.W)
abilitiesOccurrencesLabel.grid(column=0, columnspan=2, row=1, rowspan=6, sticky=tkinter.W)

# Add an Entry-bar to let the user enter his/her name for sending with the CombatLog
nameEntry = tkinter.Entry(shareTab, width=80)
nameEntry.grid(column=0, row=2, columnspan=2, sticky=tkinter.W)
nameEntry.insert(0, "Enter your name for sending here")

# Add the elements for the enemiesTab
topLabelOne = tkinter.Label(enemiesTab, text="Enemy ID number   ")
topLabelTwo = tkinter.Label(enemiesTab, text="Damage dealt to you   ")
topLabelThree = tkinter.Label(enemiesTab, text="Damage taken from you   ")
topLabelOne.grid(column=0, row=0)
topLabelTwo.grid(column=1, row=0)
topLabelThree.grid(column=2, row=0)
enemyListLabelText = tkinter.StringVar()
enemyListLabel = tkinter.Label(enemiesTab, textvariable=enemyListLabelText, justify=tkinter.LEFT)
enemyListLabel.grid(column=0, row=1, columnspan=1, rowspan=20, sticky=tkinter.W)
enemyDealtLabelText = tkinter.StringVar()
enemyDealtLabel = tkinter.Label(enemiesTab, textvariable=enemyDealtLabelText, justify=tkinter.LEFT)
enemyDealtLabel.grid(column=1, row=1, columnspan=1, rowspan=20, sticky=tkinter.W)
enemyTakenLabelText = tkinter.StringVar()
enemyTakenLabel = tkinter.Label(enemiesTab, textvariable=enemyTakenLabelText, justify=tkinter.LEFT)
enemyTakenLabel.grid(column=2, row=1, columnspan=1, rowspan=20, sticky=tkinter.W)

# Start the loop
mainWindow.mainloop()
