# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from datetime import datetime, timedelta
from queue import Queue
from tkinter import StringVar, Tk
# Own modules
from widgets.overlay import Overlay


class TimerParser(object):
    """
    An object that updates an overlay that shows the time left until a new spawn hits. !Should run in MainThread
    """
    def __init__(self, master, start_time):
        """
        :param master: master Tk instance
        :param start_time: time to start counting (datetime instance)
        """
        self.exit_queue = Queue()
        self.text_var = StringVar()
        self.overlay = Overlay((100, 100), self.text_var, master=master, auto_init=False, wait_time=5000)
        if not isinstance(start_time, datetime):
            raise ValueError("start_time is not a datetime instance but {}".format(repr(start_time)))
        self.start_time = start_time
        self.after_task = None
        # if not isinstance(master, Tk):
        #    raise ValueError("master is not a tk.Tk instance but {}".format(repr(master)))
        self.master = master
        if self.master is not None:
            self.master.after(1000, self.update)
        self.overlay.initialize_window()

    def update(self):
        """
        Function that has to be called each cycle to update the Overlay
        """
        if not self.exit_queue.empty() and self.after_task is not None:
            self.overlay.destroy()
        now = datetime.now()
        seconds = (now - self.start_time).seconds
        result = (20 - seconds % 20 if seconds >= 0 and not seconds % 20 == 0 else 0) if seconds >= 0 else seconds * -1
        self.text_var.set("Next spawn in {:02d} seconds".format(result))
        if self.master is not None:
            self.after_task = self.master.after(1000, self.update)
        self.overlay.update()


if __name__ == '__main__':
    root = Tk()
    timer = TimerParser(root, datetime.now() + timedelta(seconds=5))
    root.mainloop()


