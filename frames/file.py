"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
# Standard Library
from datetime import datetime
import operator
import os
from typing import Dict, List
# Project Modules
import variables
from parsing import matchstats, spawnstats
from data import abilities
from parsing.parser import Parser
from toplevels.splash import SplashScreen
from parsing.filehandler import FileHandler
from parsing.screen import ScreenParser
from widgets.general import Calendar, DateKeyDict


# Class for the _frame in the fileTab of the parser
class FileFrame(ttk.Frame):
    """Frame containing widgets for file, match and spawn selection"""

    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        """Create all widgets and make the links between them"""
        ttk.Frame.__init__(self, root_frame, width=200, height=420)
        self.main_window = main_window
        self._splash: SplashScreen = None

        self._calendar = Calendar(self, callback=self._select_date, highlight="#4286f4")
        self._tree = ttk.Treeview(self, show=("tree", "headings"), height=6)
        self._scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._refresh_button = ttk.Button(self, text="Refresh", command=self.update_files)

        self._files: List[str] = list()
        self._dates: Dict[datetime: List[str]] = DateKeyDict()

        self.setup_tree()

    def setup_tree(self):
        """Configure the Treeview options"""
        self._tree.configure(yscrollcommand=self._scroll.set)
        self._tree.column("#0", width=150)
        self._tree.heading("#0", text="Matches")
        self._tree.bind("<Double-1>", self._parse_item)

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
        self._calendar.grid(row=0, column=0, sticky="nswe")
        self._tree.grid(row=1, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self._scroll.grid(row=1, column=1, sticky="nswe", pady=(0, 5))
        self._refresh_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=(0, 5))

    def update_files(self):
        """Update the Calendar with the new files"""
        self.clear_data_widgets()
        self._dates.clear()
        folder = variables.settings["parsing"]["path"]
        if not os.path.exists(folder):
            messagebox.showerror("Error",
                "The specified CombatLogs folder does not exist. Please "
                "choose a different folder.")
            folder = filedialog.askdirectory()
            variables.settings.write_settings({"parsing": {"path": folder}})
            return self.update_files()
        files = [f for f in os.listdir(folder) if Parser.get_gsf_in_file(f)]
        self.create_splash(len(files))
        match_count: Dict[datetime: int] = DateKeyDict()
        for file in files:
            date = Parser.parse_filename(file)
            if date is None:  # Failed to parse
                continue
            if date not in match_count:
                match_count[date] = 0
            match_count[date] += Parser.count_matches(file)
            if date not in self._dates:
                self._dates[date] = list()
            self._dates[date].append(file)
            self._splash.increment()
        self._calendar.update_heatmap(match_count)
        self.destroy_splash()

    def _select_date(self, date: datetime):
        """Callback for Calendar widget selection command"""
        self.clear_data_widgets()
        self._tree.delete(*self._tree.get_children(""))
        if date not in self._dates:
            return
        self._files: List[str] = self._dates[date]
        for f, file in enumerate(sorted(self._files)):
            name = Parser.get_player_name_raw(file)
            cube, matches, spawns = Parser.split_combatlog_file(file)
            for m, match in enumerate(sorted(matches[::2])):
                match = datetime.strftime(match, "%H:%M, {}".format(name))
                match_iid = "{},{}".format(f, m)
                self._tree.insert("", tk.END, text=match, iid=match_iid)
                for s, spawn in enumerate(sorted(spawns[m])):
                    spawn = datetime.strftime(spawn, "%H:%M:%S")
                    player_list: List[str] = Parser.get_player_id_list(cube[m][s])
                    abs_dict: Dict[str: int] = Parser.get_abilities_dict(cube[m][s], player_list)
                    ships: List[str] = Parser.get_ship_for_dict(abs_dict)
                    ship = self.format_ships_list(ships)
                    spawn = "{}{}".format(spawn, ship)
                    spawn_iid = "{},{},{}".format(f, m, s)
                    self._tree.insert(match_iid, tk.END, text=spawn, iid=spawn_iid)

    def _parse_item(self, _: tk.Event):
        """Parse a match/spawn from a file"""
        self.clear_data_widgets()
        selection = self._tree.selection()
        if len(selection) == 0:
            return
        elements = selection[0].split(",")
        if len(elements) == 3:  # Spawns
            f, m, s = map(int, elements)
            self.parse_spawn(self._files[f], m, s)
        else:  # Matches
            f, m = map(int, elements)
            self.parse_match(self._files[f], m)

    def create_splash(self, maximum: int):
        """Update the maximum value of the splash screen"""
        if self.main_window.splash is not None:
            self._splash = self.main_window.splash
            self._splash.update_max(maximum)
        else:
            self._splash = SplashScreen(self.main_window, maximum, title="Loading Files")

    def destroy_splash(self):
        """Destroy the self-created SplashScreen or keep the BootSplash"""
        if self.main_window.splash is None:
            self._splash.destroy()

    def update_widgets(self, abilities_dict, statistics_string, shipsdict, enemies, enemydamaged,
                       enemydamaget, uncounted):
        """
        This function can update the dta widgets for files, matches and
        folders by updating the widgets of statsframe and shipsframe
        according to the data received from results
        :param abilities_dict: abilities dictionary with abilities as
            keys and amounts as values
        :param statistics_string: string to set in the statistics tab
        :param shipsdict: dictionary with ships as keys and amounts as
            values
        :param enemies: list of enemy ID numbers
        :param enemydamaged: dictionary with enemies as keys and
            amounts of damage as values
        :param enemydamaget: dictionary with enemies as keys and
            amounts of damage as values
        :param uncounted: amount of uncounted ship occurrences
        """
        self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
        for key, value in abilities_dict.items():
            self.main_window.middle_frame.abilities_treeview.insert('', tk.END, text=key, values=(value,))
        ships_string = "Ships used:\t\tCount:\n"
        for ship in abilities.ships_strings:
            if variables.settings["gui"]["faction"] == "republic":
                name = abilities.rep_strings[ship]
            else:
                name = ship
            try:
                ships_string += name + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
            except KeyError:
                ships_string += name + "\t\t0\n"
        ships_string += "Uncounted\t\t" + str(uncounted)
        self.main_window.ship_frame.ship_label_var.set(ships_string)
        for enemy in enemies:
            self.insert_enemy_into_treeview(enemy, enemydamaged, enemydamaget)
        sequence = shipsdict.items()
        most_used_ship = "default" if len(sequence) == 0 else max(sequence, key=operator.itemgetter(1))[0]
        self.main_window.ship_frame.update_ship([most_used_ship])
        self.main_window.ship_frame.update()
        self.main_window.middle_frame.screen_label_var.set("Not available for files and matches")

    def update_widgets_spawn(self, name, spawn, abilitiesdict, statistics_string, ships_list, comps, enemies,
                             enemydamaged, enemydamaget):
        """
        This function sets the data widgets for the spawn results
        results
        :param name: player name
        :param spawn: section of CombatLog
        :param abilitiesdict: abilities dictionary with abilities as
            keys and amounts as values
        :param statistics_string: string to set in the statistics tab
        :param ships_list: list of possible ships
        :param comps: list of ship components
        :param enemies: list of enemy ID numbers
        :param enemydamaged: dictionary with enemies as keys and
            amounts of damage as values
        :param enemydamaget: dictionary with enemies as keys and
            amounts of damage as values
        """
        for key, value in abilitiesdict.items():
            self.main_window.middle_frame.abilities_treeview.insert('', tk.END, text=key, values=(value,))
        self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
        ships_string = "Possible ships used:\n"
        for ship in ships_list:
            faction = variables.settings["gui"]["faction"]
            ship_name = ship if faction == "imperial" else abilities.rep_ships[ship]
            ships_string += ship_name + "\n"
        ships_string += "\t\t\t\t\t\t\nWith the components:\n"
        for component in comps:
            ships_string += component + "\n"
        self.main_window.ship_frame.ship_label_var.set(ships_string)
        for enemy in enemies:
            self.insert_enemy_into_treeview(enemy, enemydamaged, enemydamaget)
        self.main_window.ship_frame.update_ship(ships_list)
        print("[FileFrame] Inserting spawn of {} items.".format(len(spawn)))
        self.main_window.middle_frame.time_view.insert_spawn(spawn, name)

    def parse_match(self, file: str, match_i: int):
        """
        Either adds sets the match and calls add_spawns to add the
        spawns found in the match or starts the results of all files
        found in the specified file and displays the results in the
        other frames.
        """
        print("[FileFrame] Parsing file '{}', match {}".format(file, match_i))
        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        lines = Parser.read_file(file)
        player_list = Parser.get_player_id_list(lines)
        file_cube, match_timings, _ = Parser.split_combatlog(lines, player_list)
        player_name = Parser.get_player_name(lines)
        match = file_cube[match_i]
        results = matchstats.match_statistics(file, match, match_timings[::2][match_i])
        self.update_widgets(*results)
        match_list = Parser.build_spawn_from_match(match)
        self.main_window.middle_frame.time_view.insert_spawn(match_list, player_name)
        match_timing = datetime.combine(Parser.parse_filename(file).date(), match_timings[::2][match_i].time())
        self.main_window.middle_frame.scoreboard.update_match(match_timing)

    def parse_spawn(self, file: str, match_i: int, spawn_i: int):
        """
        Either starts the results of ALL spawns found in the specified
        match or just one of them and displays the results in the other
        frames accordingly.
        """
        print("[FileFrame] Parsing '{}', match {}, spawn {}".format(file, match_i, spawn_i))
        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        lines = Parser.read_file(file)
        player_list = Parser.get_player_id_list(lines)
        player_name = Parser.get_player_name(lines)
        file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player_list)
        match = file_cube[match_i]
        spawn = match[spawn_i]
        results = list(spawnstats.spawn_statistics(
            file, spawn, spawn_timings[match_i][spawn_i]))
        results[1] = Parser.parse_player_reaction_time(spawn, player_name)
        orig = len(results[1])
        results[1] = ScreenParser.build_spawn_events(
            file, match_timings[::2][match_i], spawn_timings[match_i][spawn_i], spawn, player_name)
        print("[FileFrame] ScreenParser built {} events. Total: {}".format(len(results[1]) - orig, len(results[1])))
        self.update_widgets_spawn(*results)
        arguments = (file, match_timings[::2][match_i], spawn_timings[match_i][spawn_i])
        string = FileHandler.get_features_string(*arguments)
        self.main_window.middle_frame.screen_label_var.set(string)
        self.main_window.middle_frame.update_timeline(
            file, match_i, spawn_i, match_timings, spawn_timings, file_cube)
        match_timing = datetime.combine(Parser.parse_filename(file).date(), match_timings[::2][match_i].time())
        self.main_window.middle_frame.scoreboard.update_match(match_timing)

    def clear_data_widgets(self):
        """Clear the data widgets for results parsing"""
        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        self.main_window.middle_frame.screen_label_var.set(
            "Please select an available spawn for screen results information")
        self.main_window.middle_frame.time_view.delete(
            *self.main_window.middle_frame.time_view.get_children())
        self.main_window.middle_frame.time_line.delete_marker(tk.ALL)
        self.main_window.middle_frame.scoreboard.reset()

    def insert_enemy_into_treeview(self, enemy, enemydamaged, enemydamaget):
        """
        Insert an enemy into the Treeview with the appropriate string
        :param enemy: ID number/name
        :param enemydamaged: dictionary
        :param enemydamaget: dictionary
        """
        damage_d = str(enemydamaged[enemy]) if enemy in enemydamaged else 0
        damage_t = str(enemydamaget[enemy]) if enemy in enemydamaget else 0
        kwargs = {"text": "Enemy" if enemy == "" else enemy, "values": (damage_d, damage_t)}
        self.main_window.middle_frame.enemies_treeview.insert("", tk.END, **kwargs)

    @staticmethod
    def format_ships_list(ships: List[str]):
        """Format a list of ship possibilities"""
        if len(ships) == 0:
            return ", Unknown"
        elif len(ships) == 1:
            return ", {}".format(ships[0])
        else:
            return ""
