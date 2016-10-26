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
import glob
import os
import getpass
from datetime import datetime
# Own modules
import vars
import parse
import client
import statistics
import getpass


# Class for the _frame in the fileTab of the parser
class file_frame(ttk.Frame):
    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame, width = 200, height = 400)
        self.main_window = main_window
        self.file_box = tk.Listbox(self)
        self.file_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.file_box_scroll.config(command = self.file_box.yview)
        self.file_box.config(yscrollcommand = self.file_box_scroll.set)
        self.match_box = tk.Listbox(self)
        self.match_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.match_box_scroll.config(command = self.match_box.yview)
        self.match_box.config(yscrollcommand = self.match_box_scroll.set)
        self.spawn_box = tk.Listbox(self)
        self.spawn_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.spawn_box.yview)
        self.spawn_box.config(yscrollcommand = self.spawn_box_scroll.set)
        self.file_box.bind("<Double-Button-1>", self.file_update)
        self.match_box.bind("<Double-Button-1>", self.match_update)
        self.spawn_box.bind("<Double-Button-1>", self.spawn_update)
        self.statistics_object = statistics.statistics()

    def grid_widgets(self):
        self.file_box.config(height = 7)
        self.match_box.config(height = 7)
        self.spawn_box.config(height = 7)
        self.file_box.grid(column = 0, row = 0, columnspan = 2, padx = 5, pady = 5)
        self.file_box_scroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.match_box.grid(column = 0, row =8, columnspan = 2, padx = 5, pady = 5)
        self.match_box_scroll.grid(column = 2, row = 8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.spawn_box.grid(column = 0, row = 16, columnspan = 2, padx = 5, pady = 5)
        self.spawn_box_scroll.grid(column = 2, row = 16, columnspan = 1, sticky = tk.N + tk.S, pady = 5)

    def add_matches(self):
        self.match_timing_strings = []
        self.match_timing_strings = [str(time.time()) for time in vars.match_timings]
        self.match_timing_strings = self.match_timing_strings[::2]
        '''
        for number in range(0, len(self.match_timing_strings) + 1):
            self.match_box.delete(number)
        '''
        self.match_box.delete(0, tk.END)
        self.match_box.insert(tk.END, "All matches")
        if len(self.match_timing_strings) == 0:
            self.match_box.delete(0, tk.END)
            self.add_spawns()
        else:
            for time in self.match_timing_strings:
                self.match_box.insert(tk.END, time)

    def add_spawns(self):
        self.spawn_timing_strings = []
        if vars.match_timing != None:
            try:
                index = self.match_timing_strings.index(vars.match_timing)
            except:
                self.spawn_box.delete(0, tk.END)
                return
            self.spawn_box.delete(0, tk.END)
            self.spawn_box.insert(tk.END, "All spawns")
            for spawn in vars.spawn_timings[index]:
                self.spawn_timing_strings.append(str(spawn.time()))
            for spawn in self.spawn_timing_strings:
                self.spawn_box.insert(tk.END, spawn)

    def add_files(self):
        self.file_strings = []
        os.chdir(self.main_window.default_path)
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                self.file_strings.append(file)
        self.file_box.delete(0, tk.END)
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            if statistics.check_gsf(file) == True:
                self.file_box.insert(tk.END, file[7:-14])

    def file_update(self, instance):
        if self.file_box.curselection() == (0,):
            print "[DEBUG] All CombatLogs selected"
        else:
            # Find the file name of the file selected in the list of file names
            numbers = self.file_box.curselection()
            vars.file_name = self.file_strings[numbers[0] - 1]
            # Open that file in read-Universal mode. normal read and read-binary have the same results (Issue #7)
            clicked_file = open(vars.file_name, "rU")
            # Read all the lines from the selected file
            lines = clicked_file.readlines()
            for line in lines:
                # Print all the lines in the file for debugging purposes
                print "[DEBUG] ", line.replace("\n", "")
            # Print the amount of lines read for debugging purposes
            print "[DEBUG] len(lines) = ", len(lines)
            # PARSING STARTS
            # Get the player ID numbers from the list of lines
            player = parse.determinePlayer(lines)
            # Print the amount of lines again to check whether it is the same for debugging purposes
            print "[DEBUG] len(lines) = ", len(lines), "\n"
            # Parse the lines with the acquired player ID numbers
            vars.file_cube, vars.match_timings, vars.spawn_timings = parse.splitter(lines, player)
            # Close the file object
            clicked_file.close()
            # Start adding the matches from the file to the listbox
            self.add_matches()

    def match_update(self, instance):
        if self.match_box.curselection() == (0,):
            print "[DEBUG] All matches selected"
        else:
             numbers = self.match_box.curselection()
             vars.match_timing = self.match_timing_strings[numbers[0] - 1]
             self.add_spawns()    
            
    def spawn_update(self, instance):
        if self.spawn_box.curselection() == (0,):
            print "[DEBUG] All spawns selected"
        else:
            numbers = self.spawn_box.curselection()
            vars.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            match = vars.file_cube[self.match_timing_strings.index(vars.match_timing)]
            spawn = match[self.spawn_timing_strings.index(vars.spawn_timing)]
            vars.player_numbers = parse.determinePlayer(spawn)
            vars.abilities_string, vars.events_string, vars.statistics_string, vars.ships_list, vars.ships_comps, vars.enemies, vars.enemydamaged, vars.enemydamaget = self.statistics_object.spawn_statistics(spawn)
            self.main_window.middle_frame.abilities_label_var.set(vars.abilities_string)
            self.main_window.middle_frame.events_label_var.set(vars.events_string)
            self.main_window.middle_frame.statistics_numbers_var.set(vars.statistics_string)
            ships_string = "Possible ships used:\n"
            for ship in vars.ships_list:
                ships_string += str(ship) + "\n"
            ships_string += "\nWith the components:\n"
            for component in vars.ships_comps:
                ships_string += component + "\n"
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in vars.enemies:
                self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, vars.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, vars.enemydamaget[enemy])

            
