# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI Imports
try:
     import mtTkinter as tk
except ImportError:
     import Tkinter as tk
import ttk
import tkMessageBox
# General imports
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import pyplot
from matplotlib import dates as matdates
from matplotlib.figure import Figure
import os
import datetime
from collections import OrderedDict
# Own modules
import vars
import parse
import toplevels

class graphs_frame(ttk.Frame):
    """
    A frame containing a place for a graph where the user can view his/her performance over time.
    """
    def __init__(self, root, main_window):
        """
        Set-up the plot, check the back-end and create all widgets necessary to display the plot
        and let the user select the type of plot he/she wants.
        :param root:
        :param main_window:
        """
        ttk.Frame.__init__(self, root)
        if matplotlib.get_backend() != "TkAgg":
            raise
        self.main_window = main_window
        self.type_graph = tk.StringVar()
        self.type_graph.set("play")
        self.graph_label = ttk.Label(self, text = "Here you can view various types of graphs of your performance over time.",
                                     justify = tk.LEFT, font = ("Calibri", 12))
        self.play_graph_radio = ttk.Radiobutton(self, variable = self.type_graph, value = "play", text = "Matches played")
        self.dmgd_graph_radio = ttk.Radiobutton(self, variable = self.type_graph, value = "dmgd", text = "Damage dealt")
        self.dmgt_graph_radio = ttk.Radiobutton(self, variable = self.type_graph, value = "dmgt", text = "Damage taken")
        self.hrec_graph_radio = ttk.Radiobutton(self, variable = self.type_graph, value = "hrec", text = "Healing received")
        # self.enem_graph_radio = ttk.Radiobutton(self, variable = self.type_graph, value = "enem", text = "Enemies damage dealt to")
        self.update_button = ttk.Button(self, command = self.update_graph, text = "Update graph")
        self.figure, self.axes = pyplot.subplots(figsize=(8.3, 4.2))
        # pyplot.ion()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvasw = self.canvas.get_tk_widget()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.figure.clear()

    def update_graph(self):
        """
        Function called by the update_button.
        Starts the calculation of the graphs and sets the axes and format of the plot
        Shows the plot accordingly
        Code of last three options is mostly the same
        :return:
        """
        self.figure.clear()
        if self.type_graph.get() == "play":
            files_dates = {}
            datetimes = []
            vars.files_done = 0
            self.splash_screen = toplevels.splash_screen(self.main_window, max=len(os.listdir(vars.set_obj.cl_path)),
                                                         title="Calculating graph...")
            matches_played_date = {}
            for file in os.listdir(vars.set_obj.cl_path):
                if not file.endswith(".txt"):
                    continue
                try: file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except: continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(file, "r") as file_obj:
                    lines = file_obj.readlines()
                    file_cube, match_timings, spawn_timings = parse.splitter(lines, parse.determinePlayer(lines))
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                vars.files_done += 1
                self.splash_screen.update_progress()
            pyplot.bar(list(matches_played_date.iterkeys()), list(matches_played_date.itervalues()), color=vars.set_obj.color)
            self.axes.xaxis_date()
            pyplot.title("Matches played")
            pyplot.ylabel("Amount of matches")
            pyplot.xlabel("Date")
            pyplot.xticks(rotation='vertical')
            pyplot.gca().xaxis.set_major_locator(matdates.MonthLocator())
            self.figure.subplots_adjust(bottom = 0.35)
            self.canvas.show()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "dmgd":
            files_dates = {}
            datetimes = []
            vars.files_done = 0
            self.splash_screen = toplevels.splash_screen(self.main_window, max=len(os.listdir(vars.set_obj.cl_path)),
                                                         title="Calculating graph...")
            matches_played_date = {}
            damage_per_date = {}
            for file in os.listdir(vars.set_obj.cl_path):
                if not file.endswith(".txt"):
                    continue
                try: file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except: continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                results_tuple = parse.parse_file(file_cube, player, match_timings, spawn_timings)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                if file_date not in damage_per_date:
                    damage_per_date[file_date] = sum([sum(match) for match in results_tuple[2]])
                else:
                    damage_per_date[file_date] += sum([sum(match) for match in results_tuple[2]])
                vars.files_done += 1
                self.splash_screen.update_progress()
            avg_dmg_date = {}
            for key, value in matches_played_date.iteritems():
                try:
                    avg_dmg_date[key] = round(damage_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print "[DEBUG] ZeroDivisionError while dividing damage by matches, passing"
                    pass
            avg_dmg_date = OrderedDict(sorted(avg_dmg_date.items(), key=lambda t: t[0]))
            pyplot.plot(list(avg_dmg_date.iterkeys()), list(avg_dmg_date.itervalues()), color=vars.set_obj.color)
            self.axes.xaxis_date()
            pyplot.title("Average damage dealt per match")
            pyplot.ylabel("Amount of damage")
            pyplot.xlabel("Date")
            pyplot.xticks(rotation='vertical')
            pyplot.gca().xaxis.set_major_locator(matdates.MonthLocator())
            self.figure.subplots_adjust(bottom = 0.35)
            self.canvas.show()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "dmgt":
            files_dates = {}
            datetimes = []
            vars.files_done = 0
            self.splash_screen = toplevels.splash_screen(self.main_window, max=len(os.listdir(vars.set_obj.cl_path)),
                                                         title="Calculating graph...")
            matches_played_date = {}
            damage_per_date = {}
            for file in os.listdir(vars.set_obj.cl_path):
                if not file.endswith(".txt"):
                    continue
                try: file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except: continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                results_tuple = parse.parse_file(file_cube, player, match_timings, spawn_timings)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                if file_date not in damage_per_date:
                    damage_per_date[file_date] = sum([sum(match) for match in results_tuple[1]])
                else:
                    damage_per_date[file_date] += sum([sum(match) for match in results_tuple[1]])
                vars.files_done += 1
                self.splash_screen.update_progress()
            avg_dmg_date = {}
            for key, value in matches_played_date.iteritems():
                try:
                    avg_dmg_date[key] = round(damage_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print "[DEBUG] ZeroDivisionError while dividing damage by matches, passing"
                    pass
            avg_dmg_date = OrderedDict(sorted(avg_dmg_date.items(), key=lambda t: t[0]))
            pyplot.plot(list(avg_dmg_date.iterkeys()), list(avg_dmg_date.itervalues()), color=vars.set_obj.color)
            self.axes.xaxis_date()
            pyplot.title("Average damage taken per match")
            pyplot.ylabel("Amount of damage")
            pyplot.xlabel("Date")
            pyplot.xticks(rotation='vertical')
            pyplot.gca().xaxis.set_major_locator(matdates.MonthLocator())
            self.figure.subplots_adjust(bottom = 0.35)
            self.canvas.show()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "hrec":
            files_dates = {}
            datetimes = []
            vars.files_done = 0
            self.splash_screen = toplevels.splash_screen(self.main_window, max=len(os.listdir(vars.set_obj.cl_path)),
                                                         title="Calculating graph...")
            matches_played_date = {}
            damage_per_date = {}
            for file in os.listdir(vars.set_obj.cl_path):
                if not file.endswith(".txt"):
                    continue
                try: file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except: continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                results_tuple = parse.parse_file(file_cube, player, match_timings, spawn_timings)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                if file_date not in damage_per_date:
                    damage_per_date[file_date] = sum([sum(match) for match in results_tuple[4]])
                else:
                    damage_per_date[file_date] += sum([sum(match) for match in results_tuple[4]])
                vars.files_done += 1
                self.splash_screen.update_progress()
            avg_dmg_date = {}
            for key, value in matches_played_date.iteritems():
                try:
                    avg_dmg_date[key] = round(damage_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print "[DEBUG] ZeroDivisionError while dividing damage by matches, passing"
                    pass
            avg_dmg_date = OrderedDict(sorted(avg_dmg_date.items(), key = lambda t: t[0]))
            pyplot.plot(list(avg_dmg_date.iterkeys()), list(avg_dmg_date.itervalues()), color=vars.set_obj.color)
            self.axes.xaxis_date()
            pyplot.title("Average healing received per match")
            pyplot.ylabel("Amount of healing")
            pyplot.xlabel("Date")
            pyplot.xticks(rotation='vertical')
            pyplot.gca().xaxis.set_major_locator(matdates.MonthLocator())
            self.figure.subplots_adjust(bottom = 0.35)
            self.canvas.show()
            self.splash_screen.destroy()
        else:
            tkMessageBox.showinfo("Notice", "No correct graph type selected!")
        self.axes.set_ylim(bottom=0.)


    def grid_widgets(self):
        """
        Put all widgets in the right place
        :return:
        """
        self.graph_label.grid(column = 0, row = 0, rowspan = 1, columnspan = 2, sticky = tk.W, pady = 5)
        self.play_graph_radio.grid(column = 0, row = 1, sticky = tk.W)
        self.dmgd_graph_radio.grid(column = 0, row = 2, sticky = tk.W)
        self.dmgt_graph_radio.grid(column = 0, row = 3, sticky = tk.W)
        self.hrec_graph_radio.grid(column = 0, row = 4, sticky = tk.W)
        self.update_button.grid(column = 0, row = 6, sticky =tk.W + tk.E + tk.N + tk.S)
        self.canvasw.grid(column = 1, row = 1, rowspan = 20, sticky = tk.N + tk.W, padx = 10)
        self.toolbar.grid(column = 1, row = 21, sticky =tk.N + tk.W)

    def close(self):
        """
        Try to close as much as possible
        A known bug makes it impossible for the plot to be
        closed correctly. This bug is in the matplotlib library
        :return:
        """
        print "[DEBUG] Close() of graphs_frame called"
        # Plots are not correctly closed, threads keep running in the background
        # This is a known bug to matplotlib and Tkinter: TkAgg
        pyplot.cla()
        pyplot.clf()
        pyplot.close()
        pyplot.close('all')
        pyplot.plot()
        self.figure.clear()
        self.canvasw.destroy()
        self.toolbar.destroy()
