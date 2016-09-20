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
# Own modules
import vars

# Class for the frame in the fileTab of the parser
class fileFrame(ttk.Frame):
    # __init__ creates all widgets
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)
        self.file_box = tk.Listbox(self, font = ("Arial", 11))
        self.file_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.file_box_scroll.config(command = self.file_box.yview)
        self.file_box.config(yscrollcommand = self.file_box_scroll.set)
        self.match_box = tk.Listbox(self, font = ("Arial", 11))
        self.match_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.match_box_scroll.config(command = self.match_box.yview)
        self.match_box.config(yscrollcommand = self.match_box_scroll.set)
        self.spawn_box = tk.Listbox(self, font = ("Arial", 11))
        self.spawn_box_scroll = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.spawn_box.yview)
        self.spawn_box.config(yscrollcommand = self.spawn_box_scroll.set)
     

    def grid_widgets(self):
        self.file_box.grid(column = 0, row = 0, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.file_box_scroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.match_box.grid(column = 0, row =8, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.match_box_scroll.grid(column = 2, row = 8, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)
        self.spawn_box.grid(column = 0, row = 16, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.spawn_box_scroll.grid(column = 2, row = 16, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)

    def add_matches(self):
        self.match_timing_strings = [time.time() for time in vars.match_timings]
        read_next = True
        self.spawn_box.delete(0, tk.END)
        self.spawn_box.insert(tk.END, "All matches")
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
    
    def get_file(self):
        return self.file_box.curselection()

    def get_match(self):
        return self.match_box.curselection()

    def get_spawn(self):
        return self.spawn_box.curselection()

class alliesFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class enemiesFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class playerFrame (ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class shipFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class statisticsFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class eventsFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)
        self.notebook = ttk.Notebook(self)
        self.events = ttk.Frame(self.notebook)
        self.abilitiesFrame = ttk.Frame(self.notebook)
        self.notebook.add(self.events, text = "Events")
        self.notebook.add(self.abilitiesFrame, text = "Abilities")
        self.abilitiesLabelVar = tk.StringVar()
        self.abilitiesLabel = tk.Label(self.abilitiesFrame, text = "", width = 40, height = 20, justify = tk.LEFT, wraplength = 250)

    def gridWidgets(self):
        self.abilitiesLabel.grid(column = 0, row = 2, columnspan = 4, rowspan = 11, sticky = tk.N + tk.W)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, rowspan = 12, sticky = tk.N + tk.W)
        self.grid(column = 0, row = 0, columnspan = 4, rowspan = 12, sticky = tk.N + tk.W, padx = 5, pady = 5)

    def updateAbilities(self, indexMatrix, indexList):
        for key in vars.abilitiesOccurrences[index]:
            self.abilitiesLabel['text'] = self.abilitiesLabel['text'] + str(key) +  "\n"

class realtimeFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class shareFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)

class settingsFrame(ttk.Frame):
    def __init__(self, rootFrame):
        ttk.Frame.__init__(self, rootFrame)