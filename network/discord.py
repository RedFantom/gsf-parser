"""
Author: RedFantom
License: GNU GPLv3
Copyright (C) 2018 RedFantom

Docstrings wrapped to 72 characters, line-comments to 80 characters,
code to 120 characters.
"""
# Standard Library
import os
import socket
from datetime import datetime
import _pickle as pickle
# UI Libraries
from tkinter import messagebox as mb
import tkinter as tk
# Project Modules
from network.connection import Connection
from parsing import Parser
from utils.directories import get_temp_directory
from variables import settings


class DiscordClient(Connection):
    """
    Connects to the GSF Parser Bot Server to share information on
    characters and other information about the user of this instance
    of the GSF Parser and his environment.
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"

    def __init__(self):
        """Initialize connection"""
        self.connected = False
        self.notified = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Connection.__init__(self, sock)
        self.task = None
        self.db = dict()
        self.open_database()

    def open_database(self):
        """Open the file database"""
        path = os.path.join(get_temp_directory(), "files.db")
        if not os.path.exists(path):
            self.save_database()
        with open(path, "rb") as fi:
            self.db = pickle.load(fi)

    def save_database(self):
        """Save the file database"""
        path = os.path.join(get_temp_directory(), "files.db")
        with open(path, "wb") as fo:
            pickle.dump(self.db, fo)

    def connect(self, host=None, port=None):
        """Connect the DiscordClient to the server"""
        host, port = settings["sharing"]["host"], settings["sharing"]["port"]
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
        except socket.error:
            self.connected = False
            if self.notified is False:
                mb.showwarning("Warning", "Failed to connect to the Discord Bot Server.")
                self.notified = True
        return self.connected

    def send_command(self, command: str):
        """Send a command to the Discord Server"""
        if settings["sharing"]["enabled"] is False:
            return False
        if self.connect() is False:
            return
        tag, auth = settings["sharing"]["discord"], settings["sharing"]["auth"]
        if self.validate_tag(tag) is False:
            return False
        message = "{}_{}_{}".format(tag, auth, command)
        print("[DiscordClient] {}".format(message))
        self.send(message)
        self.receive()
        response = None
        try:
            response = self.get_message(timeout=0.1)
        except socket.timeout:
            result = False
        finally:
            self.socket.close()
        if response == "ack":
            result = True
        elif response == "unauth":
            if self.notified is False:
                mb.showerror("Error", "Invalid Discord Bot Server credentials.")
                self.notified = True
            result = False
        elif response == "error":
            print("[DiscordClient] Command {} failed.".format(message))
            result = False
        else:
            print("[DiscordClient] Invalid server response: {}.".format(response))
            result = False
        return result

    def send_match_start(self, server: str, date: datetime, start: datetime, id_fmt: str):
        """Notify the server of a start of a match"""
        date = date.strftime(self.DATE_FORMAT)
        start = start.strftime(self.TIME_FORMAT)
        command = "match_{}_{}_{}_{}".format(server, date, start, id_fmt)
        return self.send_command(command)

    def send_match_end(self, server: str, date: datetime, start: datetime, id_fmt: str, end: datetime):
        """Notify the server of a match end"""
        date = DiscordClient.date_to_str(date)
        start, end = map(DiscordClient.time_to_str, (start, end))
        command = "end_{}_{}_{}_{}_{}".format(server, date, start, id_fmt, end)
        return self.send_command(command)

    def send_match_score(self, server: str, date: datetime, start: datetime, id_fmt: str, score: str):
        """Notify the server of the score of a match"""
        date = DiscordClient.date_to_str(date)
        start = DiscordClient.time_to_str(start)
        return self.send_command("end_{}_{}_{}_{}_{}".format(server, date, start, id_fmt, score))

    def send_match_map(self, server: str, date: datetime, start: datetime, id_fmt: str, map: tuple):
        """Notify the server of the map detected for a match"""
        date = DiscordClient.date_to_str(date)
        start = DiscordClient.time_to_str(start)
        return self.send_command("end_{}_{}_{}_{}_{}".format(server, date, start, id_fmt, map))

    def send_result(self, server: str, date: datetime, start: datetime, id_fmt: str,
                    character: str, assists: int, dmgd: int, dmgt: int, deaths: int):
        """Notify the server of the result a character obtained"""
        start = DiscordClient.time_to_str(start)
        date = DiscordClient.date_to_str(date)
        return self.send_command("result_{}_{}_{}_{}_{}_{}_{}_{}_{}".format(
            server, date, start, id_fmt, character, assists, dmgd, dmgt, deaths))

    def send_character(self, server: str, faction: str, name: str):
        """Notify the server of the existence of a character"""
        return self.send_command("character_{}_{}_{}_{}".format(
            server, faction, name, settings["sharing"]["discord"]))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        print("[DiscordClient] __exit__ args:", args)
        self.socket.close()

    @staticmethod
    def date_to_str(dt: datetime):
        return dt.strftime(DiscordClient.DATE_FORMAT)

    @staticmethod
    def time_to_str(dt: datetime):
        return dt.strftime(DiscordClient.TIME_FORMAT)

    @staticmethod
    def validate_tag(tag: str):
        """Return whether a given Discord tag is valid Discord tag"""
        if len(tag) == 0:
            return False
        if tag[0] != "@":
            return False
        elements = tag[1:].split("#")
        if len(elements) != 2:
            return False
        name, discriminator = elements
        if not len(name) > 4:
            return False
        if len(discriminator) != 4:
            return False
        return True

    def send_files(self, window: tk.Tk,):
        """Send the files making clever use of the Tkinter mainloop"""
        if settings["sharing"]["enabled"] is False or self.validate_tag(settings["sharing"]["discord"]) is False:
            return
        files = list(Parser.gsf_combatlogs())
        if len(self.db) == 0:
            mb.showinfo("Notice", "This is the first time data is being synchronized with the Discord Bot Server. "
                                  "This may take a while.")
        elif len(files) - len(self.db) > 10:
            mb.showinfo("Notice", "There are quite many files to synchronize. Please stand by.")
        print("[DiscordClient] Initiating sending of match data of {} CombatLogs".format(len(files)))
        for file_name in files:
            self.send_file(file_name, window)
        print("[DiscordClient] Done sending files.")

    def send_file(self, file_name, window):
        date = Parser.parse_filename(file_name)
        lines = Parser.read_file(file_name)
        player_name = Parser.get_player_name(lines)
        server = window.characters_frame.characters.get_server_for_character(player_name)
        basename = os.path.basename(file_name)
        # Actually send the file data to the server
        if date is None or server is None:
            return
        print("[DiscordClient] Synchronizing file: {}".format(basename))
        if basename not in self.db:
            self.db[basename] = {"match": False, "char": False}
        match_s, char_s = True, False
        player_id_list = Parser.get_player_id_list(lines)
        file_cube, matches, _ = Parser.split_combatlog(lines, player_id_list)
        character_enabled = window.characters_frame.characters[(server, player_name)]["Discord"]
        for index, (start, end) in enumerate(zip(matches[::2], matches[1::2])):
            match = file_cube[index]
            id_fmt = Parser.get_id_format(match[0])
            start, end = map(lambda time: datetime.combine(date.date(), time.time()), (start, end))
            results = Parser.parse_match(match, player_id_list)
            abls, dmg_d, dmg_t, _, _, _, _, _, enemies, _, _, _, _ = results
            if Parser.is_tutorial(match):
                continue
            if self.db[basename]["match"] is False:
                match_s = self.send_match_start(server, date, start, id_fmt) and match_s
                match_s = self.send_match_end(server, date, start, id_fmt, end) and match_s
            if character_enabled is True and self.db[basename]["char"] is False:
                # Parse the file with results and send the results
                deaths = len(match) - 1
                char_s = self.send_result(server, date, start, id_fmt, player_name, len(enemies), dmg_d, dmg_t, deaths)
                print("[DiscordClient] {} to send character result for ({}, {})".format(
                    "Succeeded" if char_s is True else "Failed", server, player_name))
        self.db[basename] = {"match": match_s, "char": char_s}
        self.save_database()

