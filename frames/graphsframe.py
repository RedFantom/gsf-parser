# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI Imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import platform
import os
import datetime
from collections import OrderedDict
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import variables
from parsing import parse
from toplevels.splashscreens import SplashScreen


class GraphsFrame(ttk.Frame):
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
            raise ValueError("Backend is not TkAgg")
        self.main_window = main_window
        self.type_graph = tk.StringVar()
        self.type_graph.set("play")
        self.graph_label = ttk.Label(self,
                                     text="Here you can view various types of graphs of your performance over "
                                          "time.",
                                     justify=tk.LEFT, font=("Calibri", 12))
        self.play_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="play",
                                                text="Matches played")
        self.dmgd_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="dmgd",
                                                text="Damage dealt")
        self.dmgt_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="dmgt",
                                                text="Damage taken")
        self.hrec_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="hrec",
                                                text="Healing received")
        self.enem_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="enem", text="Enemies")
        self.crit_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="critluck",
                                                text="Critical luck")
        self.hitc_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="hitcount",
                                                text="Hitcount")
        self.spawn_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="spawn",
                                                 text="Spawn length")
        self.match_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="match",
                                                 text="Match length")
        self.death_graph_radio = ttk.Radiobutton(self, variable=self.type_graph, value="deaths", text="Deaths")
        self.update_button = ttk.Button(self, command=self.update_graph, text="Update graph")
        self.graph = ttk.Frame(self)
        if platform.release() == "7" or platform.release() == "8" or platform.release() == "8.1":
            self.figure = Figure(figsize=(6.6, 3.3))
        else:
            self.figure = Figure(figsize=(6.7, 3.35))
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph)
        self.canvasw = self.canvas.get_tk_widget()
        self.tkcanvas = self.canvas._tkcanvas
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.graph)
        self.toolbar.update()

    def update_graph(self):
        """
        Function called by the update_button.
        Starts the calculation of the graphs and sets the axes and format of the plot
        Shows the plot accordingly
        Code of last three options is mostly the same
        :return:
        """
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        if self.type_graph.get() == "play":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                    file_cube, match_timings, spawn_timings = parse.splitter(lines, parse.determinePlayer(lines))
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                files_done += 1
                self.splash_screen.update_progress(files_done)
            self.axes.set_ylim(ymin=0, ymax=matches_played_date[
                                                max(matches_played_date, key=matches_played_date.get)] + 2)
            self.axes.bar(list(matches_played_date.keys()), list(matches_played_date.values()),
                          color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Matches played")
            self.axes.set_ylabel("Amount of matches")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "dmgd":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            damage_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
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
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_dmg_date = {}
            for key, value in matches_played_date.items():
                try:
                    avg_dmg_date[key] = round(damage_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing damage by matches, passing")
                    pass
            avg_dmg_date = OrderedDict(sorted(list(avg_dmg_date.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_dmg_date[max(avg_dmg_date, key=avg_dmg_date.get)] + 2000)
            self.axes.plot(list(avg_dmg_date.keys()), list(avg_dmg_date.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average damage dealt per match")
            self.axes.set_ylabel("Amount of damage")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "dmgt":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            damage_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
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
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_dmg_date = {}
            for key, value in matches_played_date.items():
                try:
                    avg_dmg_date[key] = round(damage_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing damage by matches, passing")
                    pass
            avg_dmg_date = OrderedDict(sorted(list(avg_dmg_date.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_dmg_date[max(avg_dmg_date, key=avg_dmg_date.get)] + 2000)
            self.axes.plot(list(avg_dmg_date.keys()), list(avg_dmg_date.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average damage taken per match")
            self.axes.set_ylabel("Amount of damage")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "hrec":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            damage_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
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
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_dmg_date = {}
            for key, value in matches_played_date.items():
                try:
                    avg_dmg_date[key] = round(damage_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing damage by matches, passing")
                    pass
            avg_dmg_date = OrderedDict(sorted(list(avg_dmg_date.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_dmg_date[max(avg_dmg_date, key=avg_dmg_date.get)] + 2000)
            self.axes.plot(list(avg_dmg_date.keys()), list(avg_dmg_date.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average healing received per match")
            self.axes.set_ylabel("Amount of healing")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "enem":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            enem_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                results_tuple = parse.parse_file(file_cube, player, match_timings, spawn_timings)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                total_enemies_dt = []
                for match_matrix in results_tuple[5]:
                    for spawn_list in match_matrix:
                        for enem in spawn_list:
                            if results_tuple[10][enem] > 0:
                                total_enemies_dt.append(enem)
                total_enemies_dt = set(total_enemies_dt)
                amount_enem = len(total_enemies_dt)
                if file_date in enem_per_date:
                    enem_per_date[file_date] += amount_enem
                else:
                    enem_per_date[file_date] = amount_enem
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_enem_date = {}
            for key, value in matches_played_date.items():
                try:
                    avg_enem_date[key] = round(enem_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing damage by matches, passing")
                    pass
            avg_dmg_date = OrderedDict(sorted(list(avg_enem_date.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_dmg_date[max(avg_dmg_date, key=avg_dmg_date.get)] + 2)
            self.axes.plot(list(avg_dmg_date.keys()), list(avg_dmg_date.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average enemies damage dealt to per match")
            self.axes.set_ylabel("Amount of enemies")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "critluck":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            hitcount_per_date = {}
            critcount_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                results_tuple = parse.parse_file(file_cube, player, match_timings, spawn_timings)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                if file_date not in hitcount_per_date:
                    hitcount_per_date[file_date] = sum(sum(spawn) for spawn in (match for match in results_tuple[8]))
                    critcount_per_date[file_date] = sum(sum(spawn) for spawn in (match for match in results_tuple[6]))
                else:
                    hitcount_per_date[file_date] += sum(sum(spawn) for spawn in (match for match in results_tuple[8]))
                    critcount_per_date[file_date] += sum(sum(spawn) for spawn in (match for match in results_tuple[6]))
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_crit_luck = {}
            for key, value in matches_played_date.items():
                try:
                    avg_crit_luck[key] = float(critcount_per_date[key]) / float(hitcount_per_date[key]) * 100
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing by hitcount, passing")
                    pass
            avg_crit_luck = OrderedDict(sorted(list(avg_crit_luck.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_crit_luck[max(avg_crit_luck, key=avg_crit_luck.get)] + 0.02)
            self.axes.plot(list(avg_crit_luck.keys()), list(avg_crit_luck.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average percentage critical hits per day")
            self.axes.set_ylabel("Percentage critical hits")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "hitcount":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            hitcount_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                results_tuple = parse.parse_file(file_cube, player, match_timings, spawn_timings)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                if file_date not in hitcount_per_date:
                    hitcount_per_date[file_date] = sum(sum(spawn) for spawn in (match for match in results_tuple[8]))
                else:
                    hitcount_per_date[file_date] += sum(sum(spawn) for spawn in (match for match in results_tuple[8]))
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_hit_match = {}
            for key, value in matches_played_date.items():
                try:
                    avg_hit_match[key] = round(hitcount_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing by hitcount, passing")
                    pass
            avg_crit_luck = OrderedDict(sorted(list(avg_hit_match.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_crit_luck[max(avg_crit_luck, key=avg_crit_luck.get)] + 10)
            self.axes.plot(list(avg_crit_luck.keys()), list(avg_crit_luck.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average hitcount per match per day")
            self.axes.set_ylabel("Amount of hits")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "spawn":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            spawns_played_date = {}
            spawn_length_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                if file_date in spawns_played_date:
                    spawns_played_date[file_date] += sum(len(match) for match in file_cube)
                else:
                    spawns_played_date[file_date] = sum(len(match) for match in file_cube)
                start = True
                spawns_length = 0
                start_timing = None
                for match in spawn_timings:
                    for timing in match:
                        if start:
                            start = False
                            start_timing = timing
                        else:
                            start = True
                            spawns_length += (timing - start_timing).seconds
                if file_date in spawn_length_per_date:
                    spawn_length_per_date[file_date] += spawns_length
                else:
                    spawn_length_per_date[file_date] = spawns_length
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_spawn_min = {}
            for key, value in spawns_played_date.items():
                try:
                    avg_spawn_min[key] = round((float(spawn_length_per_date[key]) / float(value)) / 60, 2)
                    if avg_spawn_min[key] == 0:
                        del avg_spawn_min[key]
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing by hitcount, passing")
                    pass
            avg_crit_luck = OrderedDict(sorted(list(avg_spawn_min.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_crit_luck[max(avg_crit_luck, key=avg_crit_luck.get)] + 1)
            self.axes.plot(list(avg_crit_luck.keys()), list(avg_crit_luck.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Length of average spawn per day")
            self.axes.set_ylabel("Spawn length in minutes")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "match":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            match_length_day = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                match_length = 0
                start = True
                start_timing = None
                for timing in match_timings:
                    if start:
                        start_timing = timing
                        start = False
                    else:
                        match_length += (timing - start_timing).seconds
                        start = True
                if file_date in match_length_day:
                    match_length_day[file_date] += match_length
                else:
                    match_length_day[file_date] = match_length
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_match_min = {}
            for key, value in matches_played_date.items():
                try:
                    avg_match_min[key] = round((float(match_length_day[key]) / float(value)) / 60, 2)
                    if avg_match_min[key] == 0:
                        del avg_match_min[key]
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing by hitcount, passing")
                    pass
            avg_crit_luck = OrderedDict(sorted(list(avg_match_min.items()), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_crit_luck[max(avg_crit_luck, key=avg_crit_luck.get)] + 2)
            self.axes.plot(list(avg_crit_luck.keys()), list(avg_crit_luck.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Length of average match per day")
            self.axes.set_ylabel("Match length in minutes")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        elif self.type_graph.get() == "deaths":
            files_dates = {}
            datetimes = []
            files_done = 0
            self.splash_screen = SplashScreen(self.main_window,
                                              len(os.listdir(variables.settings["parsing"]["path"])),
                                              title="Calculating graph...")
            matches_played_date = {}
            deaths_per_date = {}
            for file in os.listdir(variables.settings["parsing"]["path"]):
                if not file.endswith(".txt"):
                    continue
                try:
                    file_date = datetime.date(int(file[7:-26]), int(file[12:-23]), int(file[15:-20]))
                except ValueError:
                    continue
                datetimes.append(file_date)
                files_dates[file] = file_date
                with open(variables.settings["parsing"]["path"] + "/" + file, "r") as file_obj:
                    lines = file_obj.readlines()
                player = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player)
                if file_date not in matches_played_date:
                    matches_played_date[file_date] = len(file_cube)
                else:
                    matches_played_date[file_date] += len(file_cube)
                if file_date not in deaths_per_date:
                    deaths_per_date[file_date] = sum((len(match) - 1) for match in file_cube)
                else:
                    deaths_per_date[file_date] += sum((len(match) - 1) for match in file_cube)
                files_done += 1
                self.splash_screen.update_progress(files_done)
            avg_hit_match = {}
            for key, value in matches_played_date.items():
                try:
                    avg_hit_match[key] = round(deaths_per_date[key] / value, 0)
                except ZeroDivisionError:
                    print("[DEBUG] ZeroDivisionError while dividing by hitcount, passing")
                    pass
            avg_crit_luck = OrderedDict(sorted(avg_hit_match.items(), key=lambda t: t[0]))
            self.axes.set_ylim(ymin=0, ymax=avg_crit_luck[max(avg_crit_luck, key=avg_crit_luck.get)] + 2)
            self.axes.plot(list(avg_crit_luck.keys()), list(avg_crit_luck.values()),
                           color=variables.settings["gui"]["color"])
            self.axes.xaxis_date()
            self.axes.set_title("Average amount of deaths per match per day")
            self.axes.set_ylabel("Amount of deaths")
            self.axes.set_xlabel("Date")
            self.toolbar.update()
            self.canvas.show()
            self.figure.autofmt_xdate(bottom=0.25)
            self.figure.canvas.draw()
            self.splash_screen.destroy()
        else:
            tkinter.messagebox.showinfo("Notice", "No correct graph type selected!")

    def grid_widgets(self):
        """
        Put all widgets in the right place
        :return:
        """
        self.graph_label.grid(column=0, row=0, rowspan=1, columnspan=2, sticky="w", pady=5)
        self.play_graph_radio.grid(column=0, row=1, sticky="w")
        self.dmgd_graph_radio.grid(column=0, row=2, sticky="w")
        self.dmgt_graph_radio.grid(column=0, row=3, sticky="w")
        self.hrec_graph_radio.grid(column=0, row=4, sticky="w")
        self.enem_graph_radio.grid(column=0, row=5, sticky="w")
        self.crit_graph_radio.grid(column=0, row=6, sticky="w")
        self.hitc_graph_radio.grid(column=0, row=7, sticky="w")
        self.spawn_graph_radio.grid(column=0, row=8, sticky="w")
        self.match_graph_radio.grid(column=0, row=9, sticky="w")
        self.death_graph_radio.grid(column=0, row=10, sticky="w")
        self.update_button.grid(column=0, row=19, sticky="nswe")
        self.canvasw.pack()
        self.tkcanvas.pack()
        self.toolbar.pack()
        self.graph.grid(column=1, row=1, rowspan=20)
