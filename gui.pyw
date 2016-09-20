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
    fileFrame.grid_widgets()
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
    vars.statisticsfile_cube= False
    vars.player_numbers = parse.determinePlayer(lines)
    vars.player_name = parse.determinePlayerName(lines)
    vars.file_cube, vars.match_timings, vars.spawn_timings = parse.splitter(lines, vars.player_numbers)
    # Then get the useful information out of the matches
    (vars.abilities, vars.damagetaken, vars.damagedealt, vars.selfdamage, vars.healingreceived, vars.enemies,
     vars.criticalcount, vars.criticalluck, vars.hitcount, vars.enemydamaged, vars.enemydamaget, vars.match_timings, 
     vars.spawn_timings) = parse.parse_file(vars.file_cube, vars.player_numbers, vars.match_timings, vars.spawn_timings)
    fileFrame.add_files()
    fileFrame.add_matches()
    fileFrame.add_spawns()
    mainWindow.mainloop()
