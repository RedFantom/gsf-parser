# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
# Others
import os
from PIL import Image, ImageTk
# Own modules
from tools import utilities


class SplashScreen(tk.Toplevel):
    def __init__(self, window, amount, title="GSF Parser"):
        tk.Toplevel.__init__(self, window)
        self.window = window
        self.update()
        self.grab_set()
        self.title(title)
        self.label = ttk.Label(self, text="Working...")
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()
        self.progress_bar["maximum"] = amount
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self, number):
        self.progress_bar["value"] = number


class BootSplash(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Starting...")
        self.logo = ImageTk.PhotoImage(
            Image.open(os.path.join(utilities.get_assets_directory(), "logos", "logo_green.png")))
        self.panel = ttk.Label(self, image=self.logo)
        self.panel.pack()
        self.window = window
        self.label_var = tk.StringVar()
        self.label_var.set("Building widgets...")
        self.label = ttk.Label(self, textvariable=self.label_var)
        self.label.pack()
        self.amount = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=462, mode="determinate", variable=self.amount)
        self.progress_bar.pack()
        screen_res = utilities.get_screen_resolution()
        self.update()
        req_size = (self.winfo_width(), self.winfo_height())
        self.wm_geometry("+{0}+{1}".format(
            int((screen_res[0] - req_size[0]) / 2), int((screen_res[1] - req_size[1]) / 2)))
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self, amount):
        self.label_var.set("Parsing files...")
        self.amount.set(amount)
        self.progress_bar.update_idletasks()

    def update_maximum(self, maximum):
        self.progress_bar.config(maximum=maximum)
