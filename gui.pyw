# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
# General imports
import re
from datetime import datetime
# Own modules
import vars
import parse
import client
import frames

if __name__ == "__main__":
    mainWindow = tk.Tk()
    mainWindow.resizable(width = False, height = False)
    mainWindow.geometry("{}x{}".format(1000, 600))
    mainWindow.wm_title("Thranta Squadron GSF CombatLog Parser")

    # Add a notebook widget to the mainWindow and add its tabs
    notebook = ttk.Notebook(mainWindow, height = 600, width = 1000)
    fileTabFrame = ttk.Frame(notebook)
    realtimeTabFrame = ttk.Frame(notebook)
    shareTabFrame = ttk.Frame(notebook)
    settingsTabFrame = ttk.Frame(notebook)
    fileFrame = frames.fileFrame(fileTabFrame)
    fileFrame.gridWidgets()
    eventsFrame = frames.eventsFrame(fileTabFrame)
    eventsFrame.gridWidgets()
    fileFrame.grid(column = 0, row = 0, columnspan = 2, rowspan = 24)
    eventsFrame.grid(column = 2, row = 12, columnspan = 4, rowspan = 12, sticky = tk.N + tk.S + tk.W + tk.E)
    notebook.add(fileTabFrame, text = "File parsing")
    notebook.add(realtimeTabFrame, text = "Real-time parsing")
    notebook.add(shareTabFrame, text = "Sharing and Leaderboards")
    notebook.add(settingsTabFrame, text = "Settings")
    # notebook.add(alliesTab, text = "Allies")
    notebook.grid(column = 0, row = 0)
    fileObject = open("CombatLog.txt", "r")
    lines = fileObject.readlines()
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
    eventsFrame.updateAbilities(1)
    mainWindow.mainloop()
