# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI modules
import tkinter as tk
from tkinter import ttk
# General modules
from PIL import Image
from PIL.ImageTk import PhotoImage
import os
# Own modules
from parsing.parser import Parser
from parsing.icons import icons
from tools.utilities import get_assets_directory
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
        self.icons = {}
        for icon, file_name in icons.items():
            path = os.path.join(
                get_assets_directory(), "icons", file_name + (".jpg" if not file_name.endswith(".png") else "")
            )
            image = Image.open(path)
            self.icons[icon] = PhotoImage(image.resize((24, 24), Image.ANTIALIAS), master=self)
        self.style = ttk.Style(self)
        self.style.configure("TimeView.Treeview", rowheight=32)
        self.config(style="TimeView.Treeview")
        self.index = 0

    def setup_columns(self):
        """
        Setup the Treeview with the correct widths and tags
        """
        # self.enemies_treeview.column("Damage taken", width=125, anchor="e")
        self.column("#0", width=40, anchor=tk.W)
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
        if line_dict["type"] == Parser.LINE_EFFECT:
            return
        values = (
            TimeView.format_time_diff(line_dict["time"], start_time),
            player_name if Parser.compare_ids(line_dict["source"], active_ids) else line_dict["source"],
            player_name if Parser.compare_ids(line_dict["destination"], active_ids) else line_dict["destination"],
            line_dict["ability"],
            line_dict["amount"]
        )
        tag = Parser.get_event_category(line_dict, active_ids)
        if line_dict["ability"] not in self.icons:
            print("Icon for ability '{}' is missing.".format(line_dict["ability"]))
            image = self.icons["default"]
        else:
            image = self.icons[line_dict["ability"]]
        iid = (repr(line_dict["time"]) + line_dict["source"] + line_dict["target"] +
               line_dict["effect"] + str(self.index))
        self.insert("", tk.END, values=values, tags=(tag,), image=image, iid=iid)
        self.index += 1
        if line_dict["effects"] is None:
            return
        values = (
            "",
            player_name,
            str(len(line_dict["effects"])) + \
                (" Allies" if Parser.get_effect_allied(line_dict["ability"]) else " Enemies"),
            line_dict["ability"],
            line_dict["amount"]
        )
        self.insert(iid, tk.END, values=values, tags=(tag,))
        for effect in line_dict["effects"]:
            values = TimeView.get_treeview_values(effect, player_name, start_time, active_ids)
            self.insert(iid, tk.END, values=values, tags=(tag,))

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
            line_event_dict = Parser.line_to_event_dictionary(line_dict, active_ids, spawn)
            self.insert_event(line_event_dict, player_name, active_ids, start_time)

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

    @staticmethod
    def get_treeview_values(line_dict, player_name, start_time, active_ids):
        """
        Return the Treeview values for a certain line_dict
        """
        values = (
            TimeView.format_time_diff(line_dict["time"], start_time),
            player_name if Parser.compare_ids(line_dict["source"], active_ids) else line_dict["source"],
            player_name if Parser.compare_ids(line_dict["destination"], active_ids) else line_dict["destination"],
            line_dict["ability"],
            line_dict["amount"]
        )
        return values

    def delete(self, *items):
        """
        Function redirect to reset the index attribute
        """
        ttk.Treeview.delete(self, *items)
        self.index = 0
