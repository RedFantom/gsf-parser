"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
# UI Libraries
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from ttkwidgets import Calendar, ScaleEntry
# Project Modules
import variables
from parsing.parser import Parser
from widgets import ToggledFrame, VerticalScrollFrame
from toplevels import splash
from data import abilities as abls


class Filters(tk.Toplevel):
    """
    A class for a Toplevel that shows all possible filters that can be
    applied to CombatLogs. Using expandable frames, the settings in a
    certain category can be shown or hidden. If all settings are set,
    the user can click OK and a special function is called passing a
    dictionary of files.
    """

    def __init__(self, window=None):
        tk.Toplevel.__init__(self, window)
        self.wm_geometry("670x400")
        self.window = window if window is not None else variables.main_window
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
        print("[Filters] Setting up Type filters")
        self.type_frame = ToggledFrame(self.scroll_frame.interior, text="Type", labelwidth=90)
        print("[Filters] Setting up date filters")
        self.date_frame = ToggledFrame(self.scroll_frame.interior, text="Date", labelwidth=90)
        self.start_date_label = ttk.Label(self.date_frame.sub_frame, text="Start date", font=("default", 12),
                                          justify=tk.CENTER)
        self.end_date_label = ttk.Label(self.date_frame.sub_frame, text="End date", font=("default", 12),
                                        justify=tk.CENTER)
        self.start_date_widget = Calendar(self.date_frame.sub_frame)
        self.end_date_widget = Calendar(self.date_frame.sub_frame)

        print("[Filters] Setting up components filters")
        self.components_frame = ToggledFrame(self.scroll_frame.interior, text="Components", labelwidth=90)
        self.component_values = {"variables": dict(), "widgets": dict(), "frames": dict()}
        component_types = ("Primaries", "Secondaries", "Engines", "Shields", "Systems")
        for category in component_types:
            self.component_values["frames"][category] = ToggledFrame(
                self.components_frame.sub_frame, text=category, labelwidth=90)
            for key in ("variables", "widgets"):
                self.component_values[key][category] = dict()
            components = getattr(abls, category.lower())
            for component in components:
                self.component_values["variables"][category][component] = tk.BooleanVar()
                self.component_values["widgets"][category][component] = ttk.Checkbutton(
                    self.component_values["frames"][category].sub_frame, text=component,
                    variable=self.component_values["variables"][category][component], width=20)
        self.comps_dicts = [component for component in self.component_values["widgets"].values()]
        self.comps_vars = [component for component in self.component_values["variables"].values()]

        self.ships_frame = ToggledFrame(self.scroll_frame.interior, text="Ships", labelwidth=90)
        self.ships_checkboxes = {}
        self.ships_intvars = {}
        if variables.settings["gui"]["faction"] == "empire":
            for name in abls.rep_ships.keys():
                self.ships_intvars[name] = tk.IntVar()
                self.ships_checkboxes[name] = ttk.Checkbutton(self.ships_frame.sub_frame, text=name,
                                                              variable=self.ships_intvars[name], width=12)
        elif variables.settings["gui"]["faction"] == "republic":
            for name in abls.rep_ships.values():
                self.ships_intvars[name] = tk.IntVar()
                self.ships_checkboxes[name] = ttk.Checkbutton(self.ships_frame.sub_frame, text=name,
                                                              variable=self.ships_intvars[name], width=12)
        else:
            raise ValueError("No valid faction found.")

        self.statistics_frame = ToggledFrame(self.scroll_frame.interior, text="Statistics", labelwidth=90)
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
            self.statistics_scales_max[stat] = ScaleEntry(
                self.statistics_frame.sub_frame, from_=self.statistics_limits[stat][0],
                to=self.statistics_limits[stat][1], scalewidth=150, entrywidth=7)
            self.statistics_scales_min[stat] = ScaleEntry(
                self.statistics_frame.sub_frame, from_=self.statistics_limits[stat][0],
                to=self.statistics_limits[stat][1], scalewidth=150, entrywidth=7)

        self.complete_button = ttk.Button(self, text="Filter", command=self.filter)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.search_button = ttk.Button(self, text="Search", command=self.search)
        print("[Filters] Gridding widgets")
        self.grid_widgets()

    def search_files(self):
        """
        Take the inserted filters and calculate how many
        files/matches/spawns are found when the filters are applied.
        Display a tkMessageBox.showinfo() box to show the user how many
        are found and show a splash screen while searching.
        """
        pass

    def search(self):
        self.filter(search=True)

    def filter(self, search=False):
        """
        Go through all file filters and apply them to the list of files
        in the CombatLogs folder. Insert them into the file_frame
        file_tree widget when the file passed the filters.
        :param search: if search is True, the function will calculate
            the amount of files found and ask the user whether the
            results should be displayed first
        """
        # logs, matches or spawns
        results = []
        files = os.listdir(variables.settings["parsing"]["path"])
        files_done = 0
        splash = splash.SplashScreen(self, len(files))
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
            if not file_name.endswith(".txt") or not Parser.get_gsf_in_file(file_name):
                continue
            # Open the CombatLog
            lines = Parser.read_file(file_name)
            # Parse the CombatLog to get the data to filter against
            player_list = Parser.get_player_id_list(lines)
            file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player_list)
            (abilities, damagedealt, damagetaken, selfdamage, healing, _, _, _, _,
             enemy_dmg_d, enemy_dmg_t, _, _) = Parser.parse_file(file_cube, player_list)
            matches = len(file_cube)
            damagedealt, damagetaken, selfdamage, healing = (
                damagedealt / matches,
                damagetaken / matches,
                selfdamage / matches,
                healing / matches
            )
            # If Ship filters are enabled, check file against ship filters
            if self.filter_type_vars["Ships"].get() is True:
                print("Ships filters are enabled")
                if not self.check_ships_file(self.ships_intvars, abilities):
                    print("Continuing in file {0} because of Ships".format(file_name))
                    continue

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
                date = Parser.parse_filename(file_name)
                if not date:
                    print("Continuing in file {0} because the filename could not be parsed".format(file_name))
                    continue
                if self.start_date_widget.selection > date:
                    print("Continuing in file {0} because of the start date".format(file_name))
                    continue
                if self.end_date_widget.selection < date:
                    print("Continuing in file {0} because of the end date".format(file_name))
                    continue

            enemies = sum(True if dmg > 0 else False for dmg in enemy_dmg_d.values())
            killassists = sum(True if dmg > 0 else False for dmg in enemy_dmg_t.values())

            if self.filter_type_vars["Statistics"].get() is True:
                for (scale_type, scale_max), (_, scale_min) in \
                        zip(self.statistics_scales_max.items(), self.statistics_scales_min.items()):
                    value = locals()[scale_type]
                    min, max = scale_min.value, scale_max.value
                    condition = min <= value <= max if max > min else min <= value
                    if condition is False:
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

        for file_name in results:
            datetime_obj = Parser.parse_filename(file_name)
            string = datetime_obj.strftime("%Y-%m-%d   %H:%M") if datetime_obj is not None else file_name
            print("Setting file string {0} to match file_name {1}".format(string, file_name))
            self.window.file_select_frame.file_string_dict[string] = file_name
            self.window.file_select_frame.insert_file(string)
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
        self.date_frame.grid(row=3, column=1, columnspan=len(self.filter_types), sticky="nswe")
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

        for index, frame in enumerate(self.component_values["frames"].values()):
            frame.grid(row=index, column=0, sticky="nswe")

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
                ships_list = Parser.get_ship_for_dict(dict)
                print(ships_list)
                for ship, intvar in dictionary.items():
                    if intvar.get() == 1:
                        print("Required: ", ship)
                        if variables.settings["gui"]["faction"] == "empire":
                            pass
                        elif variables.settings["gui"]["faction"] == "republic":
                            ships_list = [abls.rep_ships[name] for name in ships_list]
                        else:
                            raise ValueError("faction found not valid")
                        if ship in ships_list:
                            return True
        return False


class LimitedIntVar(tk.IntVar):
    """
    Subclass of tk.IntVar that constrains the value set to a maximum and
    minimum value.
    """

    def __init__(self, low: int, high: int):
        """
        :param low: Lower limit
        :param high: Higher limit
        """
        self._low = low
        self._high = high
        tk.IntVar.__init__(self, value=low)

    def set(self, value: (str, int)):
        """
        Set the value constrained by the limits.
        :param value: int or valid str literal for int
        """
        if not isinstance(value, int) and not value.isdigit():
            raise ValueError("value argument passed is not int and cannot be converted to int")
        if isinstance(value, str):
            value = int(value)
        limited_value = max(min(self._high, value), self._low)
        tk.IntVar.set(self, limited_value)
        # Return False if the value had to be limited
        return limited_value == value
