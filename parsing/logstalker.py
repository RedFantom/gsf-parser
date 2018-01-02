# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import variables
from parsing.parser import Parser
import os


class LogStalker(object):
    """
    LogStalker class that does *not* run in a Thread, but can instead be called upon in cycles to read from the log
    file and return the lines that are newly found in the most recent CombatLog. Not interchangeable with earlier
    implementations.
    """
    def __init__(self, folder=variables.settings["parsing"]["path"], watching_callback=None):
        """
        :param folder: Folder to watch CombatLogs in
        :param watching_callback: Callback to be called when the watched file changes
        """
        self._folder = folder
        self._watching_callback = watching_callback
        self.file = None
        self._read_so_far = 0

    def update_file(self):
        """
        Update the currently watched file to the newest file available. Does not change anything if the file is already
        the most recent available.
        """
        files = os.listdir(self._folder)
        if len(files) == 0:
            raise ValueError("No files found in this folder.")
        recent = sorted(files, key=Parser.parse_filename)[-1]
        if self.file is not None and recent == self.file:
            return
        self.file = recent
        print("[LogStalker] Watching new file: {}".format(self.file))
        self._read_so_far = 0
        self._watching_callback(self.file)

    def get_new_lines(self):
        """
        Read the new lines in the file and return them as a list.
        """
        self.update_file()
        with open(os.path.join(self._folder, self.file), "rb") as fi:
            lines = fi.readlines()[self._read_so_far:]
        self._read_so_far += len(lines)
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
        if None in dictionaries:
            raise ValueError()
        return dictionaries
