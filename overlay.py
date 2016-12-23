# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import mtTkinter as tk
from PIL import ImageTk, Image
import ttk
import tkMessageBox
# General imports
import os
import getpass
import sys
# Own modules
import vars
import statistics

class splash_screen(tk.Toplevel):
    def __init__(self, window, boot=False):
        tk.Toplevel.__init__(self, window)
        self.label = ttk.Label(self, text = "Working...")
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
        if sys.platform == "win32":
            with open('C:/Users/' + getpass.getuser() + "/AppData/Local/SWTOR/swtor/settings/client_settings.ini", "r") as swtor:
                if "D3DFullScreen = true" in swtor:
                    tkMessageBox.showerror("Error", "The overlay cannot be shown with the current SWTOR settings. Please set SWTOR to Fullscreen (windowed) in the Graphics settings.")
        if vars.set_obj.pos == "TL":
            pos_c = "+0+0"
        elif vars.set_obj.pos == "BL":
            pos_c = "+0+" + str(vars.screen_h - 60)
        elif vars.set_obj.pos == "TR":
            if vars.set_obj.size == "big":
                pos_c = "+" + str(vars.screen_w - 200) + "+0"
            elif vars.set_obj.size == "small":
                pos_c = "+" + str(vars.screen_w - 80) + "+0"
        elif vars.set_obj.pos == "BR":
            if vars.set_obj.size == "big":
                pos_c = "+" + str(vars.screen_w - 200) + "+" + str(vars.screen_h - 60)
            elif vars.set_obj.size == "small":
                pos_c = "+" + str(vars.screen_w - 80) + "+" + str(vars.screen_h - 60)
        else:
            self.destroy()
            raise ValueError("vars.set_obj.pos not valid")
        self.attributes("-topmost", True)
        self.attributes("-alpha", vars.set_obj.opacity)
        self.overrideredirect(True)
        if vars.set_obj.size == "big":
            self.wm_geometry("200x75" + pos_c)
            self.text_label = ttk.Label(self, text = "Damage done:\nDamage taken:\nHealing recv:\nSelfdamage:\nSpawns:", justify = tk.LEFT)
        elif vars.set_obj.size == "small":
            self.wm_geometry("80x60" + pos_c)
            self.text_label = ttk.Label(self, text = "DD:\nDT:\nHR:\nSD:", justify = tk.LEFT)
        else:
            self.destroy()
            raise ValueError("vars.set_obj.size is neither big nor small")
        self.stats_var = tk.StringVar()
        self.stats_label = ttk.Label(self, textvariable = self.stats_var, justify = tk.RIGHT)
        # self.stats_label.config(font=("Courier", 44))
        self.text_label.pack(side=tk.LEFT)
        self.stats_label.pack(side=tk.RIGHT)
        self.stats_label.configure(background = "white", font = ("Calibri", 10), foreground = "yellow")
        self.text_label.configure(background = "white", font = ("Calibri", 10), foreground = "yellow")
        self.configure(background = "white")
        self.wm_attributes("-transparentcolor", "white")

    colors = ["white", "blue", "black", "green", "yellow", "red"]

class privacy(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        privacy = vars.client_obj.get_privacy()
        privacy_listbox = tk.Listbox(self, height = 10, width = 30)
        privacy_listbox.pack(side=tk.LEFT)
        privacy_scroll = ttk.Scrollbar(self, orient = tk.VERTICAL, command = privacy_listbox.yview)
        privacy_listbox.config(yscrollcommand=privacy_scroll.set)
        if privacy == -1:
            self.destroy()
            return
        try:
            privacy_list = list(privacy)
        except:
            tkMessageBox.showerror("Error", "Data in privacy statement received is not valid.")
            return
        index = 0
        for line in privacy_list:
            privacy_listbox.insert(0, line)
            index += 1

class boot_splash(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        print vars.set_obj.logo_color
        try:
            self.logo = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\assets\\logo_" + vars.set_obj.logo_color + ".png"))
            self.panel = ttk.Label(self, image = self.logo)
            self.panel.pack()
        except:
            print "[DEBUG] No logo.png found in the home folder."
        self.window = window
        self.label_var = tk.StringVar()
        self.label_var.set("Connecting to specified server...")
        self.label = ttk.Label(self, textvariable = self.label_var)
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient = "horizontal", length = 462, mode = "determinate")
        self.progress_bar.pack()
        directory = os.listdir(window.default_path)
        files = []
        for file in directory:
            if file.endswith(".txt"):
                files.append(file)
        vars.files_done = 0
        self.amount_files = len(files)
        '''
        if self.amount_files >= 50:
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombadwLogs folder. You may want to archive some of your %s CombatLogs in order to speed up the parsing program and the startup times." % self.amount_files)
        '''
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()
        self.done = False

    def update_progress(self):
        print "[DEBUG] update_progress called"
        if vars.files_done != self.amount_files:
            self.label_var.set("Parsing the files...")
            self.progress_bar["value"] = vars.files_done
            self.update()
        else:
            return

class conn_splash(tk.Toplevel):
    def __init__(self, window=vars.main_window):
        tk.Toplevel.__init__(self, window)
        self.window = window
        self.FLAG = False
        self.label = ttk.Label(self, text = "Connecting to specified server...")
        self.label.pack()
        self.conn_bar =  ttk.Progressbar(self, orient = "horizontal", length = 300, mode = "indeterminate")
        self.conn_bar.pack()
        self.window.after(500, self.connect)

    def connect(self):
        if not self.FLAG:
            self.update()
            self.window.after(500, self.connect)
        else:
            return


class events_view(tk.Toplevel):
    def __init__(self, window, spawn, player):
        tk.Toplevel.__init__(self, window)
        self.listbox = tk.Listbox(self, width=105, height=15, font=("Consolas", 10))
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command =self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.grid(column = 1, row = 0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.scroll.grid(column = 2, row = 0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.resizable(width = False, height = False)
        try:
            for line in spawn:
                self.listbox.insert(tk.END, statistics.print_event(line, vars.spawn_timing, player))
        except TypeError:
            self.destroy()



