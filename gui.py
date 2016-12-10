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
import overlay

# Class that contains all code to start the parser
# Creates various frames and gets all widgets into place
# Main loop is started at the end
class main_window(tk.Tk):
    def __init__(self):
        # Initialize window
        tk.Tk.__init__(self)
        # Get the default path for CombatLogs and the Installation path
        self.default_path = 'C:/Users/' + getpass.getuser() + "/Documents/Star Wars - The Old Republic/CombatLogs"
        self.install_path = os.getcwd()
        vars.install_path = self.install_path
        # Set window properties and create a splash screen from the splash_screen class
        self.resizable(width = False, height = False)
        self.splash = overlay.splash_screen(self)
        self.withdraw()
        self.geometry("{}x{}".format(800, 425))
        self.wm_title("Thranta Squadron GSF Parser")
        # Add a notebook widget with various tabs for the various functions
        self.notebook = ttk.Notebook(self, height = 400, width = 800)
        self.file_tab_frame = ttk.Frame(self.notebook)
        self.realtime_tab_frame = ttk.Frame(self.notebook)
        self.share_tab_frame = ttk.Frame(self.notebook)
        self.settings_tab_frame = ttk.Frame(self.notebook)
        self.file_select_frame = frames.file_frame(self.file_tab_frame, self)
        self.realtime_frame = frames.realtime_frame(self.realtime_tab_frame, self)
        self.middle_frame = frames.middle_frame(self.file_tab_frame, self)
        self.ship_containment_frame = ttk.Frame(self.file_tab_frame, width = 300, height = 400)
        self.ship_frame = frames.ship_frame(self.ship_containment_frame)
        self.settings_frame = frames.settings_frame(self.settings_tab_frame, self)
        # Pack the frames and put their widgets into place
        self.file_select_frame.pack(side = tk.LEFT)
        self.middle_frame.grid_widgets()
        self.file_select_frame.grid_widgets()
        self.middle_frame.pack(side = tk.LEFT, padx = 5)
        self.realtime_frame.pack()
        self.realtime_frame.grid_widgets()
        self.ship_containment_frame.pack(side = tk.RIGHT)
        self.ship_frame.pack(side = tk.RIGHT)
        self.settings_frame.grid_widgets()
        # Add the frames to the Notebook
        self.notebook.add(self.file_tab_frame, text = "File parsing")
        self.notebook.add(self.realtime_tab_frame, text = "Real-time parsing")
        self.notebook.add(self.share_tab_frame, text = "Sharing and Leaderboards")
        self.notebook.add(self.settings_tab_frame, text = "Settings")
        # Update the files in the file_select frame
        self.notebook.grid(column = 0, row = 0)
        self.file_select_frame.add_files()
        self.splash.destroy()
        # Give focus to the main window
        self.deiconify()
        # Start the main loopw
        self.mainloop()
