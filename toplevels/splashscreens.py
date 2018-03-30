"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
# Packages
from PIL import Image, ImageTk
# Project Modules
from utils import directories
from utils import utilities


class SplashScreen(tk.Toplevel):
    """Simple splash screen to show progress while loading files"""
    def __init__(self, window, amount, title="GSF Parser"):
        """
        :param window: GSF Parser MainWindow (tk.Tk)
        :param amount: Amount of files that need parsing
        :param title: Window Manager Title
        """
        tk.Toplevel.__init__(self, window)
        self.update()
        self.grab_set()  # Override clicks on MainWindow
        self.title(title)
        # Widget creation
        self.label = ttk.Label(self, text="Working...")
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()
        self.progress_bar["maximum"] = amount
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self, number):
        """Update ProgressBar indicator with number of file parsed"""
        self.progress_bar["value"] = number


class BootSplash(tk.Toplevel):
    """Simple splash screen for starting GSF Parser with logo"""
    def __init__(self, window):
        """
        :param window: GSF Parser MainWindow
        """
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Starting...")
        # Icon
        self.logo = ImageTk.PhotoImage(
            Image.open(os.path.join(directories.get_assets_directory(), "logos", "logo_green.png")))
        self.panel = ttk.Label(self, image=self.logo)
        self.panel.pack()
        # Progress indication label
        self.label_var = tk.StringVar()
        self.label_var.set("Building widgets...")
        self.label = ttk.Label(self, textvariable=self.label_var)
        self.label.pack()
        # Progress Bar (indicates parsed files)
        self.amount = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=462, mode="determinate", variable=self.amount)
        self.progress_bar.pack()
        # Move to middle of Monitor 1
        screen_res = utilities.get_screen_resolution()
        self.update()
        req_size = (self.winfo_width(), self.winfo_height())
        self.wm_geometry("+{0}+{1}".format(
            int((screen_res[0] - req_size[0]) / 2), int((screen_res[1] - req_size[1]) / 2)))
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self, amount):
        """Update amount of files parsed for ProgressBar"""
        self.label_var.set("Parsing files...")
        self.amount.set(amount)
        self.progress_bar.update_idletasks()

    def update_maximum(self, maximum):
        """Update the amount of files that need parsing for ProgressBar"""
        self.progress_bar.config(maximum=maximum)
