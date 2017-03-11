# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import multiprocessing as mp
import vision
import threading
import settings
import cPickle as pickle
import tempfile
import datetime


class ScreenParser(mp.Process):
    def __init__(self, data_queue, exit_queue):
        mp.Process.__init__(self)
        self.data_queue = data_queue
        self.exit_queue = exit_queue
        directory = tempfile.gettempdir()
        self.pickle_name = directory.replace("\\temp", "") + "\\GSF Parser\\rltdata.db"
        try:
            self.data_dictionary = pickle.load(self.pickle_name)
        except:
            self.data_dictionary = {}
        self.file = ""
        self.file_dict = {}

        """
        Dictionary structure:
        data_dictionary[filename] = file_dictionary
        file_dictionary[datetime_obj] = match_dictionary
        match_dictionary[datetime_obj] = spawn_dictionary
        spawn_dictionary["power_mgmt"] = power_mgmt_dict
            power_mgmt_dict[datetime_obj] = integer
        spawn_dictionary["cursor_pos"] = cursor_pos_dict
            cursor_pos_dict[datetime_obj] = (x, y)
        spawn_dictionary["tracking"] = tracking_dict
            tracking_dict[datetime_obj] = percentage
        spawn_dictionary["clicks"] = clicks_dict
            clicks_dict[datetime_obj] = (left, right)
        """

    def run(self):
        while True:
            if not self.exit_queue.empty():
                if not self.exit_queue.get():
                    break
            if not self.data_queue.empty():
                data = self.data_queue.get()
                if not isinstance(data, tuple):
                    raise ValueError("Unexpected data received: ", str(data))
                if data[0] == "file" and self.file is not data[1]:
                    self.data_dictionary[self.file] = self.file_dict
                    self.file = data[1]
                    self.file_dict.clear()
                if data[0] == "match" and not data[1] and not self.is_match:
                    self.is_match = False
                if data[0] == "match" and data[1] and not self.is_match:
                    pass
            screen = vision.get_cv2_screen()
            pointer_cds = vision.get_pointer_position_win32()
            power_mgmt = vision.get_power_management(screen)
            health_hull = vision.get_ship_health_hull(screen)
            health_shields_f = vision.get_ship_health_forwardshields(screen)
            health_shields_r = vision.get_ship_health_rearshields(screen)


    def close(self):
        self.__exit__()

    def __exit__(self):
        self.data_dictionary[self.file] = self.file_dict
        pickle.dump(self.data_dictionary, self.pickle_name)


class MouseCounter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gathered_date = {}

    def run(self):
        pass

