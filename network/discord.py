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
from dateutil import tz
import _pickle as pickle
# UI Libraries
from tkinter import messagebox as mb
import tkinter as tk
# Project Modules
from data.ships import ship_tiers
from network.connection import Connection
from parsing import Parser, FileHandler
from toplevels.splashscreens import DiscordSplash
from utils.directories import get_temp_directory
from variables import settings


class DiscordClient(Connection):
    """
    Connects to the GSF Parser Bot Server to share information on
    characters and other information about the user of this instance
    of the GSF Parser and his environment.

    The GSF Parser Discord Bot is a bot mean to operate in the GSF
    Discord Server to allow social interaction with match statistics.
    It provides functionality such as tracking the amount of matches
    on dates, as well as more personalized data such as match results.

    The source code for the GSF Parser Discord Bot is available here:
    <https://www.github.com/RedFantom/gsf-discord-bot>

    The connection works in a different way from the other networking
    options.
    1. DiscordClient formulates a command to send.
    2. The send_command() function appends authentication data to the
       command and sends it to the server.
    3. The server processes the command and sends a response:
       - 'ack' = Acknowledged. This does not mean the command was
         executed without error, the client is not notified of that.
         All this means is that the user authenticated successfully and
         the message was received. The server decides what to do with
         the commands given.
       - 'unauth' = The user failed to authenticate. This may mean that
         the user is not registered in the database or an invalid
         security code has been entered in the settings tab.
       - 'error' = This message is returned when the command is not
         valid. It does not mean that a valid command failed to execute.
       - None = This means the server has failed to give a response
         within the timeout of the Connection instance. This may mean
         that the server has crashed.
    4. The DiscordClient closes the Connection. For a new command, a
       new connection will be opened.

    The many-connection design is not the most efficient, but it does
    work well with the asynchronous design of the GSF Parser Discord
    Bot Server.
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
            self.db = {"version": settings["sharing"]["version"]}
            self.save_database()
        with open(path, "rb") as fi:
            self.db = pickle.load(fi)
        if self.db["version"] != settings["sharing"]["version"]:
            os.remove(path)
            self.open_database()

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
        message = "{}_{}_{}_{}".format(tag, auth, settings["misc"]["version"], command)
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
        elif response == "version":
            if self.notified is False:
                mb.showerror("Error", "Your GSF Parser version is too old for "
                                      "communication with the Discord Bot Server.")
                self.notified = True
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

    def send_match_score(self, server: str, date: datetime, start: datetime, id_fmt: str, faction: str, score: float):
        """Notify the server of the score of a match"""
        date = DiscordClient.date_to_str(date)
        start = DiscordClient.time_to_str(start)
        if faction == "Republic":
            score = 1 / score
        return self.send_command("score_{}_{}_{}_{}_{}".format(server, date, start, id_fmt, score))

    def send_match_map(self, server: str, date: datetime, start: datetime, id_fmt: str, map: tuple):
        """Notify the server of the map detected for a match"""
        date = DiscordClient.date_to_str(date)
        start = DiscordClient.time_to_str(start)
        map = "{},{}".format(*map)
        return self.send_command("map_{}_{}_{}_{}_{}".format(server, date, start, id_fmt, map))

    def send_result(self, server: str, date: datetime, start: datetime, id_fmt: str,
                    character: str, assists: int, dmgd: int, dmgt: int, deaths: int, ship: str):
        """Notify the server of the result a character obtained"""
        start = DiscordClient.time_to_str(start)
        date = DiscordClient.date_to_str(date)
        return self.send_command("result_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}".format(
            server, date, start, id_fmt, character, assists, dmgd, dmgt, deaths, ship))

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
        return DiscordClient.datetime_to_utc(dt).strftime(DiscordClient.DATE_FORMAT)

    @staticmethod
    def time_to_str(dt: datetime):
        return DiscordClient.datetime_to_utc(dt).strftime(DiscordClient.TIME_FORMAT)

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

    def send_recent_files(self, window: tk.Tk):
        """Send only the files of today"""
        files = list(Parser.gsf_combatlogs())
        result = list()
        for file in files:
            file_date = Parser.parse_filename(file).date()
            if file_date == datetime.now().date():
                result.append(file)
        self.send_files(window, result)

    @staticmethod
    def datetime_to_utc(dt: datetime):
        if dt.strftime(DiscordClient.DATE_FORMAT) == "1900-01-01":
            dt = datetime.combine(datetime.now().date(), dt.time())
        to_zone = tz.tzutc()
        from_zone = tz.tzlocal()
        local = dt.replace(tzinfo=from_zone)
        return local.astimezone(to_zone)

    def send_files(self, window: tk.Tk, files: list = None):
        """
        Send the match data found in CombatLogs in the CombatLogs folder
        to the Discord Bot Server. For the actual sending, the send_file
        function is used to send each individual file. If Discord
        Sharing is not enabled, the function returns immediately.

        This function is meant to be executed during start-up of the
        GSF Parser, while still at the SplashScreen. The procedure of
        this function takes a rather long time and given data access of
        the MainWindow.characters_frame running it in a separate Thread
        would be a bad idea, and thus this function would interrupt the
        mainloop for at least three seconds, if no files have to be
        synchronized. If files have to be synchronized, this function
        will take long to complete.
        """
        splash = DiscordSplash(window.splash if window.splash is not None else window)
        splash.update_state()
        if settings["sharing"]["enabled"] is False or self.validate_tag(settings["sharing"]["discord"]) is False:
            return
        files = list(Parser.gsf_combatlogs()) if files is None else files
        if len(self.db) == 0:
            mb.showinfo("Notice", "This is the first time data is being synchronized with the Discord Bot Server. "
                                  "This may take a while.")
        elif len(files) - len(self.db) > 10:
            mb.showinfo("Notice", "There are quite many files to synchronize. Please stand by.")
        print("[DiscordClient] Initiating sending of match data of {} CombatLogs".format(len(files)))
        for file_name in files:
            self.send_file(file_name, window)
            splash.update_state()
        splash.destroy()
        print("[DiscordClient] Done sending files.")

    def send_file(self, file_name, window):
        """
        Send the data in a single file to the Discord Bot Server. This
        is done in a few steps.
        # TODO: Optimize amount of times the file is looped over
        # TODO: Split this into multiple shorter functions
        1. Retrieve basic information for this CombatLog that is
           required for sending it, including the date it was created
           and the player name.
        2. Check the requirement that the server for this character is
           known. This is only the case if the character name is unique
           for this system across all servers. If the server cannot
           reliably be determined, the CombatLog data cannot be sent.
        3. Check the files.db database in the temporary data directory
           if this file is in it. If it is not, this is  the first time
           this file is processed. If it is, this file has already been
           processed at least once.
        4. Parse the file, determining individual matches and the times
           they started at.
        5. Retrieve data from the character database (managed by the
           MainWindow.characters_frame in the :characters: attribute.
        6. If Discord sharing is enabled for the character, make sure
           the Discord Bot Server knows about it by sending the command
           for registering a character to the server.
           Note that this may cause duplicate registration requests
           among multiple files, but the Discord Bot Server will ignore
           them if the character is already registered.
        7. Loop over the matches to send.
           7.1. Retrieve match-specific required information such as
                the player ID format and the results.
           7.2. Check if the match is a tutorial match. If it is, the
                character was the only participant and sending it would
                only clutter the database.
           7.3. Check if the non-personal match data has already been
                sent for this file and if not send it to the server.
                # TODO: Extend this part for sending the map type
           7.4. Check if personal data sharing is enabled for this
                character and it has not already been sent. Then send
                the personal match data to the server.
        8. Update the files.db database with whether the sharing of
           data was successful. Only if *all* matches were successfully
           synchronized will the state be set to True. If the state is
           False, a new attempt will be made at some later point.
        9. Save the database to file to prevent loss of data if the user
           exits the process unexpectedly.
        :param file_name: Absolute path to the CombatLog to sync
        :param window: MainWindow instance of this GSF Parser
        """
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
        character = window.characters_frame.characters[(server, player_name)]
        character_enabled = character["Discord"]
        if character_enabled is True:
            server, name, faction = character["Server"], character["Name"], character["Faction"]
            self.send_character(server, faction, name)
        print("[DiscordClient] Character sharing {} for {} on {}".format(
            "enabled" if character_enabled else "disabled", player_name, server))
        for index, (start, end) in enumerate(zip(matches[::2], matches[1::2])):
            match = file_cube[index]
            id_fmt = Parser.get_id_format(match[0])
            start, end = map(lambda time: datetime.combine(date.date(), time.time()), (start, end))
            results = Parser.parse_match(match, player_id_list)
            abls, dmg_d, dmg_t, _, _, _, _, _, enemies, _, _, ships, _ = results
            if Parser.is_tutorial(match):
                continue
            if self.db[basename]["match"] is False:
                match_s = self.send_match_start(server, date, start, id_fmt) and match_s
                match_s = self.send_match_end(server, date, start, id_fmt, end) and match_s
            else:
                print("[DiscordClient] Ignored {}".format(basename))
            data = FileHandler.get_data_dictionary()
            spawn_dict = FileHandler.get_spawn_dictionary(data, basename, start, match[0][0]["time"])
            if isinstance(spawn_dict, dict):
                if "map" in spawn_dict and isinstance(spawn_dict["map"], tuple) and None not in spawn_dict["map"]:
                    self.send_match_map(server, date, start, id_fmt, spawn_dict["map"])
                if "score" in spawn_dict and isinstance(spawn_dict["score"], float):
                    self.send_match_score(server, date, start, id_fmt, character["Faction"], spawn_dict["score"])
            if character_enabled is True:
                if self.db[basename]["char"] is False:
                    # Parse the file with results and send the results
                    ship = ship_tiers[max(ships, key=ships.__getitem__)] if len(ships) != 0 else "Unknown"
                    deaths = len(match) - 1
                    char_s = self.send_result(
                        server, date, start, id_fmt, player_name, len(enemies), dmg_d, dmg_t, deaths, ship)
                    print("[DiscordClient] {} to send character result for ({}, {})".format(
                        "Succeeded" if char_s is True else "Failed", server, player_name))
                else:
                    print("[DiscordClient] Not sending character result because already sent.")
            else:
                print("[DiscordClient] Not sending character result because not enabled.")
        self.db[basename] = {"match": match_s, "char": char_s}
        self.save_database()
