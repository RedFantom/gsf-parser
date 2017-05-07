# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk

import tkinter.ttk as ttk
from parsing import abilities
import widgets


class Filters(tk.Toplevel):
    """
    A class for a Toplevel that shows all possible filters that can be applied to CombatLogs. Using expandable frames,
    the settings in a certain category can be shown or hidden. If all settings are set, the user can click OK and a
    special function is called passing a dictionary of files.
    """

    def __init__(self, window=None):
        tk.Toplevel.__init__(self, window)
        self.description_label = ttk.Label(self, text="Please enter the filters you want to apply",
                                           font=("Calibri", 12))
        print("[DEBUG] Setting up Type filters")
        self.type_frame = widgets.ToggledFrame(self, text="Type")
        self.type_variable = tk.StringVar()
        self.type_variable.set("any")
        self.any_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="Any", variable=self.type_variable,
                                         value="any")
        self.logs_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="CombatLogs", variable=self.type_variable,
                                          value="logs")
        self.matches_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="Matches", variable=self.type_variable,
                                             value="matches")
        self.spawns_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="Spawns", variable=self.type_variable,
                                            value="spawns")
        print("[DEBUG] Setting up date filters")
        self.dateframe = widgets.ToggledFrame(self, text="Date")
        self.start_date_widget = widgets.Calendar(self.dateframe.sub_frame)
        self.end_date_widget = widgets.Calendar(self.dateframe.sub_frame)
        print("[DEBUG] Setting up components filters")
        self.components_frame = widgets.ToggledFrame(self, text="Components")
        self.primaries_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Primaries")
        self.secondaries_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Secondaries")
        self.engines_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Engines")
        self.shields_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Shields")
        self.systems_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Sytems")
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
        for primary in abilities.primaries:
            primary_var = tk.IntVar()
            primary_chk = ttk.Checkbutton(self.primaries_frame.sub_frame, text=primary)
            self.primaries_tickboxes[primary] = primary_chk
            self.primaries_tickboxes_vars[primary_chk] = primary_var
        for secondary in abilities.secondaries:
            secondary_var = tk.IntVar()
            secondary_chk = ttk.Checkbutton(self.secondaries_frame.sub_frame, text=secondary)
            self.secondaries_tickboxes[secondary] = secondary_chk
            self.secondaries_tickboxes_vars[secondary_chk] = secondary_var
        for engine in abilities.engines:
            engine_var = tk.IntVar()
            engine_chk = ttk.Checkbutton(self.engines_frame.sub_frame, text=engine)
            self.engines_tickboxes[engine] = engine_chk
            self.engines_tickboxes_vars[engine_chk] = engine_var
        for shield in abilities.shields:
            shield_var = tk.IntVar()
            shield_chk = ttk.Checkbutton(self.shields_frame.sub_frame, text=shield)
            self.shields_tickboxes[shield] = shield_chk
            self.shields_tickboxes_vars[shield_chk] = shield_var
        for system in abilities.systems:
            system_var = tk.IntVar()
            system_chk = ttk.Checkbutton(self.systems_frame.sub_frame, text=system)
            self.systems_tickboxes[system] = system_chk
            self.systems_tickboxes_vars[system_chk] = system_var
        self.comps_dicts = [self.primaries_tickboxes, self.secondaries_tickboxes, self.engines_tickboxes,
                            self.shields_tickboxes, self.systems_tickboxes]
        self.ships_frame = widgets.hoverinfo.ToggledFrame(self, text="Ships")
        print("[DEBUG] Setting up buttons")
        self.complete_button = ttk.Button(self, text="Filter", command=self.filter_files)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.search_button = ttk.Button(self, text="Search", command=self.search_files)
        print("[DEBUG] Gridding widgets")
        self.grid_widgets()

    def filter_files(self):
        pass

    def search_files(self):
        """
        Take the inserted filters and calculate how many files/matches/spawns are found when the filters are applied.
        Display a tkMessageBox.showinfo() box to show the user how many are found and show a splash screen while
        searching.
        :return:
        """
        pass

    def grid_widgets(self):
        self.description_label.grid(row=1, column=1, columnspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.type_frame.grid(row=2, column=1, columnspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.dateframe.grid(row=3, column=1, columnspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.components_frame.grid(row=4, column=1, columnspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.ships_frame.grid(row=5, column=1, columnspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.complete_button.grid(row=6, column=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.search_button.grid(row=6, column=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.cancel_button.grid(row=6, column=3, sticky=tk.N + tk.S + tk.W + tk.E)

        self.any_radio.grid(row=1, column=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.logs_radio.grid(row=1, column=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.matches_radio.grid(row=1, column=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.spawns_radio.grid(row=1, column=4, sticky=tk.N + tk.S + tk.W + tk.E)

        self.start_date_widget.grid(row=1, column=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.end_date_widget.grid(row=1, column=2, sticky=tk.N + tk.S + tk.W + tk.E)

        start_row = 1
        start_column = 1
        for dictionary in self.comps_dicts:
            for widget in dictionary.values():
                widget.grid(row=start_row, column=start_column, sticky=tk.N + tk.W)
                start_column += 1
                if start_column == 6:
                    start_column = 1
                    start_row += 1
            start_row += 1

            # TODO: Ships filters frame
