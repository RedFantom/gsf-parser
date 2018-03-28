"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""

# UI Libraries
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.filedialog
# Standard Library
import operator
import os
# Project Modules
import variables
from parsing import folderstats, filestats, matchstats, spawnstats
from data import abilities
from parsing.parser import Parser
from toplevels.splashscreens import SplashScreen
from toplevels.filters import Filters
from collections import OrderedDict
from parsing.filehandler import FileHandler


# Class for the _frame in the fileTab of the parser
class FileFrame(ttk.Frame):
    """
    Class for a frame that contains three listboxes, one for files, one for matches and
    one for spawns, and updates them and other widgets after parsing the files using the
    methods found in the parse.py module accordingly. This frame controls the whole of file
    parsing, the other frames only display the results.
    --------------------
    | combatlog_1 | /\ |
    | combatlog_2 | || |
    | combatlog_3 | \/ |
    --------------------
    | match_1     | /\ |
    | match_2     | || |
    | match_3     | \/ |
    --------------------
    | spawn_1     | /\ |
    | spawn_2     | || |
    | spawn_3     | \/ |
    --------------------
    """

    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        """
        Create all widgets and make the links between them
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame, width=200, height=420)
        self.main_window = main_window
        self.file_tree = ttk.Treeview(self, height=13)
        self.file_tree.bind("<Double-1>", self.update_parse)
        self.file_tree["show"] = ("tree", "headings")
        self.file_tree.heading("#0", text="Files", command=self.flip_sorting)
        self.ascending = False
        self.file_tree.column("#0", width=150)
        self.file_string_dict = OrderedDict()
        self.match_string_dict = OrderedDict()
        self.spawn_string_dict = OrderedDict()
        self.file_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.config(yscrollcommand=self.file_scroll.set)

        self.match_timing_strings = None
        self.splash = None

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.add_files)
        self.filters_button = ttk.Button(self, text="Filters", command=self.filters)

    @staticmethod
    def filters():
        """
        Opens Toplevel to enable filters and then adds the filtered
        CombatLogs to the Listboxes
        """
        Filters()

    def grid_widgets(self):
        """
        Put all widgets in the right places
        :return:
        """
        self.file_tree.grid(column=0, row=0, rowspan=16, sticky="nswe", pady=5, padx=(5, 0))
        self.file_scroll.grid(column=1, row=0, rowspan=16, sticky="ns", pady=5)
        self.refresh_button.grid(column=0, columnspan=3, row=17, rowspan=1, sticky="nswe", padx=5)
        self.filters_button.grid(column=0, columnspan=3, row=18, rowspan=1, sticky="nswe", pady=5, padx=5)

    def flip_sorting(self):
        """
        Flip the sorting of the files in the Treeview (callback for the
        Treeview header button)
        """
        self.ascending = not self.ascending
        self.add_files()

    def add_files(self, silent=False):
        """
        Function that checks files found in the in the settings
        specified folder for GSF matches and if those are found in a
        file, it gets added to the listbox. Provides error handling.
        """
        self.file_tree.delete(*self.file_tree.get_children())
        self.clear_data_widgets()
        self.main_window.ship_frame.ship_label_var.set("")
        try:
            old_cwd = os.getcwd()
            os.chdir(variables.settings["parsing"]["path"])
            os.chdir(old_cwd)
        except OSError:
            tkinter.messagebox.showerror("Error",
                                         "The CombatLogs folder found in the settings file is not valid. Please "
                                         "choose another folder.")
            folder = tkinter.filedialog.askdirectory(title="CombatLogs folder")
            variables.settings.write_settings({'parsing': {'path': folder}})
            variables.settings.read_settings()
        combatlogs_folder = variables.settings["parsing"]["path"]
        file_list = os.listdir(combatlogs_folder)
        if not silent:
            splash_screen = SplashScreen(self.main_window, len(file_list), title="Loading files")
        else:
            splash_screen = None
        if len(file_list) > 100:
            tkinter.messagebox.showinfo("Suggestion", "Your CombatLogs folder contains a lot of CombatLogs, {0} to be "
                                                      "precise. How about moving them to a nice archive folder? This "
                                                      "will speed up some processes "
                                                      "significantly.".format(len(file_list)))
        self.file_tree.insert("", tk.END, iid="all", text="All CombatLogs")
        file_list = list(reversed(sorted(file_list)) if not self.ascending else sorted(file_list))
        if self.main_window.splash.winfo_exists():
            self.main_window.splash.update_maximum(len(file_list))
        for number, file in enumerate(file_list):
            if not Parser.get_gsf_in_file(file):
                continue
            file_string = Parser.parse_filename(file)
            if file_string is None:
                continue
            self.file_string_dict[file_string] = file
            number += 1
            if splash_screen is not None:
                splash_screen.update_progress(number)
                splash_screen.update()
            self.insert_file(file_string)
            if self.main_window.splash.winfo_exists():
                self.main_window.splash.update_progress(number)
        if splash_screen is not None:
            splash_screen.destroy()
        return

    def insert_file(self, file_string):
        """
        Insert a file into the Treeview list of files and links it to
        an entry in self.file_string_dict
        :param file_string: string representing the file in the list
        """
        if file_string in self.file_string_dict:
            file_name = self.file_string_dict[file_string]
        elif file_string.endswith(".txt"):
            file_name = file_string
        else:
            raise ValueError("Unsupported file_string received: {0}".format(file_string))
        self.file_tree.insert("", tk.END, iid=file_name, text=file_string)
        lines = Parser.read_file(file_name)
        player_list = Parser.get_player_id_list(lines)
        if len(player_list) == 0:
            raise ValueError("Empty player list for file {}".format(file_name))
        file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player_list)
        if len(match_timings) / 2 != len(file_cube):
            raise ValueError("Invalid results for {}\n{}\n{}".format(file_name, file_cube, match_timings))
        match_index = 0
        for match in match_timings[::2]:
            self.file_tree.insert(file_name, tk.END, iid=(file_name, match_index), text=match.strftime("%H:%M"))
            spawn_index = 0
            for spawn in spawn_timings[match_index]:
                self.file_tree.insert((file_name, match_index), tk.END, iid=(file_name, match_index, spawn_index),
                                      text=spawn.strftime("%H:%M:%S"))
                spawn_index += 1
            match_index += 1

    def update_widgets(self, abilities_dict, statistics_string, shipsdict, enemies, enemydamaged,
                       enemydamaget, uncounted):
        """
        This function can update the dta widgets for files, matches and folders
        by updating the widgets of statsframe and shipsframe according to the
        data received from parsing
        :param abilities_dict: abilities dictionary with abilities as keys and amounts as values
        :param statistics_string: string to set in the statistics tab
        :param shipsdict: dictionary with ships as keys and amounts as values
        :param enemies: list of enemy ID numbers
        :param enemydamaged: dictionary with enemies as keys and amounts of damage as values
        :param enemydamaget: dictionary with enemies as keys and amounts of damage as values
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
        This function sets the data widgets for the spawn parsing results
        :param name: player name
        :param spawn: section of CombatLog
        :param abilitiesdict: abilities dictionary with abilities as keys and amounts as values
        :param statistics_string: string to set in the statistics tab
        :param ships_list: list of possible ships
        :param comps: list of ship components
        :param enemies: list of enemy ID numbers
        :param enemydamaged: dictionary with enemies as keys and amounts of damage as values
        :param enemydamaget: dictionary with enemies as keys and amounts of damage as values
        :return: None
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
        self.main_window.middle_frame.time_view.insert_spawn(spawn, name)

    def update_parse(self, *args):
        """
        Callback for the Treeview widget that calls the correct function to load
        a file, match or spawn depending on which is selected.
        :param args: Tkinter event
        """
        try:
            selection = self.file_tree.selection()[0]
        except IndexError:
            return
        elements = selection.split(" ")
        if selection == "all":
            # Whole folder
            print("[FileFrame] Whole folder selected")
            self.parse_folder()
        elif len(elements) is 1:
            # Single file
            self.parse_file(elements[0])
        elif len(elements) is 2:
            # Match
            self.parse_match(elements)
        elif len(elements) is 3:
            # Spawn
            self.parse_spawn(elements)
        else:
            tkinter.messagebox.showerror("Error", "The following invalid amount of elements was detected: {0}. "
                                                  "Please report this error in the GitHub "
                                                  "repository.".format(len(elements)))
            raise ValueError("Invalid value for elements detected {0}".format(len(elements)))

    def parse_file(self, file_name):
        """
        Function either sets the file and calls add_matches to add the matches
        found in the file to the matches_listbox, or starts the parsing of all
        files found in the specified folder and displays the results in the
        other frames.
        :param file_name:
        """
        self.clear_data_widgets()
        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        lines = Parser.read_file(file_name)
        player_list = Parser.get_player_id_list(lines)
        file_cube, _, _ = Parser.split_combatlog(lines, player_list)
        results = filestats.file_statistics(file_name, file_cube)
        self.update_widgets(*results)

    def parse_folder(self):
        """
        Function that initiates the parsing of a whole folder by calling the
        folder_statistics() function and updates the widgets by calling the
        self.update_widgets function accordingly.
        """
        self.clear_data_widgets()
        results = folderstats.folder_statistics()
        self.update_widgets(*results)

    def parse_match(self, elements):
        """
        Either adds sets the match and calls add_spawns to add the spawns found
        in the match or starts the parsing of all files found in the specified
        file and displays the results in the other frames.
        :param elements: specifies file and match
        """
        self.clear_data_widgets()
        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        file_name, match_index = elements[0], int(elements[1])
        lines = Parser.read_file(file_name)
        player_list = Parser.get_player_id_list(lines)
        file_cube, match_timings, _ = Parser.split_combatlog(lines, player_list)
        match = file_cube[match_index]
        results = matchstats.match_statistics(file_name, match, match_timings[::2][match_index])
        self.update_widgets(*results)

    def parse_spawn(self, elements):
        """
        Either starts the parsing of ALL spawns found in the specified match or
        just one of them and displays the results in the other frames
        accordingly.
        """
        self.clear_data_widgets()
        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        file_name, match_index, spawn_index = elements[0], int(elements[1]), int(elements[2])
        lines = Parser.read_file(file_name)
        player_list = Parser.get_player_id_list(lines)
        file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player_list)
        match = file_cube[match_index]
        spawn = match[spawn_index]
        results = spawnstats.spawn_statistics(file_name, spawn, spawn_timings[match_index][spawn_index])
        self.update_widgets_spawn(*results)
        arguments = (file_name, match_timings[::2][match_index], spawn_timings[match_index][spawn_index])
        string = FileHandler.get_features_string(*arguments)
        self.main_window.middle_frame.screen_label_var.set(string)
        self.main_window.middle_frame.update_timeline(
            file_name, match_index, spawn_index, match_timings, spawn_timings, file_cube
        )

    def clear_data_widgets(self):
        """Clear the data widgets for parsing results"""
        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children()
        )
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children()
        )
        self.main_window.ship_frame.ship_label_var.set("")
        self.main_window.middle_frame.screen_label_var.set(
            "Please select an available spawn for screen parsing information"
        )
        self.main_window.middle_frame.time_view.delete(
            *self.main_window.middle_frame.time_view.get_children()
        )
        self.main_window.middle_frame.time_line.delete_marker(tk.ALL)

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

    def get_spawn(self):
        """
        Get the spawn from the selection in the file_tree
        :return: list of event strings, player_list, spawn timing and match timing
        """
        selection = self.file_tree.selection()[0]
        elements = selection.split(" ")
        if len(elements) is not 3:
            tkinter.messagebox.showinfo("Requirement", "Please select a spawn to view the events of.")
            return
        lines = Parser.read_file(elements[0])
        player_list = Parser.get_player_id_list(lines)
        file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player_list)
        match_index, spawn_index = int(elements[1]), int(elements[2])
        return (file_cube[match_index][spawn_index], player_list, spawn_timings[match_index][spawn_index],
                match_timings[match_index])
