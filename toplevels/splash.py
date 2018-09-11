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
# Project Modules
from utils import directories
from utils import utilities


class SplashScreen(tk.Toplevel):
    """Simple splash screen to show progress while loading files"""
    def __init__(self, window, amount, title="GSF Parser", text="Working..."):
        """
        :param window: GSF Parser MainWindow (tk.Tk)
        :param amount: Amount of files that need results
        :param title: Window Manager Title
        """
        tk.Toplevel.__init__(self, window)
        self.update()
        self.grab_set()  # Override clicks on MainWindow
        self.title(title)
        # Widget creation
        self.label = ttk.Label(self, text=text)
        self.label.pack()
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()
        self.progress_bar["maximum"] = amount
        self.progress_bar["value"] = 0
        self.update()

    def update_max(self, number):
        """Update ProgressBar indicator with number of file parsed"""
        self.progress_bar["value"] = number
        self.update()

    def increment(self):
        """Increment the progress of the Progressbar by one"""
        self.progress_bar["value"] += 1
        self.update()


class BootSplash(tk.Toplevel):
    """Simple splash screen for starting GSF Parser with logo"""

    def __init__(self, window):
        """
        :param window: GSF Parser MainWindow
        """
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Starting...")
        # Icon
        self.logo = utilities.open_icon("logo_green.png", folder="logos")
        self.panel = ttk.Label(self, image=self.logo)
        self.panel.pack()
        # Progress indication label
        self.label_var = tk.StringVar()
        self.label_var.set("Building widgets...")
        self.label = ttk.Label(self, textvariable=self.label_var)
        self.label.pack()
        # Progress Bar (indicates parsed files)
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=462, mode="determinate")
        self.progress_bar.pack()
        self.update_geometry()
        self.update()

    def update_max(self, amount):
        """Update amount of files parsed for ProgressBar"""
        self.label_var.set("Parsing files...")
        self.progress_bar["maximum"] = amount
        self.progress_bar.update_idletasks()

    def increment(self):
        """Increment the progress of Progressbar by one"""
        self.progress_bar["value"] += 1
        self.progress_bar.update_idletasks()

    def update_geometry(self):
        """Move to the middle of Monitor 0"""
        screen_res = utilities.get_screen_resolution()
        self.update()
        req_size = (self.winfo_width(), self.winfo_height())
        self.wm_geometry("+{0}+{1}".format(
            int((screen_res[0] - req_size[0]) / 2), int((screen_res[1] - req_size[1]) / 2)))


class DiscordSplash(tk.Toplevel):
    """SplashScreen with indeterminate progress indicator for Discord"""

    def __init__(self, master: tk.Tk):
        """Initialize the Toplevel with image"""
        self.path = os.path.join(directories.get_assets_directory(), "gui", "loading32.gif")
        self.index = 0
        tk.Toplevel.__init__(self, master)
        self.wm_overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.image_label = ttk.Label(self)
        self.update_state()
        self.text_label = ttk.Label(self, text="Synchronizing with the Discord Bot Server...")
        self.grid_widgets()
        self.update_geometry()

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
        self.image_label.grid(row=0, column=0, padx=5, pady=5)
        self.text_label.grid(row=0, column=1, padx=(0, 5), pady=5)

    def update_geometry(self):
        """Move to the middle over the GSF Parser window"""
        self.update()
        req_width, req_height = self.winfo_reqwidth(), self.winfo_reqheight()
        master_width, master_height = self.master.winfo_width(), self.master.winfo_height()
        master_x, master_y = self.master.winfo_x(), self.master.winfo_y()
        middle_x, middle_y = map(int, (master_x + 0.5 * master_width, master_y + 0.5 * master_height))
        x, y = map(int, (middle_x - 0.5 * req_width, middle_y - 0.5 * req_height))
        self.wm_geometry("{}x{}+{}+{}".format(req_width, req_height, x, y))

    def update_state(self):
        """Update the GIF animation of the image"""
        image = tk.PhotoImage(master=self, file=self.path, format="gif -index {}".format(self.index))
        self.index += 1
        if self.index == 20:
            self.index = 0
        self.image_label.configure(image=image)
        self.update_geometry()
        self.update()
