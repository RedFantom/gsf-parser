# -*- coding: utf-8 -*-
#
# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import os
# Own modules
import widgets
import variables
import parsing.parse as parse
from widgets.verticalscrollframe import VerticalScrollFrame
from widgets import ScaleEntry
from . import splashscreens
from parsing import abilities as abls
from parsing.parse import parse_file_name


class Filters(tk.Toplevel):
    """
    A class for a Toplevel that shows all possible filters that can be applied to CombatLogs. Using expandable frames,
    the settings in a certain category can be shown or hidden. If all settings are set, the user can click OK and a
    special function is called passing a dictionary of files.
    """

    def __init__(self, window=None):
        tk.Toplevel.__init__(self, window)
        self.wm_geometry("670x400")
        if window:
            self.window = window
        else:
            self.window = variables.main_window
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=670, canvasheight=355)

        self.wm_resizable(False, False)
        self.description_label = ttk.Label(self.scroll_frame.interior,
                                           text="Please enter the filters you want to apply",
                                           font=("Calibri", 12))
        self.filter_types = ["Date", "Components", "Ships", "Statistics"]
        self.filter_type_checkbuttons = []
        self.filter_type_vars = {}
        for type in self.filter_types:
            self.filter_type_vars[type] = tk.BooleanVar()
            self.filter_type_checkbuttons.append(
                ttk.Checkbutton(self.scroll_frame.interior, text=type, variable=self.filter_type_vars[type]))
        print("[DEBUG] Setting up Type filters")
        self.type_frame = widgets.ToggledFrame(self.scroll_frame.interior, text="Type", labelwidth=90)
        print("[DEBUG] Setting up date filters")
        self.dateframe = widgets.ToggledFrame(self.scroll_frame.interior, text="Date", labelwidth=90)
        self.start_date_label = ttk.Label(self.dateframe.sub_frame, text="Start date", font=("default", 12),
                                          justify=tk.CENTER)
        self.end_date_label = ttk.Label(self.dateframe.sub_frame, text="End date", font=("default", 12),
                                        justify=tk.CENTER)
        self.start_date_widget = widgets.Calendar(self.dateframe.sub_frame)
        self.end_date_widget = widgets.Calendar(self.dateframe.sub_frame)
        print("[DEBUG] Setting up components filters")
        self.components_frame = widgets.ToggledFrame(self.scroll_frame.interior, text="Components", labelwidth=90)
        self.primaries_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Primaries", labelwidth=90)
        self.secondaries_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Secondaries",
                                                      labelwidth=90)
        self.engines_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Engines", labelwidth=90)
        self.shields_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Shields", labelwidth=90)
        self.systems_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Sytems", labelwidth=90)
        self.primaries_tickboxes = {}
        self.primaries_tickboxes_vars = {}
        self.secondaries_tickboxes = {}
        self.secondaries_tickboxes_vars = {}
        self.engines_tickboxes = {}
        self.engines_tickboxes_vars = {}
        self.shields_tickboxes = {}
        self.shields_tickboxes_vars = {}
        self.systems_tickboxes = {}
        self.systems_tickboxes_vars = {}
        for primary in abls.primaries:
            primary_var = tk.IntVar()
            primary_chk = ttk.Checkbutton(self.primaries_frame.sub_frame, text=primary, variable=primary_var,
                                          width=20)
            self.primaries_tickboxes[primary] = primary_chk
            self.primaries_tickboxes_vars[primary] = primary_var
        for secondary in abls.secondaries:
            secondary_var = tk.IntVar()
            secondary_chk = ttk.Checkbutton(self.secondaries_frame.sub_frame, text=secondary,
                                            variable=secondary_var,
                                            width=20)
            self.secondaries_tickboxes[secondary] = secondary_chk
            self.secondaries_tickboxes_vars[secondary] = secondary_var
        for engine in abls.engines:
            engine_var = tk.IntVar()
            engine_chk = ttk.Checkbutton(self.engines_frame.sub_frame, text=engine, variable=engine_var,
                                         width=20)
            self.engines_tickboxes[engine] = engine_chk
            self.engines_tickboxes_vars[engine] = engine_var
        for shield in abls.shields:
            shield_var = tk.IntVar()
            shield_chk = ttk.Checkbutton(self.shields_frame.sub_frame, text=shield, variable=shield_var,
                                         width=20)
            self.shields_tickboxes[shield] = shield_chk
            self.shields_tickboxes_vars[shield] = shield_var
        for system in abls.systems:
            system_var = tk.IntVar()
            system_chk = ttk.Checkbutton(self.systems_frame.sub_frame, text=system, variable=system_var,
                                         width=20)
            self.systems_tickboxes[system] = system_chk
            self.systems_tickboxes_vars[system] = system_var
        self.comps_dicts = [self.primaries_tickboxes, self.secondaries_tickboxes, self.engines_tickboxes,
                            self.shields_tickboxes, self.systems_tickboxes]
        self.comps_vars = [self.primaries_tickboxes_vars, self.secondaries_tickboxes_vars, self.engines_tickboxes_vars,
                           self.shields_tickboxes_vars, self.systems_tickboxes_vars]

        self.ships_frame = widgets.ToggledFrame(self.scroll_frame.interior, text="Ships", labelwidth=90)
        self.ships_checkboxes = {}
        self.ships_intvars = {}
        if variables.settings_obj["gui"]["faction"] == "imperial":
            for name in abls.rep_ships.keys():
                self.ships_intvars[name] = tk.IntVar()
                self.ships_checkboxes[name] = ttk.Checkbutton(self.ships_frame.sub_frame, text=name,
                                                              variable=self.ships_intvars[name], width=12)
        elif variables.settings_obj["gui"]["faction"] == "republic":
            for name in abls.rep_ships.values():
                self.ships_intvars[name] = tk.IntVar()
                self.ships_checkboxes[name] = ttk.Checkbutton(self.ships_frame.sub_frame, text=name,
                                                              variable=self.ships_intvars[name], width=12)
        else:
            raise ValueError("No valid faction found.")

        self.statistics_frame = widgets.ToggledFrame(self.scroll_frame.interior, text="Statistics", labelwidth=90)
        self.statistics_header_label = ttk.Label(self.statistics_frame.sub_frame,
                                                 text="All statistics are averages per match, if the maximum is set to "
                                                      "zero the setting is ignored.")
        self.statistics_max_label = ttk.Label(self.statistics_frame.sub_frame, text="Maximum")
        self.statistics_min_label = ttk.Label(self.statistics_frame.sub_frame, text="Minimum")

        self.statistics = ["damagedealt", "damagetaken", "selfdamage", "healing", "killassists", "enemies"]
        self.statistics_dict = {
            "damagedealt": "Damage dealt: ",
            "damagetaken": "Damage taken: ",
            "selfdamage": "Selfdamage: ",
            "healing": "Healing received: ",
            "killassists": "Enemies damage dealt to: ",
            "enemies": "Enemies damage taken from: "
        }
        self.statistics_limits = {
            "damagedealt": (0, 200000),
            "damagetaken": (0, 200000),
            "selfdamage": (0, 50000),
            "healing": (0, 20000),
            "killassists": (0, 100),
            "enemies": (0, 100)
        }

        self.statistics_scales_max = {}
        self.statistics_labels = {}
        self.statistics_scales_min = {}

        for stat in self.statistics:
            self.statistics_labels[stat] = ttk.Label(self.statistics_frame.sub_frame, text=self.statistics_dict[stat])
            self.statistics_scales_max[stat] = ScaleEntry(self.statistics_frame.sub_frame,
                                                          from_=self.statistics_limits[stat][0],
                                                          to=self.statistics_limits[stat][1], scalewidth=150,
                                                          entrywidth=7)
            self.statistics_scales_min[stat] = ScaleEntry(self.statistics_frame.sub_frame,
                                                          from_=self.statistics_limits[stat][0],
                                                          to=self.statistics_limits[stat][1], scalewidth=150,
                                                          entrywidth=7)

        self.complete_button = ttk.Button(self, text="Filter", command=self.filter)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.search_button = ttk.Button(self, text="Search", command=self.search)
        print("[DEBUG] Gridding widgets")
        self.grid_widgets()

    def search_files(self):
        """
        Take the inserted filters and calculate how many files/matches/spawns are found when the filters are applied.
        Display a tkMessageBox.showinfo() box to show the user how many are found and show a splash screen while
        searching.
        :return:
        """
        pass

    def search(self):
        self.filter(search=True)

    def filter(self, search=False):
        """
        Go through all file filters and apply them to the list of files in the CombatLogs folder. Insert them into the
        file_frame file_tree widget when the file passed the filters.
        :param search: if search is True, the function will calculate the amount of files found and ask the user whether
                       the results should be displayed first
        :return: None
        """
        # logs, matches or spawns
        results = []
        files = os.listdir(variables.settings_obj["parsing"]["path"])
        files_done = 0
        splash = splashscreens.SplashScreen(self, len(files))
        # Clear the widgets in the file frame
        self.window.file_select_frame.file_string_dict.clear()
        self.window.file_select_frame.clear_data_widgets()
        self.window.file_select_frame.file_tree.delete(*self.window.file_select_frame.file_tree.get_children())
        # Start looping over the files in the CombatLogs folder
        for file_name in files:
            # Set passed to True. Will be set to False in some filter code
            passed = True
            # Update the SplashScreen progress bar
            files_done += 1
            splash.update_progress(files_done)
            # If the file does not end with .txt, it's not a CombatLog
            if not file_name.endswith(".txt"):
                continue
            if not parse.check_gsf(file_name):
                continue
            # Open the CombatLog
            with open(os.path.join(variables.settings_obj["parsing"]["path"], file_name)) as f:
                lines = f.readlines()
            # Parse the CombatLog to get the data to filter against
            player_list = parse.determinePlayer(lines)
            file_cube, match_timings, spawn_timings = parse.splitter(lines, player_list)
            (abilities, damagetaken, damagedealt,
             selfdamage, healingreceived, enemies,
             criticalcount, criticalluck, hitcount,
             enemydamaged, enemydamaget, match_timings,
             spawn_timings) = parse.parse_file(file_cube, player_list, match_timings, spawn_timings)
            # Calculate the averages
            damagetaken = self.file_number(damagetaken)
            damagedealt = self.file_number(damagedealt)
            selfdamage = self.file_number(selfdamage)
            healingreceived = self.file_number(healingreceived)

            # If Ship filters are enabled, check file against ship filters
            if self.filter_type_vars["Ships"].get() is True:
                print("Ships filters are enabled")
                if not self.check_ships_file(self.ships_intvars, abilities):
                    print("Continuing in file {0} because of Ships".format(file_name))
                    continue
            # If the file got this far, then get the abilities dictionary
            abilities = self.file_dictionary(abilities)

            # If the Components filters are enabled, check against Components filters
            if self.filter_type_vars["Components"].get() is True:
                print("Components filters are enabled")
                for dictionary in self.comps_vars:
                    if not self.check_components(dictionary, abilities):
                        # Passed is applied here as "continue" will not work inside this for loop
                        passed = False
                        break
                if not passed:
                    print("Continuing in file {0} because of Components".format(file_name))
                    continue

            if self.filter_type_vars["Date"].get() is True:
                print("Date filters are enabled")
                date = parse_file_name(file_name)
                if not date:
                    print("Continuing in file {0} because the filename could not be parsed".format(file_name))
                    continue
                if self.start_date_widget.selection > date:
                    print("Continuing in file {0} because of the start date".format(file_name))
                    continue
                if self.end_date_widget.selection < date:
                    print("Continuing in file {0} because of the end date".format(file_name))
                    continue

            if self.filter_type_vars["Statistics"].get() is True:
                if self.statistics_scales_max["damagedealt"].value is not 0:
                    if not self.statistics_scales_max["damagedealt"].value >= damagedealt:
                        print("Continuing in file {0} because of damagedealt max".format(file_name))
                        continue
                    if not self.statistics_scales_min["damagedealt"].value <= damagedealt:
                        print("Continuing in file {0} because of damagedealt min".format(file_name))
                        continue
                if self.statistics_scales_max["damagetaken"].value is not 0:
                    if not self.statistics_scales_max["damagetaken"].value >= damagetaken:
                        print("Continuing in file {0} because of damagetaken max".format(file_name))
                        continue
                    if not self.statistics_scales_min["damagetaken"].value <= damagetaken:
                        print("Continuing in file {0} because of damagetaken min".format(file_name))
                        continue
                if self.statistics_scales_max["selfdamage"].value is not 0:
                    if not self.statistics_scales_max["selfdamage"].value >= selfdamage:
                        print("Continuing in file {0} because of selfdamage max".format(file_name))
                        continue
                    if not self.statistics_scales_min["selfdamage"].value <= selfdamage:
                        print("Continuing in file {0} because of selfdamage min".format(file_name))
                        continue
                if self.statistics_scales_max["healing"].value is not 0:
                    if not self.statistics_scales_max["healing"].value >= healingreceived:
                        print("Continuing in file {0} because of healing max".format(file_name))
                        continue
                    if not self.statistics_scales_min["healing"].value <= healingreceived:
                        print("Continuing in file {0} because of healing min".format(file_name))
                        continue
                if self.statistics_scales_max["enemies"].value is not 0:
                    if not self.statistics_scales_max["enemies"].value >= len(enemydamaget):
                        print("Continuing in file {0} because of enemies max".format(file_name))
                        continue
                    if not self.statistics_scales_min["enemies"].value <= len(enemydamaget):
                        print("Continuing in file {0} because of enemies min".format(file_name))
                        continue
                if self.statistics_scales_max["killassists"].value is not 0:
                    if not self.statistics_scales_max["killassists"].value >= len(enemydamaged):
                        continue
                    if not self.statistics_scales_min["killassists"].value <= len(enemydamaged):
                        continue

            results.append(file_name)
        print("Amount of results: {0}".format(len(results)))
        print("Results: {0}".format(results))
        splash.destroy()
        if search and len(results) is not 0:
            print("Search is enabled")
            if not tkinter.messagebox.askyesno("Search results",
                                               "With the filters you specified, %s results were found. Would you like "
                                               "to view them?" % len(results)):
                return
        if len(results) == 0:
            tkinter.messagebox.showinfo("Search results",
                                        "With the filters you specified, no results were found.")
            return
        else:
            for file_name in results:
                datetime_obj = parse.parse_file_name(file_name)
                if datetime_obj:
                    string = datetime_obj.strftime("%Y-%m-%d   %H:%M" if variables.settings_obj["gui"]["date_format"]
                                                                         is "ymd" else "%Y-%d-%m   %H:%M")
                else:
                    string = file_name
                print("Setting file string {0} to match file_name {1}".format(string, file_name))
                self.window.file_select_frame.file_string_dict[string] = file_name
                try:
                    self.window.file_select_frame.insert_file(string)
                except tk.TclError as e:
                    print(e)
        self.destroy()

    def grid_widgets(self):
        self.description_label.grid(row=0, column=1, columnspan=len(self.filter_types),
                                    sticky="nswe")
        self.scroll_frame.grid(row=1, column=1, columnspan=6, sticky="nswe")
        set_column = 1
        for widget in self.filter_type_checkbuttons:
            widget.grid(row=1, column=set_column, sticky="w")
            set_column += 1
        # self.type_frame.grid(row=2, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.dateframe.grid(row=3, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.components_frame.grid(row=4, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.ships_frame.grid(row=5, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.statistics_frame.grid(row=6, column=1, columnspan=len(self.filter_types), sticky="nswe")

        self.complete_button.grid(row=2, column=1, sticky="nswe", pady=5, padx=5)
        self.search_button.grid(row=2, column=2, sticky="nswe", pady=5, padx=(0, 5))
        self.cancel_button.grid(row=2, column=3, sticky="nswe", pady=5, padx=(0, 5))

        self.start_date_label.grid(row=0, column=1, sticky="we")
        self.end_date_label.grid(row=0, column=2, sticky="we")
        self.start_date_widget.grid(row=1, column=1, sticky="nswe")
        self.end_date_widget.grid(row=1, column=2, sticky="nswe")

        self.primaries_frame.grid(row=0, column=0, sticky="nswe")
        self.secondaries_frame.grid(row=1, column=0, sticky="nswe")
        self.engines_frame.grid(row=2, column=0, sticky="nswe")
        self.shields_frame.grid(row=3, column=0, sticky="nswe")
        self.systems_frame.grid(row=4, column=0, sticky="nswe")

        start_row = 1
        start_column = 1
        for dictionary in self.comps_dicts:
            for widget in dictionary.values():
                widget.grid(row=start_row, column=start_column, sticky="w" + tk.N)
                start_column += 1
                if start_column == 4:
                    start_column = 1
                    start_row += 1
            start_row = 1
            start_column = 1
            start_row += 1

        set_row = 1
        set_column = 1
        for widget in self.ships_checkboxes.values():
            widget.grid(row=set_row, column=set_column, sticky="nw")
            set_column += 1
            if set_column == 6:
                set_column = 1
                set_row += 1

        self.statistics_header_label.grid(row=1, column=1, columnspan=5, sticky="w", padx=5, pady=5)
        self.statistics_max_label.grid(row=2, column=4, sticky="w", pady=(0, 5), padx=5)
        self.statistics_min_label.grid(row=2, column=2, sticky="w", pady=(0, 5), padx=5)
        set_row = 3
        for stat in self.statistics:
            self.statistics_labels[stat].grid(row=set_row, column=1, sticky="nw", padx=5, pady=(0, 5))
            self.statistics_scales_min[stat].grid(row=set_row, column=2, sticky="nw", padx=5, pady=(0, 5))
            self.statistics_scales_max[stat].grid(row=set_row, column=4, sticky="nw", padx=5, pady=(0, 5))
            set_row += 1
        return

    @staticmethod
    def file_dictionary(abilities):
        return_value = {}
        for abl_list in abilities:
            for abl in abl_list:
                return_value.update(abl)
        return return_value

    @staticmethod
    def file_number(matrix):
        return_value = 0
        for list in matrix:
            return_value += sum(list)
        try:
            return return_value / len(matrix)
        except ZeroDivisionError:
            return 0

    @staticmethod
    def check_components(dictionary, abilities):
        for component, intvar in dictionary.items():
            if intvar.get() is 0:
                continue
            if component not in abilities:
                return False
        return True

    @staticmethod
    def check_ships_file(dictionary, abilities):
        for list in abilities:
            for dict in list:
                ships_list = parse.determineShip(dict)
                print(ships_list)
                for ship, intvar in dictionary.items():
                    if intvar.get() == 1:
                        print("Required: ", ship)
                        if variables.settings_obj["gui"]["faction"] == "imperial":
                            pass
                        elif variables.settings_obj["gui"]["faction"] == "republic":
                            ships_list = [abls.rep_ships[name] for name in ships_list]
                        else:
                            raise ValueError("faction found not valid")
                        if ship in ships_list:
                            return True
        return False


class LimitedIntVar(tk.IntVar):
    """
    Subclass of tk.IntVar that allows limits in the value of the variable stored
    """

    def __init__(self, low, high):
        self._low = low
        self._high = high
        tk.IntVar.__init__(self, value=low)

    def set(self, value):
        """
        Set a new value, but check whether it is in limits first. If not, return False and set the new value to
        either be the minimum (if value is smaller than the minimum) or the maximum (if the value is larger than
        the maximum). Both str and int are supported as value types, as long as the str contains an int.
        """
        if not isinstance(value, int):
            try:
                value = int(value)
            except ValueError:
                raise ValueError("value argument passed is not int and cannot be converted to int")
        limited_value = max(min(self._high, value), self._low)
        tk.IntVar.set(self, limited_value)
        # Return False if the value had to be limited
        return limited_value is value
