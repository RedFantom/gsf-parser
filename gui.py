# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
from ttkthemes import ThemedTk
import tkinter.ttk as ttk
from tkinter import messagebox
import os
import variables
from tools import client
import main
import socket
from frames import fileframe, resourcesframe, sharingframe, graphsframe, toolsframe
from frames import settingsframe, realtimeframe, buildframe, charactersframe
from frames import shipframe, statsframe
from frames.strategiesframe import StrategiesFrame
from toplevels.splashscreens import BootSplash
import pyscreenshot
from tools.utilities import get_temp_directory
from datetime import datetime
from sys import exit
from github import Github, GithubException
from semantic_version import Version
from toplevels.update import UpdateWindow
from widgets.debugwindow import DebugWindow


# Class that contains all code to start the parser
# Creates various frames and gets all widgets into place
# Main loop is started at the end
class MainWindow(ThemedTk):
    """
    Child class of tk.Tk that creates the main windows of the parser. Creates all frames that are necessary for the
    various functions of the parser an
    """

    def __init__(self):
        # Initialize window
        ThemedTk.__init__(self)
        self.set_attributes()
        self.update_scaling()
        self.open_debug_window()
        self.finished = False
        variables.main_window = self
        self.style = ttk.Style()
        self.set_icon()
        self.set_variables()
        self.update_style(start=True)
        # Get the default path for CombatLogs and the Installation path
        self.default_path = variables.settings_obj["parsing"]["cl_path"]
        # Set window properties and create a splash screen from the splash_screen class
        self.withdraw()
        variables.client_obj = client.ClientConnection()
        self.splash = BootSplash(self)
        # TODO Enable connecting to the server in a later phase
        if variables.settings_obj["sharing"]["auto_upl"] or variables.settings_obj["parsing"]["auto_ident"]:
            variables.client_obj.init_conn()
            print("[DEBUG] Connection initialized")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        # Add a notebook widget with various tabs for the various functions
        self.notebook = ttk.Notebook(self, height=420, width=800)
        self.file_tab_frame = ttk.Frame(self.notebook)
        self.realtime_tab_frame = ttk.Frame(self.notebook)
        self.share_tab_frame = sharingframe.SharingFrame(self.notebook)
        self.settings_tab_frame = ttk.Frame(self.notebook)
        self.file_select_frame = fileframe.FileFrame(self.file_tab_frame, self)
        self.middle_frame = statsframe.StatsFrame(self.file_tab_frame, self)
        self.ship_frame = shipframe.ShipFrame(self.middle_frame.notebook)
        self.middle_frame.notebook.add(self.ship_frame, text="Ship")
        self.realtime_frame = realtimeframe.RealtimeFrame(self.realtime_tab_frame, self)
        self.settings_frame = settingsframe.SettingsFrame(self.settings_tab_frame, self)
        self.graphs_frame = graphsframe.GraphsFrame(self.notebook, self)
        self.resources_frame = resourcesframe.ResourcesFrame(self.notebook, self)
        self.characters_frame = charactersframe.CharactersFrame(self.notebook)
        self.builds_frame = buildframe.BuildsFrame(self.notebook)
        self.toolsframe = toolsframe.ToolsFrame(self.notebook)
        self.strategies_frame = StrategiesFrame(self.notebook)
        # Pack the frames and put their widgets into place
        self.grid_widgets()
        self.child_grid_widgets()
        # Add the frames to the Notebook
        self.setup_notebook()
        # Update the files in the file_select frame
        self.notebook.grid(column=0, row=0)
        self.file_select_frame.add_files(silent=True)
        self.settings_frame.update_settings()
        # Check for updates
        self.splash.label_var.set("Checking for updates...")
        self.update()
        self.check_update()
        # Give focus to the main window
        self.deiconify()
        self.finished = True
        self.splash.destroy()
        # Start the main loop

    def grid_widgets(self):
        """
        Grid all widgets in the frames
        """
        self.file_select_frame.grid(column=1, row=1, sticky="nswe")
        self.middle_frame.grid(column=2, row=1, sticky="nswe", padx=5, pady=5)
        self.realtime_frame.grid()
        # self.ship_frame.grid(column=3, row=1, sticky="nswe")
        self.settings_frame.grid()
        self.graphs_frame.grid(column=0, row=0)

    def child_grid_widgets(self):
        """
        Call grid_widgets on all child widgets that must contain widgets
        """
        self.file_select_frame.grid_widgets()
        self.middle_frame.grid_widgets()
        self.realtime_frame.grid_widgets()
        self.ship_frame.grid_widgets()
        self.settings_frame.grid_widgets()
        self.graphs_frame.grid_widgets()
        self.builds_frame.grid_widgets()
        self.characters_frame.grid_widgets()
        self.toolsframe.grid_widgets()
        self.file_select_frame.clear_data_widgets()
        self.strategies_frame.grid_widgets()

    def setup_notebook(self):
        """
        Add all created frames to the notebook widget
        """
        self.notebook.add(self.file_tab_frame, text="File parsing")
        self.notebook.add(self.realtime_tab_frame, text="Real-time parsing")
        self.notebook.add(self.characters_frame, text="Characters")
        self.notebook.add(self.builds_frame, text="Builds")
        self.notebook.add(self.graphs_frame, text="Graphs")
        self.notebook.add(self.strategies_frame, text="Strategies")
        self.notebook.add(self.share_tab_frame, text="Sharing")
        self.notebook.add(self.resources_frame, text="Resources")
        self.notebook.add(self.toolsframe, text="Tools")
        self.notebook.add(self.settings_tab_frame, text="Settings")

    def set_attributes(self):
        """
        Setup various window attributes:
        - Resizability
        - Window title
        - WM_DELETE_WINDOW redirect
        - DPI scaling
        - Screenshot functionality
        """
        self.resizable(width=False, height=False)
        self.wm_title("GSF Parser")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.geometry("{}x{}".format(*self.get_window_size()))
        self.bind("<F10>", self.screenshot)

    def set_variables(self):
        """
        Set program global variables in the shared variables module
        """
        variables.color_scheme.set_scheme(variables.settings_obj["gui"]["event_scheme"])
        # Get the screen properties
        variables.screen_w = self.winfo_screenwidth()
        variables.screen_h = self.winfo_screenheight()
        variables.path = variables.settings_obj["parsing"]["cl_path"]

    def get_scaling_factor(self):
        """
        Return the DPI scaling factor (float)
        """
        return self.winfo_pixels("1i") / 72.0

    def get_window_size(self):
        """
        Return the window size, taking scaling into account
        """
        factor = self.winfo_pixels("1i") / 96.0
        size_x = int(800 * factor)
        size_y = int(425 * factor)
        return size_x, size_y

    def update_scaling(self):
        """
        Update the DPI scaling of the child widgets of the window
        """
        self.tk.call('tk', 'scaling', '-displayof', '.', self.get_scaling_factor())

    def open_debug_window(self):
        """
        Open a DebugWindow instance if that setting is set to True
        """
        if variables.settings_obj["gui"]["debug"] is True:
            DebugWindow(self, title="GSF Parser Debug Window", stdout=True, stderr=True)
        return

    def update_style(self, start=False):
        """
        Update the style of the window. This includes theme and text colour, but also font.
        :param start: If True, no new window is created. if set to True and the window is already running, then
                      TclErrors will be generated by external functions.
        :return: None
        """
        self.set_theme("arc")
        self.style.configure('.', font=("Calibri", 10))
        self.style.configure('TButton', anchor="w")
        self.style.configure('Toolbutton', anchor="w")
        try:
            self.style.configure('.', foreground=variables.settings_obj["gui"]["color"])
        except KeyError:
            self.style.configure('.', foreground='#2f77d0')
        if not start:
            self.destroy()
            main.new_window()

    def set_icon(self):
        """
        Changes the window's icon
        """
        self.iconbitmap(default=os.path.dirname(os.path.realpath(__file__)) + "\\assets\\logos\\icon_" +
                                variables.settings_obj["gui"]["logo_color"] + ".ico")

    def exit(self):
        """
        Function to cancel any running tasks and call any functions to save the data in use before actually closing the
        GSF Parser
        :return: SystemExit(0)
        """
        if self.destroy():
            exit()

    def screenshot(self, *args):
        """
        Take a screenshot of the GSF Parser window and save, only works on Windows
        :return: None
        """
        x = self.winfo_x()
        y = self.winfo_y()
        result_box = (x, y, self.winfo_reqwidth() + x + 13, self.winfo_reqheight() + y + 15)
        screenshot = pyscreenshot.grab(result_box)
        file_name = os.path.join(get_temp_directory(), "screenshot_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +
                                 ".png")
        screenshot.save(file_name, "PNG")

    def check_update(self):
        """
        Function to check for GSF Parser updates by checking tags and opening a window if an update is available
        :return: None
        """
        if not variables.settings_obj["misc"]["autoupdate"]:
            return
        try:
            user = Github().get_user("RedFantom")
            repo = user.get_repo("GSF-Parser")
            current = Version(variables.settings_obj["misc"]["version"].replace("v", ""))
            for item in repo.get_tags():
                try:
                    if Version(item.name.replace("v", "")) > current:
                        UpdateWindow(self, item.name)
                        break
                    elif Version(item.name.replace("v", "")) < current:
                        # The newest tags come first in the loop
                        # If the tag is older than the current version, an update isn't needed
                        # The loop is stopped to preserve the rate limit
                        break
                except ValueError as e:
                    print(e)
                    continue
        except (GithubException, socket.timeout, socket.error):
            pass

    def destroy(self):
        if self.strategies_frame.settings:
            if self.strategies_frame.settings.server:
                messagebox.showerror("Error", "You cannot exit the GSF Parser while running a Strategy Server.")
                return False
            if self.strategies_frame.settings.client:
                messagebox.showerror("Error", "You cannot exit the GSF Parser while connected to a Strategy Server.")
                return False
            self.strategies_frame.settings.destroy()
        ThemedTk.destroy(self)
        return True
