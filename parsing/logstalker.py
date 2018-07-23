"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import variables
from parsing.parser import Parser
import os


class LogStalker(object):
    """
    LogStalker class that does *not* run in a Thread, but can instead
    be called upon in cycles to read from the log file and return the
    lines that are newly found in the most recent CombatLog. Not
    interchangeable with earlier implementations.
    """
    def __init__(self, folder=variables.settings["parsing"]["path"], watching_callback=None):
        """
        :param folder: Folder to watch CombatLogs in
        :param watching_callback: Callback to be called when the watched file changes
        """
        self._folder = folder
        self._watching_callback = watching_callback
        self.file = None
        self.path = None
        self._read_so_far = 0

    def update_file(self):
        """
        Update the currently watched file to the newest file available.
        Does not change anything if the file is already the most recent
        available.
        """
        files = os.listdir(self._folder)
        if len(files) == 0:
            raise ValueError("No files found in this folder.")
        recent = sorted(files, key=Parser.parse_filename)[-1]
        if self.file is not None and recent == self.file:
            return
        self.file = recent
        self.path = os.path.join(self._folder, self.file)
        self._read_so_far = 0
        self._watching_callback(self.file)
        self._process_new_file()

    def _process_new_file(self):
        """Backlog only the lines of a match that are match lines"""
        print("[LogStalker] Processing new file.")
        lines = self.read_file(self.path, 0)
        player_list = Parser.get_player_id_list(lines)
        file_cube, _, _ = Parser.split_combatlog(lines, player_list)
        if len(file_cube) == 0:
            print("[LogStalker] No matches in this file")
            self._read_so_far = len(lines)
            return
        last_line = file_cube[-1][-1][-1]
        if last_line["time"] == lines[-1]["time"]:
            print("[LogStalker] Match still active")
            # Last line is still a match line
            match_len = sum(len(spawn) for spawn in file_cube[-1])
            self._read_so_far = len(lines) - match_len
            return
        # Last line is no longer a match
        print("[LogStalker] Last line is not a match event")
        self._read_so_far = len(lines)

    def get_new_lines(self):
        """Read the new lines in the file and return them as a list"""
        self.update_file()
        dictionaries = self.read_file(self.path, self._read_so_far)
        self._read_so_far += len(dictionaries)
        if None in dictionaries:
            raise ValueError()
        return dictionaries

    @staticmethod
    def read_file(path, skip):
        """Read the file in UnicodeDecodeError safe method"""
        with open(path, "rb") as fi:
            lines = fi.readlines()[skip:]
        dictionaries = []
        for line in lines:
            try:
                line = line.decode()
            except UnicodeDecodeError:
                continue
            line = Parser.line_to_dictionary(line)
            if line is None:
                continue
            dictionaries.append(line)
        return dictionaries
