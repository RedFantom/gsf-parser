"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard library
from datetime import datetime
import os
import sys
# UI Libraries
from ttkthemes import ThemedTk
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
# Frames
from frames import FileFrame, GraphsFrame, \
    SettingsFrame, RealTimeFrame, BuildsFrame, CharactersFrame, ShipFrame, \
    StatsFrame, StrategiesFrame, ToolsFrame, ChatFrame
# Widgets
from ttkwidgets import DebugWindow
from toplevels.splash import BootSplash
# Project Modules
from network.discord import DiscordClient
from utils.directories import get_temp_directory, get_assets_directory
from utils.update import check_update
from variables import settings
import variables
# Packages
from mss import mss
from PIL import Image
from PIL.ImageTk import PhotoImage
from pypresence import Presence
from raven import Client as RavenClient


class MainWindow(ThemedTk):
    """
    Child class of tk.Tk that creates the main windows of the parser.
    Creates all frames that are necessary for the various functions of
    the parser and provides exit-handling.
    """

    def __init__(self, raven: RavenClient):
        self.raven = variables.raven = raven
        self.width = 800 if sys.platform != "linux" else 825
        self.height = 425 if sys.platform != "linux" else 450
        # Initialize window
        ThemedTk.__init__(self, gif_override=True)
        self.set_attributes()
        self.update_scaling()
        self.open_debug_window()
        self.finished = False
        variables.main_window = self
        self.style = ttk.Style()
        self.set_icon()
        self.set_variables()
        self.update_style()
        self.discord = DiscordClient()
        # Get the default path for CombatLogs and the Installation path
        self.default_path = variables.settings["parsing"]["path"]
        # Set window properties and create a splash screen from the splash_screen class
        self.withdraw()
        self.splash = BootSplash(self)
        self.splash.label_var.set("Building widgets...")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        # Add a notebook widget with various tabs for the various functions
        self.notebook = ttk.Notebook(self, height=420, width=self.width)
        self.file_tab_frame = ttk.Frame(self.notebook)
        self.realtime_tab_frame = ttk.Frame(self.notebook)
        self.settings_tab_frame = ttk.Frame(self.notebook)
        self.characters_frame = CharactersFrame(self.notebook, self)
        self.file_select_frame = FileFrame(self.file_tab_frame, self)
        self.middle_frame = StatsFrame(self.file_tab_frame, self)
        self.ship_frame = ShipFrame(self.middle_frame.notebook)
        self.middle_frame.notebook.add(self.ship_frame, text="Ship")
        self.realtime_frame = RealTimeFrame(self.realtime_tab_frame, self)
        self.settings_frame = SettingsFrame(self.settings_tab_frame, self)
        self.graphs_frame = GraphsFrame(self.notebook, self)
        self.builds_frame = BuildsFrame(self.notebook, self)
        self.toolsframe = ToolsFrame(self.notebook)
        self.strategies_frame = StrategiesFrame(self.notebook)
        self.chat_frame = ChatFrame(self.notebook, self)
        # Pack the frames and put their widgets into place
        self.grid_widgets()
        self.child_grid_widgets()
        # Add the frames to the Notebook
        self.setup_notebook()
        # Update the files in the file_select frame
        self.splash.label_var.set("Parsing files...")
        self.notebook.grid(column=0, row=0, padx=2, pady=2)
        if not os.path.exists("development"):
            self.file_select_frame.add_files(silent=True)
        self.settings_frame.update_settings()
        # Check for updates
        self.splash.label_var.set("Checking for updates...")
        self.update()
        check_update()
        # Synchronize with Discord Bot Server
        if settings["sharing"]["enabled"] is True:
            self.splash.label_var.set("Synchronizing with Discord Bot Server...")
            self.update()
            self.discord.send_files(self)
        # Discord Rich Presence
        if settings["realtime"]["drp"] is True:
            self.rpc = Presence(436173115064713216)
            try:
                self.rpc.connect()
            except Exception:
                messagebox.showwarning("Error", "Discord Rich Presence failed to connect.")
                self.rpc = None
        else:
            self.rpc = None
        self.update_presence()
        # Give focus to the main window
        self.deiconify()
        self.finished = True
        self.splash.destroy()
        self.splash = None
        # Mainloop start (main.py)

    def update_presence(self):
        """Update to the basic GSF Parser presence"""
        if self.rpc is None:
            return
        assert isinstance(self.rpc, Presence)
        self.rpc.update(state="Not real-time parsing", large_image="logo_green_png")

    def grid_widgets(self):
        """Grid all widgets in the frames"""
        self.file_select_frame.grid(column=1, row=1, sticky="nswe")
        self.middle_frame.grid(column=2, row=1, sticky="nswe", padx=5, pady=5)
        self.realtime_frame.grid()
        self.settings_frame.grid()
        self.graphs_frame.grid(column=0, row=0)

    def child_grid_widgets(self):
        """Configure the child widgets of the Frames in grid geometry"""
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
        """Add all created frames to the notebook widget"""
        self.notebook.add(self.file_tab_frame, text="File parsing")
        self.notebook.add(self.realtime_tab_frame, text="Real-time parsing")
        self.notebook.add(self.chat_frame, text="Chat Logger")
        self.notebook.add(self.characters_frame, text="Characters")
        self.notebook.add(self.builds_frame, text="Builds")
        self.notebook.add(self.graphs_frame, text="Graphs")
        self.notebook.add(self.strategies_frame, text="Strategies")
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
        """Set program global variables in the shared variables module"""
        variables.colors.set_scheme(variables.settings["gui"]["event_scheme"])

    def get_scaling_factor(self):
        """Return the DPI scaling factor (float)"""
        return self.winfo_pixels("1i") / 72.0

    def get_window_size(self):
        """Return the window size, taking scaling into account"""
        factor = self.winfo_pixels("1i") / 96.0
        size_x = int(self.width * factor)
        size_y = int(self.height * factor)
        return size_x, size_y

    def update_scaling(self):
        """Update the DPI scaling of the child widgets of the window"""
        self.tk.call('tk', 'scaling', '-displayof', '.', self.get_scaling_factor())

    def open_debug_window(self):
        """Open a DebugWindow instance if that setting is set to True"""
        if variables.settings["gui"]["debug"] is True:
            DebugWindow(self, title="GSF Parser Debug Window", stdout=True, stderr=True)
        return

    def update_style(self):
        """
        Update the style of the window. This includes theme and text
        colour, but also font.
        """
        print("[MainWindow] PNG-based theme: {}".format(self.png_support))
        self.set_theme("arc")
        print("[MainWindow] ThemedWidget Version: {}".format(getattr(self, "VERSION", None)))
        self.style.configure('.', font=("Calibri", 10))
        self.style.configure('TButton', anchor="w")
        self.style.configure('Toolbutton', anchor="w")
        self.style.configure('.', foreground=settings["gui"]["color"])
        self.setup_tk_toplevel_hooks()

    def setup_tk_toplevel_hooks(self):
        """Change the default background color of Tk and Toplevel"""
        color = self.style.lookup("TFrame", "background")
        self.config(background=color)
        __init__original = tk.Toplevel.__init__

        def __init__toplevel(*args, **kwargs):
            kwargs.setdefault("background", color)
            __init__original(*args, **kwargs)

        tk.Toplevel.__init__ = __init__toplevel

    def set_icon(self):
        """Changes the window's icon"""
        icon_path = os.path.join(get_assets_directory(), "logos", "icon_green.ico")
        icon = PhotoImage(Image.open(icon_path))
        self.tk.call("wm", "iconphoto", self._w, icon)

    def exit(self):
        """
        Function to cancel any running tasks and call any functions to
        save the data in use before actually closing the
        GSF Parser
        :return: SystemExit(0)
        """
        if self.destroy():
            sys.exit()

    def screenshot(self, *args):
        """Take a screenshot of the GSF Parser window and save"""
        x = self.winfo_x()
        y = self.winfo_y()
        result_box = (x, y, self.winfo_reqwidth() + x + 13, self.winfo_reqheight() + y + 15)
        file_name = os.path.join(
            get_temp_directory(),
            "screenshot_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png")
        with mss() as sct:
            image = sct.grab(result_box)
        image = Image.frombytes("RGB", image.size, image.rgb)
        image.save(file_name)

    def destroy(self):
        """
        Destroy the MainWindow after checking for running processes

        Destroying the MainWindow is not allowed while connected to a
        Strategy Server or running one, the user will have to exit the
        server first.
        """
        if self.strategies_frame.settings is not None:
            if self.strategies_frame.settings.server:
                messagebox.showerror("Error", "You cannot exit the GSF Parser while running a Strategy Server.")
                return False
            if self.strategies_frame.settings.client:
                messagebox.showerror("Error", "You cannot exit the GSF Parser while connected to a Strategy Server.")
                return False
            self.strategies_frame.settings.destroy()
        if self.realtime_frame.parser is not None:
            if self.realtime_frame.parser.is_alive():
                self.realtime_frame.stop_parsing()
        ThemedTk.destroy(self)
        if self.rpc is not None:
            self.rpc.update()
            self.rpc.close()
        return True

    def report_callback_exception(self, exc, val, tb):
        """Redirect Exceptions in the mainloop to RavenClient"""
        if not os.path.exists("development"):
            self.raven.captureException()
        ThemedTk.report_callback_exception(self, exc, val, tb)
