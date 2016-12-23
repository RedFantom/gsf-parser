# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# Fully new stalking_alt.py file written by RedFantom as a test for solving the problems with the earlier stalking_alt.py file
import os
import vars
import threading
from datetime import datetime

class LogStalker(threading.Thread):
    def __init__(self, folder=vars.set_obj.cl_path, callback=None):
        threading.Thread.__init__(self)
        self.folder = folder
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
                    print "[DEBUG] File name can't be parsed. Skipping..."
            temp_datetime_list = []
            for (key, value) in self.datetime_dict.iteritems():
                temp_datetime_list.append(key)
            latest_file_datetime = max(temp_datetime_list)
            latest_file_name = self.datetime_dict[latest_file_datetime]
            if self.current_file == latest_file_name:
                self.callback(self.read_from_file())
            else:
                print "[DEBUG] Watching: " + latest_file_name
                self.current_file = latest_file_name
                with open(self.current_file, "r") as file_obj:
                    self.read_so_far = len(file_obj.readlines())

    def read_from_file(self):
        del self.lines[:]
        with open(self.current_file, "rb") as file_obj:
            self.lines = file_obj.readlines()[self.read_so_far:]
            self.read_so_far += len(self.lines)
        return self.lines
