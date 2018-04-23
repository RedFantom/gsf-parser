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
        self.files = list()
        self.file = str()
        self.task = None
        self.db = list()
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
                    character: str, assists: int, damage: int, deaths: int):
        """Notify the server of the result a character obtained"""
        start = DiscordClient.time_to_str(start)
        date = DiscordClient.date_to_str(date)
        return self.send_command("result_{}_{}_{}_{}_{}_{}_{}_{}".format(
            server, date, start, id_fmt, character, assists, damage, deaths))

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
    def is_enabled():
        return settings["sharing"]["enabled"]

    @staticmethod
    def date_to_str(dt: datetime):
        return dt.strftime(DiscordClient.DATE_FORMAT)

    @staticmethod
    def time_to_str(dt: datetime):
        return dt.strftime(DiscordClient.TIME_FORMAT)

    @staticmethod
    def validate_tag(tag: str):
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

    def send_files(self, window: tk.Tk):
        """Send the files making clever use of the Tkinter mainloop"""
        if settings["sharing"]["enabled"] is False or self.validate_tag(settings["sharing"]["discord"]) is False:
            return
        self.files = list(Parser.gsf_combatlogs())
        print("[DiscordClient] Initiating sending of match data of {} CombatLogs".format(len(self.files)))
        # Send the first file
        self.file = self.files[0]
        window.after(2000, self.send_file, self.file, window)

    def send_file(self, file_name: str, window: tk.Tk):
        """
        Send a given file to the Discord Bot Server and queue the next
        one by using an after_idle task.
        """
        date = Parser.parse_filename(file_name)
        lines = Parser.read_file(file_name)
        player_name = Parser.get_player_name(lines)
        server = window.characters_frame.characters.get_server_for_character(player_name)
        basename = os.path.basename(file_name)
        self.connect()
        print("[DiscordClient] Considering file: {}".format(file_name))
        # Actually send the file data to the server
        if date is not None and server is not None and basename not in self.db and self.connected is True:
            print("[DiscordClient] Sending matches for file: {}".format(basename))
            player_id_list = Parser.get_player_id_list(lines)
            file_cube, matches, _ = Parser.split_combatlog(lines, player_id_list)
            result = True
            for index, (start, end) in enumerate(zip(matches[::2], matches[1::2])):
                id_fmt = Parser.get_id_format(file_cube[index][0])
                start, end = map(lambda time: datetime.combine(date.date(), time.time()), (start, end))
                result = (self.send_match_start(server, date, start, id_fmt) and result)
                result = (self.send_match_end(server, date, start, id_fmt, end) and result)
            print("[DiscordClient] {}: {}".format(basename, result))
            self.db.append(basename) if result is True else None
            self.save_database()
        # Create the task for sending the next file
        index = self.files.index(self.file)
        if index == len(self.files) - 1:
            return
        index += 1
        self.file = self.files[index]
        window.after(2000, self.send_file, self.file, window)