class ship_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame, width = 300, height = 400)
        self.ship_label_var = tk.StringVar()
        self.ship_label = tk.Label(root_frame, textvariable = self.ship_label_var, justify = tk.LEFT, wraplength = 495)
        self.ship_label.pack(side = tk.TOP)

class middle_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.notebook = ttk.Notebook(self, width = 300, height = 375)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text = "Statistics")
        self.notebook.add(self.enemies_frame, text = "Enemies")
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt:\nDamage taken:\nSelfdamage:\nHealing received:\nHitcount:\nCriticalcount:\nCriticalluck:\n"
        self.statistics_label_var.set(string)
        self.statistics_label = tk.Label(self.stats_frame, textvariable = self.statistics_label_var, justify = tk.LEFT, wraplength = 145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = tk.Label(self.stats_frame, textvariable = self.statistics_numbers_var, justify = tk.LEFT, wraplength = 145)
        self.enemies_label = tk.Label(self.enemies_frame, text = "Name\tDamage taken\tDamage dealt\n")
        self.enemies_listbox = tk.Listbox(self.enemies_frame, width = 14, height = 20)
        self.enemies_damaget = tk.Listbox(self.enemies_frame, width = 14, height = 20)
        self.enemies_damaged = tk.Listbox(self.enemies_frame, width = 14, height = 20)
        self.enemies_scroll = tk.Scrollbar(self.enemies_frame, orient = tk.VERTICAL,)
        self.enemies_scroll.config(command = self.yview)
        self.enemies_listbox.config(yscrollcommand = self.enemies_scroll.set)
        self.enemies_damaget.config(yscrollcommand = self.enemies_scroll.set)
        self.enemies_damaged.config(yscrollcommand = self.enemies_scroll.set)
        self.events_frame = ttk.Frame(self.notebook)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.abilities_frame, text = "Abilities")
        self.notebook.add(self.events_frame, text = "Events")
        self.abilities_label_var = tk.StringVar()
        self.abilities_label = tk.Label(self.abilities_frame, textvariable = self.abilities_label_var, justify = tk.LEFT, wraplength = 295)
        self.events_label_var = tk.StringVar()
        self.events_label = tk.Label(self.events_frame, textvariable = self.events_label_var, justify = tk.LEFT, wraplength = 295)

    def yview(self, *args):
        self.enemies_listbox.yview(*args)
        self.enemies_damaged.yview(*args)
        self.enemies_damaget.yview(*args)

    def grid_widgets(self):
        self.abilities_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.events_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N + tk.W)
        self.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N + tk.W, padx = 5, pady = 5)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_label.grid(column = 0, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_numbers.grid(column = 2, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_label.grid(column = 0, row = 0, columnspan = 3)
        self.enemies_listbox.grid(column = 0, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaged.grid(column = 1, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaget.grid(column = 2, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_scroll.grid(column = 3, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)


class realtime_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class share_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class settings_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.entry_frame = ttk.Frame(root_frame)
        self.privacy_frame = ttk.Frame(root_frame)
        self.server_frame = ttk.Frame(root_frame)
        self.upload_frame = ttk.Frame(root_frame)
        self.save_frame = ttk.Frame(root_frame)
        self.license_frame = ttk.Frame(root_frame)
        self.main_window = main_window
        self.parsing_label = tk.Label(root_frame, text = "Parsing settings", justify=tk.LEFT)
        self.path_entry = tk.Entry(self.entry_frame, width=75)
        self.path_entry_label = tk.Label(self.entry_frame, text = "\tCombatLogs folder:")
        self.path_entry.insert(0, self.main_window.default_path)
        self.privacy_label = tk.Label(self.privacy_frame, text = "\tConnect to server for player identification:")
        self.privacy_var = tk.BooleanVar()
        self.privacy_select_true = tk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = True, text = "Yes")
        self.privacy_select_false = tk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = False, text = "No")
        self.sharing_label = tk.Label(root_frame, text = "Share settings", justify=tk.LEFT)
        self.server_label = tk.Label(self.server_frame, text = "\tServer for sharing:")
        self.server_address_entry = tk.Entry(self.server_frame, width=20)
        self.server_colon_label = tk.Label(self.server_frame, text = ":")
        self.server_port_entry = tk.Entry(self.server_frame, width=4)
        self.auto_upload_label = tk.Label(self.upload_frame, text="\tAuto-upload CombatLogs to the server:")
        self.auto_upload_var = tk.BooleanVar()
        self.auto_upload_true = tk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=True, text="Yes")
        self.auto_upload_false = tk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=False, text="No")
        self.save_settings_button = tk.Button(self.save_frame, text="  Save  ", command=self.save_settings)
        self.discard_settings_button = tk.Button(self.save_frame, text="Discard", command=self.discard_settings)
        self.default_settings_button = tk.Button(self.save_frame, text="Defaults", command = self.default_settings)
        self.license_button = tk.Button(self.license_frame, text="License", command=self.show_license)
        self.version_label = tk.Label(self.license_frame, text="Version 2.0")
        self.update_label_var = tk.StringVar()
        self.update_label = tk.Label(self.license_frame, textvariable=self.update_label_var) 
        self.copyright_label = tk.Label(self.license_frame, text = "Copyright (C) 2016 by RedFantom and Daethyra", justify=tk.LEFT)
        self.thanks_label = tk.Label(self.license_frame, text = "Special thanks to Nightmaregale for bèta testing", justify=tk.LEFT)
        
    def read_settings(self):
        os.chdir(main_window.install_path)
        try:
            settings_object = open("settings.ini", "rU")
        except IOError:
            return -1
        try:
            settings = settings_object.readlines()
            settings_object.close()
            split_settings = []
            for setting in settings:
                setting.split("=")
                split_settings.append(setting)
            vars.user_path = split_settings[0][1]
            vars.privacy = bool(split_settings[1][1])
            vars.server_address = split_settings[2][1]
            vars.server_port = int(split_settings[3][1])
            vars.auto_upload = bool(split_settings[4][1])
            os.chdir(user_path)
            return 0
        except IOError:
            tkMessageBox.showerror("Error", "Error reading settings file")
            settings_object.close()
            return -1
        except:
            tkMessageBox.showerror("Error", "Error in settings.ini, file exists")
            if not settings_object.closed:
                settings_object.close()
            return -1

    def write_settings(self, path, privacy, address, port, upload):
        os.chdir(self.main_window.install_path)
        try:
            settings_object = open("settings.ini", "w")
        except IOError:
            tkMessageBox.showerror("Error", "Error opening settings file for writing")
            return
        try:
            settings_object.seek(0)
            settings_object.truncate()
        except IOError:
            tkMessageBox.showerror("Error", "Error deleting contents of settings file")
            settings_object.close()
            return
        settings_object.write("user_path=" + path + "\n")
        settings_object.write("privacy=" + privacy + "\n")
        settings_object.write("server_address=" + address + "\n")
        settings_object.write("server_port=" + port + "\n")
        settings_object.write("auto_upload=" + upload + "\n")
        settings_object.close()

    def grid_widgets(self):
        self.parsing_label.grid(column=0, row=0, sticky=tk.W)
        self.path_entry_label.grid(column=0, row=0, sticky=tk.W)
        self.path_entry.grid(column=1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.entry_frame.grid(column=0, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        self.privacy_label.grid(column=0, row=0,sticky=tk.W)
        self.privacy_select_true.grid(column=1, row=0)
        self.privacy_select_false.grid(column=2, row=0)
        self.privacy_frame.grid(column=0, row=2, sticky=tk.N+tk.S+tk.W+tk.E)
        self.sharing_label.grid(column=0, row=3, sticky=tk.W)
        self.server_label.grid(column=0, row=0, sticky=tk.W)
        self.server_address_entry.grid(column=1,row=0)
        self.server_colon_label.grid(column=2,row=0)
        self.server_port_entry.grid(column=3,row=0)
        self.server_frame.grid(column=0, row=4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.auto_upload_label.grid(column=0, row=0)
        self.auto_upload_true.grid(column=1,row=0)
        self.auto_upload_false.grid(column=2,row=0)
        self.upload_frame.grid(column=0,row=5,sticky=tk.N+tk.S+tk.W+tk.E)
        self.save_settings_button.grid(column=0, row=0, padx=2)
        self.discard_settings_button.grid(column=1, row=0, padx=2)
        self.default_settings_button.grid(column=2, row=0, padx=2)
        self.save_frame.grid(column=0, row=6, sticky=tk.W)
        self.license_button.grid(column=1,row=0,sticky=tk.W, padx=5)
        self.copyright_label.grid(column=0, row=0, sticky=tk.W)
        self.update_label.grid(column=0, row=2, sticky=tk.W)
        self.thanks_label.grid(column=0,row=1, sticky=tk.W)
        self.license_frame.grid(column=0, row=7, sticky=tk.N+tk.S+tk.W+tk.E)

    def update_settings(self):
        pass

    def save_settings(self):
        pass

    def discard_settings(self):
        pass

    def default_settings(self):
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, "C:\\Users\\" + getpass.getuser() + "\\Star Wars - The Old Republic\CombatLogs")
        self.privacy_var.set(False)
        self.server_address_entry.delete(0, tk.END)
        self.server_address_entry.insert(0, "thrantasquadron.tk")
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, "83")
        self.auto_upload_var.set(False)

    def show_license(self):
        tkMessageBox.showinfo("License", "This program is licensed under the General Public License Version 3, by GNU. See LICENSE in the installation directory for more details")

    def show_privacy(self):
        pass

