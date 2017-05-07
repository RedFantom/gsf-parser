# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
try:
    import mttkinter.mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import variables
from toplevels import EventsView


class StatsFrame(ttk.Frame):
    """
    A simple frame containing a notebook with three tabs to show statistics and information to the user
    Main frame:
    ----------------------------------
    |  _____ _____ _____             |
    | |_____|_____|_____|___________ |
    | | frame to display            ||
    | |_____________________________||
    ----------------------------------

    Statistics tab:
    ----------------------------------
    | list                           |
    | of                             |
    | stats                          |
    ----------------------------------

    Enemies tab:
    -----------------------------
    | Help string               |
    | ______ ______ ______ ____ |
    | |enem| |dmgd| |dmgt| |/\| |
    | |enem| |dmgd| |dmgt| |||| |
    | |enem| |dmgd| |dmgt| |\/| |
    | |____| |____| |____| |__| |
    -----------------------------

    Abilities tab:
    -----------------------------
    | ability              |/\| |
    | ability              |||| |
    | ability              |\/| |
    -----------------------------
    """

    def __init__(self, root_frame, main_window):
        """
        Set up all widgets and variables. StringVars can be manipulated by the file frame,
        so that frame can set the statistics to be shown in this frame. Strings for Tkinter
        cannot span multiple lines!
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = main_window
        self.notebook = ttk.Notebook(self, width=300, height=310)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.notebook.add(self.enemies_frame, text="Enemies")
        self.events_frame = ttk.Frame(self, width=300)
        self.events_button = ttk.Button(self.events_frame, text="Show events for spawn", command=self.show_events,
                                        state=tk.DISABLED, width=43)
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt to\nDamage dealt:\nDamage taken:\nDamage ratio:\nSelfdamage:\nHealing received:\n" + \
                 "Hitcount:\nCriticalcount:\nCriticalluck:\nDeaths:\nDuration:\nDPS:"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable=self.statistics_label_var, justify=tk.LEFT,
                                          wraplength=145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable=self.statistics_numbers_var,
                                            justify=tk.LEFT, wraplength=145)
        self.enemies_treeview = ttk.Treeview(self.enemies_frame, columns=("Enemy name/ID", "Damage dealt",
                                                                          "Damage taken"),
                                             displaycolumns=("Enemy name/ID", "Damage dealt", "Damage taken"),
                                             height=14)
        self.enemies_treeview.heading("Enemy name/ID", text="Enemy name/ID",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Enemy name/ID", False, "str"))
        self.enemies_treeview.heading("Damage dealt", text="Damage dealt",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Damage dealt", False, "int"))
        self.enemies_treeview.heading("Damage taken", text="Damage taken",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Damage taken", False, "int"))
        self.enemies_treeview["show"] = "headings"
        self.enemies_treeview.column("Enemy name/ID", width=125, stretch=False, anchor=tk.W)
        self.enemies_treeview.column("Damage taken", width=80, stretch=False, anchor=tk.E)
        self.enemies_treeview.column("Damage dealt", width=80, stretch=False, anchor=tk.E)
        self.enemies_scrollbar = ttk.Scrollbar(self.enemies_frame, orient=tk.VERTICAL,
                                               command=self.enemies_treeview.yview)
        self.enemies_treeview.config(yscrollcommand=self.enemies_scrollbar.set)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.abilities_frame, text="Abilities")
        self.abilities_treeview = ttk.Treeview(self.abilities_frame, columns=("Ability", "Times used"),
                                               displaycolumns=("Ability", "Times used"), height=14)
        self.abilities_treeview.column("Ability", width=200, stretch=False, anchor=tk.W)
        self.abilities_treeview.column("Times used", width=85, stretch=False, anchor=tk.E)
        self.abilities_treeview.heading("Ability", text="Ability",
                                        command=lambda: self.treeview_sort_column(self.abilities_treeview,
                                                                                  "Ability", False, "str"))
        self.abilities_treeview.heading("Times used", text="Times used",
                                        command=lambda: self.treeview_sort_column(self.abilities_treeview,
                                                                                  "Times used", False, "int"))
        self.abilities_treeview["show"] = "headings"
        self.abilities_scrollbar = ttk.Scrollbar(self.abilities_frame, orient=tk.VERTICAL,
                                                 command=self.abilities_treeview.yview)
        self.abilities_treeview.config(yscrollcommand=self.abilities_scrollbar.set)
        self.notice_label = ttk.Label(self.stats_frame, text="\n\n\n\nThe damage dealt for bombers can not be " +
                                                             "accurately calculated due to CombatLog limitations, "
                                                             "as damage dealt by bombs is not recorded.",
                                      justify=tk.LEFT, wraplength=290)

    def show_events(self):
        """
        Open a TopLevel of the overlay module to show the lines of a Combatlog in a human-readable manner
        :return:
        """
        self.toplevel = EventsView(self.window, variables.spawn, variables.player_numbers)

    def grid_widgets(self):
        """
        Put all widgets in the right place
        :return:
        """
        self.abilities_treeview.grid(column=0, row=0, sticky=tk.N + tk.W)
        self.abilities_scrollbar.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.notebook.grid(column=0, row=0, columnspan=4, sticky=tk.N + tk.W + tk.E)
        self.events_frame.grid(column=0, row=1, columnspan=4, sticky=tk.N + tk.S + tk.W + tk.E)
        self.events_button.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E, columnspan=4, pady=12)
        self.statistics_label.grid(column=0, row=2, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.statistics_numbers.grid(column=2, row=2, columnspan=2, sticky=tk.N + tk.W + tk.E)
        self.notice_label.grid(column=0, row=3, columnspan=4, sticky=tk.W + tk.E + tk.S)
        self.enemies_treeview.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.enemies_scrollbar.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)

    def treeview_sort_column(self, treeview, column, reverse, type):
        l = [(treeview.set(k, column), k) for k in treeview.get_children('')]
        if type == "int":
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        elif type == "str":
            l.sort(key=lambda t: t[0], reverse=reverse)
        else:
            raise NotImplementedError
        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)
        treeview.heading(column, command=lambda: self.treeview_sort_column(treeview, column, not reverse, type))