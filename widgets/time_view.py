"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
# UI Libraries
import tkinter as tk
from tkinter import ttk
# Packages
from PIL import Image
from PIL.ImageTk import PhotoImage
# Project Modules
from parsing.parser import Parser
from data.icons import icons
from data.effects import all_effects
from utils.directories import get_assets_directory
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
        self._width = kwargs.pop("width", 1.0)
        ttk.Treeview.__init__(self, *args, **kwargs)
        color_scheme = variables.colors.current_scheme
        for category in color_scheme.keys():
            self.tag_configure(category, foreground=color_scheme[category][0], background="gray25", font=("default", 9))
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
        self.column("#0", width=int(40 * self._width), anchor=tk.W)
        self.column("time", width=int(60 * self._width))
        self.column("source", width=int(105 * self._width))
        self.column("target", width=int(105 * self._width))
        self.column("ability", width=int(155 * self._width))
        self.column("amount", width=int(50 * self._width))

    def insert_event(self, line_dict, player_name, active_ids, start_time):
        """
        Insert a new line into the Treeview
        :param line_dict: line dictionary (Parser.line_to_dictionary)
        :return: None
        """
        if line_dict is None or line_dict["type"] == Parser.LINE_EFFECT:
            return
        if line_dict["effect"].split(":")[1].split("{")[0].strip() in all_effects:
            return
        values = (
            TimeView.format_time_diff(line_dict["time"], start_time),
            player_name if Parser.compare_ids(line_dict["source"], active_ids) else (line_dict["source"] if
                line_dict["source"] != "" else "System"),
            player_name if Parser.compare_ids(line_dict["destination"], active_ids) else (line_dict["destination"] if
                line_dict["destination"] != "" else "System"),
            line_dict["ability"],
            line_dict["amount"]
        )
        tag = Parser.get_event_category(line_dict, active_ids)
        if line_dict["ability"] not in self.icons:
            print("[TimeView] Icon for ability '{}' is missing.".format(line_dict["ability"]))
            image = self.icons["default"]
        else:
            image = self.icons[line_dict["ability"]]
        iid = (repr(line_dict["time"]) + line_dict["source"] + line_dict["target"] +
               line_dict["effect"] + str(self.index))
        self.insert("", tk.END, values=values, tags=(tag,), image=image, iid=iid)
        self.index += 1
        if line_dict["effects"] is None:
            return
        for _, effect in sorted(line_dict["effects"].items()):
            if effect["dot"] is not None:
                target_string = "for {} damage".format(effect["damage"])
            else:
                target_string = "{} {}".format(effect["count"], "Allies" if effect["allied"] is True else "Enemies")
            if effect["name"] != "Damage" and effect["duration"] == 0:
                duration_string = ""
            elif effect["name"] != "Damage":
                duration_string = "for {:.1f} seconds".format(effect["duration"])
            elif effect["dot"] is None:
                duration_string = "for {} damage total".format(effect["damage"])
            else:
                duration_string = "over {:.1f} seconds".format(effect["dot"])
            values = ("", effect["name"], target_string, duration_string, "")
            kwargs = {"values": values, "tags": (tag,)}
            if effect["name"] in self.icons:
                kwargs.update({"image": self.icons[effect["name"]]})
            self.insert(iid, tk.END, **kwargs)

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
        return time.strftime("%H:%M:%S")

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
        """Function redirect to reset the index attribute"""
        ttk.Treeview.delete(self, *items)
        self.index = 0

    def delete_all(self):
        self.delete(*self.get_children())
