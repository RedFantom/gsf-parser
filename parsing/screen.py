# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import multiprocessing as mp
import vision
import threading
import settings


class ScreenParser(mp.Process):
    def __init__(self, data_queue, exit_queue):
        mp.Process.__init__(self)
        self.data_queue = data_queue
        self.exit_queue = exit_queue

    def run(self):
        while True:
            if not self.exit_queue.empty():
                if not self.exit_queue.get():
                    break
            else:
                screen = vision.get_cv2_screen()
                pointer = vision.get_pointer_position_win32()


    def close(self):
        pass


class MouseCounter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gathered_date = {}

    def run(self):
        pass

