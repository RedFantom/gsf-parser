# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from pynput import mouse
from queue import Queue
import tkinter as tk
from PIL import Image
from mss.base import ScreenShot
from os import path
from datetime import datetime
# Own modules
from widgets.overlay import Overlay
# from .abilities import primaries
from parsing.imgcompare import get_similarity
import variables
from tools.utilities import get_cursor_position, get_assets_directory


class FlyTextParser(object):
    """
    A Class capable of displaying overlays where the cursor is when shooting. Shows overlays for misses due to evasion
    and misses due to not being on target separately.
    """
    def __init__(self, master, line_queue):
        """
        :param master: master Tk instance
        :param line_queue: Queue in which line events are put
        """
        self.master = master
        self.line_queue = line_queue
        self._mouse_listener = mouse.Listener(on_click=self.click_callback)
        self.mouse_queue = Queue()
        self.internal_queue = Queue()
        self.overlays = []
        template_path = path.join(get_assets_directory(), "vision", "ontarget.png")
        self.on_target_template = Image.open(template_path).convert("RGB")
        self.ship = None
        self.firing = False
        self.last_shot = None

    def update(self, screenshot=None, cursor_position=None):
        """
        Runs the loop, receiving data from all the queues (managed from separate Threads) in order to perform
        the functionality of this class
        """
        if not self._mouse_listener.is_alive():
            self._mouse_listener.start()
        while not self.mouse_queue.empty():
            x, y, pressed = self.mouse_queue.get()
            print("Mouse button was {}".format(pressed))
            self.firing = pressed
        if screenshot is not None and cursor_position is not None and self.firing is True:
            print("Updating FlyText")
            # (datetime.now() - self.last_shot).seconds < self.ship.components["PrimaryWeapon"]["FiringRate"]
            if not self.on_target(screenshot, cursor_position):
                self.overlays.append(FlyText(self.master, cursor_position))
                print("New FlyText opened for miss")
            else:
                self.internal_queue.put(datetime.now())
        while not self.line_queue.empty():
            # Events are coming in, yay!
            line, active_id = self.line_queue.get()
            if line["source"] != active_id:
                continue

        for overlay in self.overlays:
            self.overlays.remove(overlay) if overlay.alive is False else None

    def on_target(self, screenshot, cursor_position):
        if isinstance(screenshot, ScreenShot):
            screenshot = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        x, y = cursor_position
        box = (x - 21, y - 20, x + 23, y + 23)
        pointer = screenshot.crop(box)
        similarity = get_similarity(pointer, self.on_target_template)
        print("Similirity score: ", similarity)
        return similarity < 6.0

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
        self.mouse_queue.put((x, y, pressed))

    def close(self):
        pass

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
                                                                         "italic": False},
                         wait_time=20)
        self.original_position = position
        self._fadeout = fadeout
        self._fadetime = fadetime
        self._move_downward = move_downward
        self.master.after(20, self.update_attributes)
        self.alive = True

    def update_attributes(self):
        """
        Updates the window attributes to match Overlay behaviour
        """
        self._position = (self.original_position[0],
                          self.original_position[1] +
                          int(round(self._move_downward / self._fadetime * self._wait_time * self.count, 0)))
        opacity = 255 - int(round(255 / self._fadetime * self._wait_time * self.count, 0))
        if opacity <= 0:
            self.destroy()
            self.alive = False
            return
        self._opacity = opacity
        self.count += 1
        self.master.after(20, self.update_attributes)


if __name__ == '__main__':
    root = tk.Tk()
    line_queue = Queue()
    line_queue.put({"ability": "Burst Laser Cannon"})
    parser = FlyTextParser(root, line_queue)
    screenshot = Image.open("../assets/vision/test_flytext.png")
    parser.update(screenshot, (952, 578))
    screenshot = Image.open("../assets/vision/testing.png")
    parser.update(screenshot, (935, 512))
    root.after(10000, parser.update)
    root.mainloop()
