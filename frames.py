# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
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
import main

# Class for the _frame in the fileTab of the parser
class file_frame(ttk.Frame):
    # __init__ creates all widgets
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame, width = 200, height = 600)
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

    def grid_widgets(self):
        self.file_box.grid(column = 0, row = 0, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.file_box_scroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.match_box.grid(column = 0, row =8, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.match_box_scroll.grid(column = 2, row = 8, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)
        self.spawn_box.grid(column = 0, row = 16, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.spawn_box_scroll.grid(column = 2, row = 16, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)

    def add_matches(self):
        self.match_timing_strings = []
        self.match_timing_strings = [time.time() for time in vars.match_timings]
        for number in range(0, len(self.match_timing_strings) + 1):
            self.match_box.delete(number)
        self.match_box.delete(0, tk.END)
        read_next = True
        self.match_box.insert(tk.END, "All matches")
        for time in self.match_timing_strings:
            if not read_next:
                read_next = True
            else:
                self.match_box.insert(tk.END, time)
                read_next = False

    def add_spawns(self):
        self.spawn_timing_strings = []
        for match in vars.spawn_timings:
            for time in match:
                self.spawn_timing_strings.append(time.time())
        self.spawn_box.delete(0, tk.END)
        self.spawn_box.insert(tk.END, "All spawns")
        for time in self.spawn_timing_strings:
            self.spawn_box.insert(tk.END, time)

    def add_files(self):
        self.file_strings = []
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                self.file_strings.append(file)
        self.file_box.delete(0, tk.END)
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file)

    def file_update(self, instance):
        if self.file_box.curselection() == (0,):
            print "All CombatLogs selected"
        else:
            numbers = self.file_box.curselection()
            vars.file_name = self.file_strings[numbers[0] - 1]
            print vars.file_name
            file_object = open(vars.file_name, "r")
            lines = file_object.readlines()
            player = parse.determinePlayer(lines)
            vars.file_cube, vars.match_timings, vars.spawn_timings = parse.splitter(lines, player)
            file_object.close()
            self.add_matches()          

    def match_update(self, instance):
        print "Update! ", instance       
            
    def spawn_update(self, instance):
        print "Update! ", instance

class ship_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class middle_frame(ttk.Frame):
    def __init__(self, root_frame, width = 300, height = 600):
        ttk.Frame.__init__(self, root_frame)
        self.statistics_frame = statistics_frame(self)
        self.events_frame = events_frame(self)

    def grid_widgets(self):
        self.statistics_frame.grid_widgets()
        self.events_frame.grid_widgets()
        self.statistics_frame.pack(side = tk.TOP)
        self.events_frame.pack(side = tk.BOTTOM)

class statistics_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)
        self.notebook = ttk.Notebook(self, width = 300, height = 270)
        self.stats_frame = ttk.Frame(self.notebook)
        self.allies_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text = "Statistics")
        self.notebook.add(self.allies_frame, text = "Allies")
        self.notebook.add(self.enemies_frame, text = "Enemies")
        self.statistics_label_var = tk.StringVar()
        self.statistics_label = tk.Label(self.stats_frame, textvariable = self.statistics_label_var, justify = tk.LEFT, wraplength = 295)
        self.allies_label_var = tk.StringVar()
        self.allies_label = tk.Label(self.allies_frame, textvariable = self.allies_label_var, justify = tk.LEFT, wraplength = 295)
        self.enemies_label_var = tk.StringVar()
        self.enemies_label = tk.Label(self.enemies_frame, textvariable = self.enemies_label_var, justify = tk.LEFT, wraplength = 295)

    def grid_widgets(self):
        self.notebook.grid(column = 0, row = 0, columnspan = 4, rowspan = 12, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_label.grid(column = 0, row = 1, columnspan = 4, rowspan = 11, sticky = tk.N + tk.S + tk.W + tk.E)
        self.allies_label.grid(column = 0, row = 1, columnspan = 4, rowspan = 11, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_label.grid(column = 0, row = 1, columnspan = 4, rowspan = 11, sticky = tk.N + tk.S + tk.W + tk.E)
    
    def update_statistics(self):
        print "Update!"

class events_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)
        self.notebook = ttk.Notebook(self, width = 300, height = 270)
        self.events = ttk.Frame(self.notebook)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.events, text = "Events")
        self.notebook.add(self.abilities_frame, text = "Abilities")
        self.abilities_label_var = tk.StringVar()
        self.abilities_label = tk.Label(self.abilities_frame, textvariable = self.abilities_label_var, justify = tk.LEFT, wraplength = 295)

    def grid_widgets(self):
        self.abilities_label.grid(column = 0, row = 2, columnspan = 4, rowspan = 11, sticky = tk.N + tk.W)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, rowspan = 12, sticky = tk.N + tk.W)
        self.grid(column = 0, row = 0, columnspan = 4, rowspan = 12, sticky = tk.N + tk.W, padx = 5, pady = 5)

    def update_abilities(self, indexMatrix, indexList):
        for key in vars.abilitiesOccurrences[index]:
            self.abilities_label['text'] = self.abilities_label['text'] + str(key) +  "\n"

class realtime_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class share_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class settings_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)
