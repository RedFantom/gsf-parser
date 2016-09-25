# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
# General imports
import re
import os
import getpass
from datetime import datetime
# Own modules
import vars
import parse
import client
import frames
import statistics

class main_window:
    def __init__(self):
        self.window = tk.Tk()
        self.window.resizable(width = False, height = False)
        self.window.geometry("{}x{}".format(1000, 625))
        self.window.wm_title("Thranta Squadron GSF Parser")
        default_path = 'C:/Users/' + getpass.getuser() + "/Documents/Star Wars - The Old Republic/CombatLogs"
        os.chdir(default_path)
        # Add a self.notebook widget to the self.window and add its tabsw
        self.notebook = ttk.Notebook(self.window, height = 600, width = 1000)
        self.file_tab_frame = ttk.Frame(self.notebook)
        self.realtime_tab_frame = ttk.Frame(self.notebook)
        self.share_tab_frame = ttk.Frame(self.notebook)
        self.settings_tab_frame = ttk.Frame(self.notebook)
        self.file_select_frame = frames.file_frame(self.file_tab_frame, self)
        self.file_select_frame.pack(side = tk.LEFT)
        self.middle_frame = frames.middle_frame(self.file_tab_frame, self)
        self.middle_frame.grid_widgets()
        self.file_select_frame.grid_widgets()
        self.middle_frame.pack(side = tk.LEFT, padx = 5)
        self.ship_containment_frame = ttk.Frame(self.file_tab_frame, width = 500, height = 600)
        self.ship_containment_frame.pack(side = tk.RIGHT)
        self.ship_frame = frames.ship_frame(self.ship_containment_frame)
        self.ship_frame.grid(column = 0, row = 0, sticky = tk.N + tk.S + tk.W + tk.E)
        self.ship_frame.pack(side = tk.RIGHT)
        self.notebook.add(self.file_tab_frame, text = "File parsing")
        self.notebook.add(self.realtime_tab_frame, text = "Real-time parsing")
        self.notebook.add(self.share_tab_frame, text = "Sharing and Leaderboards")
        self.notebook.add(self.settings_tab_frame, text = "Settings")
        # self.notebook.add(alliesTab, text = "Allies")
        self.notebook.grid(column = 0, row = 0)
        '''
        # DEBUG
        self.fileObject = open("CombatLog.txt", "r")
        self.lines = self.fileObject.readlines()
        # This is not a statistics file, and setStatistics() must be able to determine that
        vars.statisticsfile = False
        vars.player_numbers = parse.determinePlayer(self.lines)
        vars.player_name = parse.determinePlayerName(self.lines)
        vars.file_cube, vars.match_timings, vars.spawn_timings = parse.splitter(self.lines, vars.player_numbers)
        # Then get the useful information out of the matches
        (vars.abilities, vars.damagetaken, vars.damagedealt, vars.selfdamage, vars.healingreceived, vars.enemies,
        vars.criticalcount, vars.criticalluck, vars.hitcount, vars.enemydamaged, vars.enemydamaget, vars.match_timings,
        vars.spawn_timings) = parse.parse_file(vars.file_cube, vars.player_numbers, vars.match_timings, vars.spawn_timings)
        # DEBUG END
        '''
        self.file_select_frame.add_files()
        self.window.mainloop()
