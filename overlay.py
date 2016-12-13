# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
import tkMessageBox
# General imports
import os
import getpass
# Own modules
import vars
import frames
import main

class splash_screen(tk.Toplevel):
    def __init__(self, window, boot=False):
        tk.Toplevel.__init__(self, window)
        with open('C:/Users/' + getpass.getuser() + "/AppData/Local/SWTOR/swtor/settings/client_settings.ini", "r") as swtor:
            if "D3DFullScreen = true" in swtor:
                tkMessageBox.showerror("Error", "The overlay cannot be shown with the current SWTOR settings. Please set SWTOR to Fullscreen (windowed) in the Grapichs settings.")
        self.label = tk.Label(self, text = "Working...")
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient = "horizontal", length = 300, mode = "determinate")
        self.progress_bar.pack()
        try:
            list = os.listdir(window.default_path)
        except:
            print "[DEBUG] Running on UNIX, functionality disabled"
            return
        files = []
        for file in list:
            if file.endswith(".txt"):
                files.append(file)
        vars.files_done = 0
        self.amount_files = len(files)
        if(self.amount_files >= 50 and boot):
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombatLogs folder. You may want to archive some of your %s CombatLogs in order to speed up the parsing program and the startup times." % self.amount_files)
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self):
        self.progress_bar["value"] = vars.files_done
        self.update()

class overlay(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        if main.set_obj.pos == "TL":
            pos_c = "+0+0"
        elif main.set_obj.pos == "BL":
            pos_c = "+0+" + str(vars.screen_h - 75)
        elif main.set_obj.pos == "TR":
            if main.set_obj.size == "big":
                pos_c = "+" + str(vars.screen_w - 200) + "+0"
            elif main.set_obj.size == "small":
                pos_c = "+" + str(vars.screen_w - 100) + "+0"
        elif main.set_obj.pos == "BR":
            if main.set_obj.size == "big":
                pos_c = "+" + str(vars.screen_w - 200) + "+" + str(vars.screen_h - 75)
            elif main.set_obj.size == "small":
                pos_c = "+" + str(vars.screen_w - 100) + "+" + str(vars.screen_h - 75)
        else:
            raise ValueError("main.set_obj.pos not valid")
            self.destroy()
            return
        self.attributes("-topmost", True)
        self.attributes("-alpha", main.set_obj.opacity)
        self.overrideredirect(True)                        
        if main.set_obj.size == "big":
            self.wm_geometry("200x75" + pos_c)
            self.text_label = tk.Label(self, text = "Damage done:\nDamage taken:\nHealing recv:\nSelfdamage:\n", justify = tk.LEFT)
        elif main.set_obj.size == "small":
            self.wm_geometry("100x75" + pos_c)
            self.text_label = tk.Label(self, text = "DD:\nDT:\nHR:\nSD:\n", justify = tk.LEFT)
        else:
            raise ValueError("main.set_obj.size is neither big nor small")
            return
        self.stats_var = tk.StringVar()
        self.stats_label = tk.Label(self, textvariable = self.stats_var, justify = tk.RIGHT)
        # self.stats_label.config(font=("Courier", 44))
        self.text_label.pack(side=tk.LEFT)
        self.stats_label.pack(side=tk.RIGHT)

    def set_position(self, pos):
        pass

class privacy(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
