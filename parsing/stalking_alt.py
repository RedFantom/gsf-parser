# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Fully new stalking_alt.py file written by RedFantom as a test for solving the problems with
# the earlier stalking_alt.py file
import os
import threading
import time
from datetime import datetime

import variables
import realtime


class LogStalker(threading.Thread):
    """
    A new LogStalker class (compared to the LogStalker class in stalking.py),
    that provides a new way of reading CombatLogs for less IO usage and a more
    stable back-end.
    Trade-off is that the datetime.datetime.strptime every time makes the
    process take longer to pick-up on changes, due to the required processing
    time of the datetime functions.
    LogStalker classes are completely interchangable and compatible with the
    current code, only the import statement in realtimeframe.py must be
    changed.
    """

    def __init__(self, folder=variables.settings_obj.cl_path, callback=None,
                 watching_stringvar=None):
        """
        Open a LogStalker class
        :param folder: the folder with the files to watch
        :param callback: the callback that needs to be called with the
                         new lines as a list argument
        :param watching_stringvar: the tk.StringVar that shows the name
                                   of the file being watched
        """
        threading.Thread.__init__(self)
        self.folder = folder
        self.stringvar = watching_stringvar
        print self.folder
        if not callback:
            raise ValueError("callback is not allowed to be None")
        self.callback = callback
        self.list_of_files = os.listdir(self.folder)
        self.current_file = None
        self.read_so_far = 0
        self.lines = []
        self.datetime_dict = {}

    def run(self):
        """
        The main Thread activity. Watches a SINGLE file for changes, specifically the
        one with the name format combat_%Y-%m-%d_%H_%M_%S_xxxxxx.txt that has the
        newest date in the name. All files that do not use this format are not watched.
        The lines pulled from the file being watched are put into a list and the callback
        from the __init__ function is called with this as an argument. The StringVar is
        updated every time the watched file changes.
        :return: None
        """
        while variables.FLAG:
            folder_list = os.listdir(self.folder)
            self.datetime_dict.clear()
            for name in folder_list:
                if not name.endswith(".txt"):
                    continue
                try:
                    self.datetime_dict[datetime.strptime(name[:-10], "combat_%Y-%m-%d_%H_%M_%S_")] = name
                except ValueError:
                    continue
            temp_datetime_list = []
            for (key, value) in self.datetime_dict.iteritems():
                temp_datetime_list.append(key)
            latest_file_datetime = max(temp_datetime_list)
            latest_file_name = self.datetime_dict[latest_file_datetime]
            if self.current_file == latest_file_name:
                self.callback(self.read_from_file())
            else:
                print "[DEBUG] Watching: " + latest_file_name
                if self.stringvar:
                    self.stringvar.set("Watching: " + latest_file_name)
                self.current_file = latest_file_name
                with open(self.current_file, "r") as file_obj:
                    self.read_so_far = len(file_obj.readlines())
            # sleep 0.1 seconds to reduce IO usage
            time.sleep(variables.settings_obj.timeout)

    def read_from_file(self):
        """
        Read the new lines from the current file and return them
        as a list.
        :return: list of lines
        """
        self.lines = []
        with open(self.current_file, "rb") as file_obj:
            lines_temp = file_obj.readlines()[self.read_so_far:]
        try:
            line_temp = lines_temp[-1]
        except IndexError:
            return []
        if realtime.line_to_dictionary(line_temp):
            self.lines = lines_temp
        else:
            self.lines = lines_temp[:-1]
        self.read_so_far += len(self.lines)
        return self.lines
