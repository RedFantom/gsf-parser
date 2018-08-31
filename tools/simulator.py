"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from datetime import datetime
import time
import os
import threading


class Simulator(threading.Thread):
    """Simulate the creation of a CombatLog with a template file"""

    def __init__(self, input_file, output_directory=None):
        """
        :param input_file: Valid path from working dir to file to
            file to simulate
        :param output_directory: Directory to put the new simulated
            CombatLog into
        """
        threading.Thread.__init__(self)
        self.input_file = input_file
        self.output_directory = output_directory
        self.exit_event = threading.Event()

    def run(self):
        """Create the new file and simulate the generation of events"""
        # Create new log file name with the form: "combat_2012-04-17_20_08_37_242569.txt"
        timestamp = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")
        file_name = "combat_" + timestamp + ".txt"
        last, current = "", ""
        format = "%H:%M:%S.%f"

        with open(self.input_file, "r") as fi, open(os.path.join(self.output_directory, file_name), "a") as fo:
            for line in fi:
                if self.exit_event.is_set():
                    break
                if last == "":
                    last = line.split(None, 1)[0].replace('[', '').replace(']', '')
                else:
                    last = current

                current = line.split(None, 1)[0].replace('[', '').replace(']', '')
                delta = datetime.strptime(current, format) - datetime.strptime(last, format)
                delta_sec = delta.total_seconds()

                fo.write(line)
                print("[Simulator] {}".format(line.strip()))
                fo.flush()
                time.sleep(delta_sec)

    def stop(self):
        """Set the exit event to signal exit from the Simulator"""
        self.exit_event.set()


if __name__ == '__main__':
    import variables
    folder = variables.settings["parsing"]["path"]
    most_recent = list(sorted(os.listdir(folder), reverse=True))[0]
    simulator = Simulator(most_recent, folder)
    try:
        simulator.start()
        while True:
            pass
    except KeyboardInterrupt:
        simulator.stop()

