# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# Fully new stalking_alt.py file written by RedFantom as a test for solving the problems with the earlier stalking_alt.py file
import os
import vars
import threading
import time
from datetime import datetime

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
    def __init__(self, folder=vars.set_obj.cl_path, callback=None,
                 watching_stringvar=None):
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
        while vars.FLAG:
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
            time.sleep(0.1)

    def read_from_file(self):
        del self.lines[:]
        with open(self.current_file, "rb") as file_obj:
            self.lines = file_obj.readlines()[self.read_so_far:]
            self.read_so_far += len(self.lines)
        return self.lines
