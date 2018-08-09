"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from functools import partial
from itertools import tee
import os
# UI Libraries
import tkinter as tk
from tkinter import ttk
# Packages
from PIL import Image
from PIL.ImageTk import PhotoImage
# Project Modules
from parsing.parser import Parser
from data.icons import ICONS
from data.effects import all_effects
from utils.directories import get_assets_directory
import variables


def pairwise(iterable):
    """
    For i_0, i_1, i_2, ... i_n in iterable return
    (i_0, i_1), (i_1, i_2), (i_2, i_3) ...
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


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
        self._icons = {
            name[:-4]: PhotoImage(
                Image.open(
                    os.path.join(get_assets_directory(), "icons", name)).
                resize((24, 24), Image.ANTIALIAS))
            for name in os.listdir(os.path.join(get_assets_directory(), "icons"))
        }
        for icon, file_name in ICONS.items():
            self.icons[icon] = self._icons[file_name]
        self.style = ttk.Style(self)
        self.style.configure("TimeView.Treeview", rowheight=32)
        self.config(style="TimeView.Treeview")
        self.index = 0
        self._contents = list()

    def setup_columns(self):
        """Setup the Treeview with the correct widths and tags"""
        self.column("#0", width=int(40 * self._width), anchor=tk.W)
        self.column("time", width=int(60 * self._width))
        self.column("source", width=int(105 * self._width))
        self.column("target", width=int(105 * self._width))
        self.column("ability", width=int(155 * self._width))
        self.column("amount", width=int(50 * self._width))

    def insert_event(self, line: dict, player_name, active_ids, start_time):
        """Insert a new line into the Treeview"""
        if line is None or line["type"] == Parser.LINE_EFFECT:
            return
        source, target = \
            map(partial(self.process_player, player_name, active_ids), (line["source"], line["target"]))
        source, target = map(self.format_id, (source, target))
        values = (
            TimeView.format_time_diff(line["time"], start_time),
            source, target,
            line["ability"],
            line["amount"] if line["amount"] != 0 else ""
        )
        tag = Parser.get_event_category(line, active_ids)
        if line["ability"] not in self.icons and "icon" not in line:
            print("[TimeView] {} missing icon".format(line["ability"]))
            image = self.icons["default"]
        elif line["ability"] in self.icons:
            image = self.icons[line["ability"]]
        elif "icon" in line:
            d = self._icons if line["icon"] in self._icons else self.icons
            image = d[line["icon"]]
        else:
            print("[TimeView] Missing Icon for: '{}'".format(line["ability"]))
            return
        iid = (repr(line["time"]) + line["source"] + line["target"] +
               line["effect"] + str(self.index))
        ref, start = map(partial(datetime.combine, datetime(1970, 1, 1).date()), (line["time"].time(), start_time.time()))
        index = int((ref - start).total_seconds() * 10e3)
        self._contents.append(index)
        index = list(sorted(self._contents)).index(index)
        self.insert("", index, values=values, tags=(tag,), image=image, iid=iid)
        self.index += 1
        if "effects" not in line or line["effects"] is None:
            return
        if "custom" not in line or line["custom"] is False:
            self.insert_effects_for_event(iid, line, tag)
        else:
            self.insert_effects(iid, line["effects"], tag)

    def insert_effects(self, iid: str, effects: tuple, tag: str):
        """Insert the raw defined effects of an event"""
        for effect in effects:
            image = None
            if len(effect) == 6:
                image, effect = effect[5], effect[:5]
                if image in self.icons:
                    image = self.icons[image]
                else:
                    image = self._icons[image]
            self.insert(iid, tk.END, values=effect, image=image, tags=(tag,))

    def insert_effects_for_event(self, iid: str, line: dict, tag: str):
        """Insert the effects for an event dictionary"""
        for _, effect in sorted(line["effects"].items()):
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

    @staticmethod
    def process_player(name: str, active_ids: list, player: str):
        """Return an appropriate player representation"""
        if Parser.compare_ids(player, active_ids):
            return name
        if player == "":
            return "System"
        return player

    def insert_spawn(self, spawn, player_name, active_ids: list=None):
        """Insert the events of a spawn into the Treeview"""
        self.delete_all()
        if len(spawn) == 0:
            raise ValueError("Invalid spawn passed.")
        spawn = spawn if isinstance(spawn[0], dict) else [Parser.line_to_dictionary(line) for line in spawn]
        start_time = spawn[0]["time"]
        active_ids = Parser.get_player_id_list(spawn) if active_ids is None else active_ids
        for line in spawn:
            if "custom" not in line or line["custom"] is False:
                line_event_dict = Parser.line_to_event_dictionary(line, active_ids, spawn)
            else:
                line_event_dict = line
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
        """Return the Treeview values for a certain line_dict"""
        values = (
            TimeView.format_time_diff(line_dict["time"], start_time),
            player_name if Parser.compare_ids(line_dict["source"], active_ids) else line_dict["source"],
            player_name if Parser.compare_ids(line_dict["target"], active_ids) else line_dict["target"],
            line_dict["ability"],
            line_dict["amount"]
        )
        return values

    def delete_all(self):
        self.delete(*self.get_children())
        self.index = 0
        self._contents.clear()

    @staticmethod
    def validate_effect(effect: str):
        elems = effect.split(":")
        if len(elems) < 2:
            return True
        return elems[1].split("{")[0].strip() in all_effects

    def format_id(self, id: str):
        return id if not id.isdigit() else id[8:]
