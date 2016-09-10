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
        self.fileBox = tk.Listbox(self, font = ("Arial", 11))
        self.fileBoxScroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.fileBoxScroll.config(command = self.fileBox.yview)
        self.fileBox.config(yscrollcommand = self.fileBoxScroll.set)
        self.fileBox.insert(tk.END, "All CombatLogs")
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt") == True:
                self.fileBox.insert(tk.END, str(file))
        self.matchBox = tk.Listbox(self, font = ("Arial", 11))
        self.matchBoxScroll = tk.Scrollbar(self, orient = tk.VERTICAL)
        self.matchBoxScroll.config(command = self.matchBox.yview)
        self.matchBox.config(yscrollcommand = self.matchBoxScroll.set)
        self.matchBox.insert(tk.END, "All matches")
        index = 0
        for match in vars.matches:
            self.matchBox.insert(tk.END, vars.timings(index))
            index += 2
        self.spawnBox = tk.Listbox(self, font = ("Arial", 11))
        self.spawnBoxScroll = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.spawnBox.yview)
        self.spawnBox.config(yscrollcommand = self.spawnBoxScroll.set)
        self.spawnBox.insert(tk.END, "All spawns")
        indexMatrix = 0
        indexList = 0
        for spawn in vars.spawns:
            self.spawnBox.insert(tk.END, vars.shipsUsed[indexMatrix][indexList])
        

    def gridWidgets(self):
        self.fileBox.grid(column = 0, row = 0, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.fileBoxScroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.matchBox.grid(column = 0, row =8, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.matchBoxScroll.grid(column = 2, row = 8, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)
        self.spawnBox.grid(column = 0, row = 16, columnspan = 2, rowspan = 8, padx = 5, pady = 5)
        self.spawnBoxScroll.grid(column = 2, row = 16, columnspan = 1, rowspan = 8, sticky = tk.N + tk.S, pady = 5)

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