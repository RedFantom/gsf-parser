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
import statistics
import frames

class main_window:
    def __init__(self):
        self.window = tk.Tk()
        self.window.resizable(width = False, height = False)
        self.window.geometry("{}x{}".format(800, 425))
        self.window.wm_title("Thranta Squadron GSF Parser")
        self.default_path = 'C:/Users/' + getpass.getuser() + "/Documents/Star Wars - The Old Republic/CombatLogs"
        self.install_path = os.getcwd()
        # Add a self.notebook widget to the self.window and add its tabs
        self.notebook = ttk.Notebook(self.window, height = 400, width = 800)
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
        self.ship_containment_frame = ttk.Frame(self.file_tab_frame, width = 300, height = 400)
        self.ship_containment_frame.pack(side = tk.RIGHT)
        self.ship_frame = frames.ship_frame(self.ship_containment_frame)
        self.ship_frame.pack(side = tk.RIGHT)
        self.notebook.add(self.file_tab_frame, text = "File parsing")
        self.notebook.add(self.realtime_tab_frame, text = "Real-time parsing")
        self.notebook.add(self.share_tab_frame, text = "Sharing and Leaderboards")
        self.notebook.add(self.settings_tab_frame, text = "Settings")
        self.settings_frame = frames.settings_frame(self.settings_tab_frame, self)
        self.settings_frame.grid_widgets()
        # self.notebook.add(alliesTab, text = "Allies")
        self.notebook.grid(column = 0, row = 0)


        self.file_select_frame.add_files()
        self.window.mainloop()
