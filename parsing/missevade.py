# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from pynput import mouse
import win32gui
import threading
from queue import Queue
import tkinter as tk
# Own modules
from widgets.overlay import Overlay
from parsing.stalking_alt import LogStalker
import variables


class MissEvadeParser(threading.Thread):
    """
    A Class capable of displaying overlays where the cursor is when shooting. Shows overlays for misses due to evasion
    and misses due to not being on target separately.
    """
    def __init__(self, master, stalker=None):
        """
        :param master: master Tk instance
        :param stalker: optional LogStalker instance
        """
        threading.Thread.__init__(self)
        if stalker is not None:
            if not isinstance(stalker, LogStalker):
                raise ValueError("stalker is not a LogStalker instance")
            self.stalker = stalker
            self._orig_callback = self.stalker.callback
            self.stalker.callback = self.line_callback
        else:
            self.stalker = LogStalker(callback=self.line_callback)
            self._orig_callback = None
        self._mouse_listener = mouse.Listener(on_click=self.click_callback)
        self.internal_queue = Queue()
        self.exit_queue = Queue()

    def run(self):
        """
        Runs the loop, receiving data from all the queues (managed from separate Threads) in order to perform
        the functionality of this class
        """
        pass

    def line_callback(self, lines):
        """
        Callback for Stalker with list of lines as argument
        """
        pass

    def click_callback(self, x, y, button, pressed):
        """
        :param x: x coordinate
        :param y: y coordinate
        :param button: mouse.Button
        :param pressed: Boolean
        """
        if button is not mouse.Button.left:
            return
        self.internal_queue.put((x, y, pressed))

    def close(self):
        self.exit_queue.put(True)

    def __exit__(self):
        self.close()


class FlyText(Overlay):
    """
    Overlay that shows for a certain time and then fades out
    """

    def __init__(self, master, position, fadeout=True, fadetime=1000, text="Miss", move_downward=20):
        self.master = master
        self.count = 0
        if not isinstance(self.master, tk.Tk):
            raise ValueError()
        self.text = tk.StringVar(value=text)
        font_family = variables.settings_obj["realtime"]["overlay_tx_font"]
        font_size = variables.settings_obj["realtime"]["overlay_tx_size"]
        bold = True
        Overlay.__init__(self, position, self.text, master=master, font={"family": font_family,
                                                                         "size": font_size,
                                                                         "bold": bold,
                                                                         "italic": False})
        self.original_position = position
        self._fadeout = fadeout
        self._fadetime = fadetime
        self._move_downward = move_downward
        self.master.after(20, self.update_attributes)

    def update_attributes(self):
        """
        Updates the window attributes to match Overlay behaviour
        """
        self._position = (self.original_position[0],
                          self.original_position[1] +
                          int(round(self._move_downward / self._fadetime * 20 * self.count, 0)))
        opacity = 255 - int(round(255 / self._fadetime * 20 * self.count, 0))
        if opacity <= 0:
            self.destroy()
            return
        self._opacity = opacity
        self.count += 1
        self.master.after(20, self.update_attributes)


if __name__ == '__main__':
    root = tk.Tk()
    var = tk.StringVar(value="Hello World")
    overlay = FlyText(root, (500, 100))
    overlay.initialize_window()
    overlay_two = FlyText(root, (540, 1000), text="Evade")
    overlay_two.initialize_window()
    root.mainloop()
