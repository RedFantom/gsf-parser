﻿# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

from datetime import datetime
import time
import os
import threading
from queue import Queue


class Simulator(threading.Thread):
    """
    Takes an existent log file and copies it into a newly created file, simulating the time-delta.

    :param: input_file: input file to be copied
    :return: None
    """
    def __init__(self, input_file, output_directory=None):
        threading.Thread.__init__(self)
        self.input_file = input_file
        self.output_directory = output_directory
        self.exit_queue = Queue()

    def run(self):
        # Create new log file name with the form: "combat_2012-04-17_20_08_37_242569.txt"
        timestamp = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")
        file_name = "combat_" + timestamp + ".txt"
        last, current = "", ""
        FMT = "%H:%M:%S.%f"

        with open(self.input_file, "r") as fi, open(os.path.join(self.output_directory, file_name), "a") as fo:
            for line in fi:

                if not self.exit_queue.empty():
                    break

                if last is "":
                    last = line.split(None, 1)[0].replace('[', '').replace(']', '')
                else:
                    last = current

                current = line.split(None, 1)[0].replace('[', '').replace(']', '')

                delta = datetime.strptime(current, FMT) - datetime.strptime(last, FMT)
                delta_sec = delta.total_seconds()

                fo.write(line)
                fo.flush()
                time.sleep(delta_sec)

