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
from datetime import datetime
# Own modules
import vars
import parse
import client
import statistics


# Class for the _frame in the fileTab of the parser
class file_frame(ttk.Frame):
    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame, width = 200, height = 600)
        self.main_window = main_window
        self.file_box = tk.Listbox(self, font = ("Arial", 11) )
        self.file_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.file_box_scroll.config(command = self.file_box.yview)
        self.file_box.config(yscrollcommand = self.file_box_scroll.set)
        self.match_box = tk.Listbox(self, font = ("Arial", 11) )
        self.match_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.match_box_scroll.config(command = self.match_box.yview)
        self.match_box.config(yscrollcommand = self.match_box_scroll.set)
        self.spawn_box = tk.Listbox(self, font = ("Arial", 11) )
        self.spawn_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.spawn_box.yview)
        self.spawn_box.config(yscrollcommand = self.spawn_box_scroll.set)
        self.file_box.bind("<Double-Button-1>", self.file_update)
        self.match_box.bind("<Double-Button-1>", self.match_update)
        self.spawn_box.bind("<Double-Button-1>", self.spawn_update)
        self.statistics_object = statistics.statistics()

    def grid_widgets(self):
        self.file_box.grid(column = 0, row = 0, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.file_box_scroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.match_box.grid(column = 0, row =8, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.match_box_scroll.grid(column = 2, row = 8, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)
        self.spawn_box.grid(column = 0, row = 16, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.spawn_box_scroll.grid(column = 2, row = 16, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)

    def add_matches(self):
        self.match_timing_strings = []
        self.match_timing_strings = [str(time.time()) for time in vars.match_timings]
        del_next = False
        self.match_timing_strings = self.match_timing_strings[::2]
        for number in range(0, len(self.match_timing_strings) + 1):
            self.match_box.delete(number)
        self.match_box.delete(0, tk.END)
        read_next = True
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
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                self.file_strings.append(file)
        self.file_box.delete(0, tk.END)
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file[7:-14])

    def file_update(self, instance):
        if self.file_box.curselection() == (0,):
            print "All CombatLogs selected"
        else:
            numbers = self.file_box.curselection()
            vars.file_name = self.file_strings[numbers[0] - 1]
            file_object = open(vars.file_name, "r")
            lines = file_object.readlines()
            player = parse.determinePlayer(lines)
            vars.file_cube, vars.match_timings, vars.spawn_timings = parse.splitter(lines, player)
            file_object.close()
            self.add_matches()          

    def match_update(self, instance):
        if self.match_box.curselection() == (0,):
            print "All matches selected"
        else:
             numbers = self.match_box.curselection()
             vars.match_timing = self.match_timing_strings[numbers[0] - 1]
             self.add_spawns()    
            
    def spawn_update(self, instance):
        if self.spawn_box.curselection() == (0,):
            print "All spawns selected"
        else:
            numbers = self.spawn_box.curselection()
            vars.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            match = vars.file_cube[self.match_timing_strings.index(vars.match_timing)]
            spawn = match[self.spawn_timing_strings.index(vars.spawn_timing)]
            vars.player_numbers = parse.determinePlayer(spawn)
            vars.abilities_string, vars.events_string, vars.enemies_string, vars.statistics_string, vars.ships_list, vars.ships_comps = self.statistics_object.spawn_statistics(spawn)
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
            self.main_window.middle_frame.enemies_label_var.set(vars.enemies_string)
            
class ship_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame, width = 500, height = 600)
        self.ship_label_var = tk.StringVar()
        self.ship_label = tk.Label(root_frame, textvariable = self.ship_label_var, justify = tk.LEFT, wraplength = 495)
        self.ship_label.pack(side = tk.TOP)

class middle_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.notebook = ttk.Notebook(self, width = 300, height = 575)
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
        self.enemies_label_var = tk.StringVar()
        self.enemies_label = tk.Label(self.enemies_frame, textvariable = self.enemies_label_var, justify = tk.LEFT, wraplength = 295)
        self.events_frame = ttk.Frame(self.notebook)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.abilities_frame, text = "Abilities")
        self.notebook.add(self.events_frame, text = "Events")
        self.abilities_label_var = tk.StringVar()
        self.abilities_label = tk.Label(self.abilities_frame, textvariable = self.abilities_label_var, justify = tk.LEFT, wraplength = 295)
        self.events_label_var = tk.StringVar()
        self.events_label = tk.Label(self.events_frame, textvariable = self.events_label_var, justify = tk.LEFT, wraplength = 295)

    def grid_widgets(self):
        self.abilities_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.events_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N + tk.W)
        self.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N + tk.W, padx = 5, pady = 5)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_label.grid(column = 0, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_numbers.grid(column = 2, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_label.grid(column = 0, row = 1, columnspan = 4, sticky = tk.N + tk.S + tk.W + tk.E)


class realtime_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class share_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class settings_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)
