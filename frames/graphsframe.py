"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""

# UI Imports
import tkinter as tk
import tkinter.ttk as ttk
import platform
import os
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from variables import settings
from toplevels.splashscreens import SplashScreen
from parsing.parser import Parser


class GraphsFrame(ttk.Frame):
    """
    A frame containing a place for a graph where the user can view his/her
    performance over time.
    """

    graph_options = {
        "play": ("Matches played", "Matches played per day", "bar"),
        "dmgd": ("Damage dealt", "Damage dealt per match", "plot"),
        "dmgt": ("Damage taken", "Damage taken per match", "plot"),
        "hrec": ("Healing received", "Healing received per match", "plot"),
        "enem": ("Enemies", "Kills + Assists per match", "plot"),
        "critluck": ("Critical luck", "Critical hit percentage per match", "plot"),
        "hitcount": ("Hit count", "Amount of hits per match", "plot"),
        "spawn": ("Spawn Length", "Spawn length per match", "plot"),
        "match": ("Match Length", "Match length per day", "plot"),
        "deaths": ("Deaths", "Amount of deaths per match", "plot"),
    }

    def __init__(self, root, main_window):
        """
        Set-up the plot, check the back-end and create all widgets necessary to
        display the plot and let the user select the type of plot he/she wants.
        """
        ttk.Frame.__init__(self, root)
        if matplotlib.get_backend() != "TkAgg":
            raise ValueError("Backend is not TkAgg")
        self.main_window = main_window
        self.type_graph = tk.StringVar()
        self.type_graph.set("play")
        self.graph_label = ttk.Label(
            self, text="Here you can view various types of graphs of your performance over time.", justify=tk.LEFT,
            font=("Calibri", 12))
        self.graph_radios = {
            type: ttk.Radiobutton(self, variable=self.type_graph, value=type, text=description)
            for type, (description, _, _) in self.graph_options.items()
        }
        self.update_button = ttk.Button(self, command=self.calculate_graph, text="Calculate Graph")
        self.graph = ttk.Frame(self)
        size = (6.6, 3.3) if platform.release() in ("7", "8", "8.1", "10") else (6.7, 3.35)
        self.figure = Figure(figsize=size)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph)
        self.canvasw = self.canvas.get_tk_widget()
        self.tkcanvas = self.canvas._tkcanvas
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.graph)
        self.toolbar.update()

    def calculate_graph(self):
        """Calculate a new Graph based on the setting given by the user"""
        # Setup Figure for calculation
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        # Create required data variables
        files_done = 0
        graph_type = self.type_graph.get()
        print("[GraphsFrame] Calculating graph:", graph_type)
        files = os.listdir(settings["parsing"]["path"])
        value_per_date = {}
        files_per_date = {}
        # Open splash screen
        splash_screen = SplashScreen(
            self.main_window, len(files), title="Calculating graph...")
        # Loop over all the files
        for file in files:
            # Update splash screen
            files_done += 1
            splash_screen.update_progress(files_done)
            # Skip non-valid files
            if not Parser.get_gsf_in_file(file):
                continue
            file_datetime = Parser.parse_filename(file)
            if file_datetime is None:
                continue
            # Process date
            file_date = file_datetime.date()
            # Parse the file and calculate the value
            lines = Parser.read_file(file)
            player = Parser.get_player_id_list(lines)
            file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player)
            # Retrieve value for file
            value = GraphsFrame.calculate_value(graph_type, file_cube, match_timings, spawn_timings, player)
            # Update dictionary of amount of files per date
            if file_date not in files_per_date:
                files_per_date[file_date] = 0
            files_per_date[file_date] += 1
            # Update value per date
            if file_date not in value_per_date:
                value_per_date[file_date] = 0
            value_per_date[file_date] += value
        # Calculate the final values dictionary
        average_per_file = {date: value / files_per_date[date] for date, value in value_per_date.items()}
        values = average_per_file if graph_type != "play" else value_per_date
        # Calculate values
        x_values = sorted(values.keys())
        y_values = [values[key] for key in x_values]
        # Graph this setup
        graph_func = getattr(axes, self.graph_options[graph_type][2])
        graph_func(x_values, y_values, color=settings["gui"]["color"])
        # Change graph properties
        axes.xaxis_date()
        axes.set_xlabel("Date")
        axes.set_ylim(ymin=0, ymax=max(y_values) * 1.1)
        axes.set_title(self.graph_options[graph_type][1])
        axes.set_ylabel(self.graph_options[graph_type][0])
        self.toolbar.update()
        self.canvas.show()
        self.figure.autofmt_xdate(bottom=0.25)
        self.figure.canvas.draw()
        splash_screen.destroy()

    @staticmethod
    def calculate_value(graph_type, file_cube, match_timings, spawn_timings, player_id_list):
        """
        Calculate the correct value for a given graph type and file
        cube. Calculates the average per match in principal, but can
        differ for certain graph types.
        """
        amount_matches = len(file_cube)
        # Amount of matches played
        if graph_type == "play":
            return amount_matches
        # Amount of deaths per match
        elif graph_type == "deaths":
            return len(player_id_list) / amount_matches - 1
        # Average match and spawn length
        elif graph_type in ("match", "spawn"):
            total = 0
            start = None
            amount_spawns = sum(len(match) for match in file_cube)
            for timing in match_timings:
                if start is not None:
                    total += (timing - start).total_seconds()
                    start = None
                    continue
                start = timing
            total = total / 60
            return total / (amount_matches if graph_type == "match" else amount_spawns)

        # Parse the file as its required now
        (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount, critcount,
         crit_luck, enemies, enemy_dmg_d, enemy_dmg_t, ships, uncounted) = \
            Parser.parse_file(file_cube, player_id_list)
        # Average damage dealt per match
        if graph_type == "dmgd":
            return dmg_d / amount_matches
        # Average damage taken per match
        elif graph_type == "dmgt":
            return dmg_t / amount_matches
        # Average healing received per match
        elif graph_type == "hrec":
            return healing / amount_matches
        # Average hit count per match
        elif graph_type == "hitcount":
            return hitcount / amount_matches
        # Average critical luck per match
        elif graph_type == "critluck":
            return crit_luck / amount_matches
        # Average amount of enemies damage dealt to
        elif graph_type == "enem":
            return len(enemies) / amount_matches
        else:
            raise NotImplementedError()

    def grid_widgets(self):
        """
        Put all widgets in the right place
        """
        self.graph_label.grid(column=0, row=0, rowspan=1, columnspan=2, sticky="w", pady=5)
        row = 1
        for radio in self.graph_radios.values():
            radio.grid(row=row, column=0, sticky="w")
            row += 1
        self.update_button.grid(column=0, row=row, sticky="nswe")
        self.canvasw.pack()
        self.tkcanvas.pack()
        self.toolbar.pack()
        self.graph.grid(column=1, row=1, rowspan=row+1)
