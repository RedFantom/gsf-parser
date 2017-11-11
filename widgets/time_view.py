# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI modules
import tkinter as tk
from tkinter import ttk
# Own modules
from parsing.parser import Parser

import variables


class TimeView(ttk.Treeview):
    """
    A Treeview that contains a list of events in a good and formatted way
    """
    def __init__(self, *args, **kwargs):
        """
        All arguments are passed to the initialization of the Treeview
        """
        kwargs.update({
            "columns": ("time", "source", "target", "ability", "amount"),
            "show": ("headings", "tree")
        })
        ttk.Treeview.__init__(self, *args, **kwargs)
        color_scheme = variables.color_scheme.current_scheme
        for category in color_scheme.keys():
            self.tag_configure(category, foreground=color_scheme[category][0], background="gray25")
        for column in kwargs["columns"]:
            self.heading(column, text=column.title())
        self.setup_columns()

    def setup_columns(self):
        """
        Setup the Treeview with the correct widths and tags
        """
        # self.enemies_treeview.column("Damage taken", width=125, anchor="e")
        self.column("#0", width=40)
        self.column("time", width=60)
        self.column("source", width=105)
        self.column("target", width=105)
        self.column("ability", width=155)
        self.column("amount", width=50)

    def insert_event(self, line_dict, player_name, active_ids, start_time):
        """
        Insert a new line into the Treeview
        :param line_dict: line dictionary (Parser.line_to_dictionary)
        :return: None
        """
        values = (
            TimeView.format_time_diff(line_dict["time"], start_time),
            player_name if Parser.compare_ids(line_dict["source"], active_ids) else line_dict["source"],
            player_name if Parser.compare_ids(line_dict["destination"], active_ids) else line_dict["destination"],
            line_dict["ability"].strip(),
            line_dict["amount"]
        )
        tag = Parser.get_event_category(line_dict, active_ids)
        if tag is None:
            return
        self.insert("", tk.END, values=values, tags=(tag,))

    def insert_spawn(self, spawn, player_name):
        """
        Insert the events of a spawn into the Treeview
        :param spawn: A set of lines or line_dicts
        :param player_name: player name str
        :return: None
        """
        if len(spawn) == 0:
            raise ValueError("Invalid spawn passed.")
        spawn = spawn if isinstance(spawn[0], dict) else [Parser.line_to_dictionary(line) for line in spawn]
        start_time = spawn[0]["time"]
        active_ids = Parser.get_player_id_list(spawn)
        for line_dict in spawn:
            self.insert_event(line_dict, player_name, active_ids, start_time)
        """
        spawn, player_numbers, spawn_timing, match_timing = self.window.file_select_frame.get_spawn()
        """

    @staticmethod
    def format_time_diff(time, start_time):
        """
        Format the time difference between two times in a nice manner
        :param time: time the event occurs
        :param start_time: time the match or spawn has started
        :return: a formatted string of the time difference
        """
        delta = time - start_time
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d" % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
        return string



