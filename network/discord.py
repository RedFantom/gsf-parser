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

    DATE_FORMAT = "%Y-%m-%d|%H:%M:%S.%f"

    def __init__(self):
        """Initialize connection"""
        host, port = settings["sharing"]["host"], settings["sharing"]["port"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Connection.__init__(self, sock)
        try:
            self.connect(host, port)
            self.connected = True
        except socket.error:
            mb.showwarning("Warning", "Failed to connect to Discord Bot Server.")
            self.connected = False
        self.files = list()
        self.file = str()
        self.task = None

    def send_command(self, command: str):
        """Send a command to the Discord Server"""
        if settings["sharing"]["enabled"] is False or self.connected is False:
            return False
        tag, auth = settings["sharing"]["discord"], settings["sharing"]["auth"]
        if self.validate_tag(tag) is False:
            return False
        message = "{}_{}_{}".format(tag, auth, command)
        self.send(message)
        self.receive()
        response = self.get_message()
        if response == "ack":
            return True
        elif response == "unauth":
            mb.showerror("Error", "Invalid Discord Bot Server credentials.")
            return False
        elif response == "error":
            print("[DiscordClient] Command {} failed.".format(message))
            return False
        print("[DiscordClient] Invalid server response: {}.".format(response))
        return False

    def send_match_start(self, server: str, start: datetime):
        """Notify the server of a start of a match"""
        string = DiscordClient.datetime_to_str(start)
        self.send_command("match_{}_{}".format(server, string))

    def send_match_end(self, server: str, start: datetime, end: datetime):
        """Notify the server of a match end"""
        start, end = map(DiscordClient.datetime_to_str, (start, end))
        self.send_command("end_{}_{}_{}".format(server, start, end))

    def send_match_score(self, server: str, start: datetime, score: str):
        """Notify the server of the score of a match"""
        start = DiscordClient.datetime_to_str(start)
        self.send_command("score_{}_{}_{}".format(server, start, score))

    def send_match_map(self, server: str, start: datetime, map: tuple):
        """Notify the server of the map detected for a match"""
        start = DiscordClient.datetime_to_str(start)
        self.send_command("map_{}_{}_{}".format(server, start, map))

    def send_result(self, server: str, start: datetime, character: str,
                    assists: int, damage: int, deaths: int):
        """Notify the server of the result a character obtained"""
        start = DiscordClient.datetime_to_str(start)
        self.send_command("result_{}_{}_{}_{}_{}_{}".format(
            server, start, character, assists, damage, deaths))

    def send_character(self, server: str, faction: str, name: str):
        """Notify the server of the existence of a character"""
        self.send_command("character_{}_{}_{}".format(server, faction, name))

    def __enter__(self):
        return self

    def __exit__(self):
        self.socket.close()

    @staticmethod
    def is_enabled():
        return settings["sharing"]["enabled"]

    @staticmethod
    def datetime_to_str(dt: datetime):
        return dt.strftime(DiscordClient.DATE_FORMAT)

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
        # Send the first file
        self.file = self.files[0]
        self.send_file(self.file, window)

    def send_file(self, file_name: str, window: tk.Tk):
        """
        Send a given file to the Discord Bot Server and queue the next
        one by using an after_idle task.
        """
        date = Parser.parse_filename(file_name)
        _, matches, _ = Parser.split_combatlog_file(file_name)

