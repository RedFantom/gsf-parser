"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from queue import Queue
from threading import Thread
# Project Modules
from parsing.shipstats import ShipStats
# Packages
from pynput.keyboard import Key
try:
    from rgbkeyboards import \
        Keyboards, KeyboardController, BaseKeyboard,\
        keygroups, effects


    class RGBController(Thread):
        """
        Controls an RGB Keyboard with fade, flash and other effects
        """
        PRESS = "press"
        RELEASE = "release"

        RED = (255, 0, 0)
        YELLOW = (255, 255, 0)
        GREEN = (0, 255, 0)
        CYAN = (0, 255, 255)
        BLUE = (0, 0, 255)
        PURPLE = (175, 0, 255)
        ORANGE = (255, 150, 0)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)

        BACKGROUND = {key: (100, 100, 100) for key in keygroups.all}
        FOREGROUND = {
            # Movement
            'w': RED,
            'a': RED,
            's': RED,
            'd': RED,
            'shift_l': RED,
            'x': RED,
            # Targeting
            'tab': YELLOW,
            'e': YELLOW,
            'r': YELLOW,
            # Camera
            'f': GREEN,
            'c': GREEN,
            # Specials
            'space': PURPLE,
            'F1': ORANGE,
            'F2': CYAN,
            'F3': PURPLE,
            'F4': WHITE,
            '1': BLUE,
            '2': CYAN,
            '3': PURPLE,
            '4': WHITE,
            "dd": ORANGE,
            "dt": RED,
            "hr": GREEN
        }

        ABILITY_KEYS = {
            '1': "Systems",
            '2': "ShieldProjector",
            '3': "Engines",
            '4': "CoPilot"
        }

        WANTS = [
            Key.space,
            Key.f1,
            Key.f2,
            Key.f3,
            Key.f4
        ]

        def __init__(self):
            """Initialize rgbkeyboards and backend"""
            Thread.__init__(self)
            self.data_queue = Queue()
            self._exit_queue = Queue()

            keyboard = Keyboards().keyboard
            if keyboard is None or not isinstance(keyboard, BaseKeyboard):
                self._enable = False
                return
            self._effect = None
            print("[RGBController] Controller enabled")
            self._controller = KeyboardController(keyboard)
            self._default = self.BACKGROUND
            self._default.update(self.FOREGROUND)
            self._cooldowns = {str(i): 15 for i in range(1, 5)}
            self._lighting = self._default.copy()
            self._enable = True

        @property
        def enabled(self):
            return self._enable

        def run(self):
            """
            Run the control loop on the keyboard controller

            Receives events from the RealTimeParser in order to apply
            specific lighting effects.
            """
            if not self.enabled:
                return
            self._controller.start()
            self._controller.set_full_color(0, (100, 100, 100))
            print("[RGBController] Started KeyboardController")
            # self._controller.set_ind_color(0.1, self._default)
            print("[RGBController] Default background set")
            while True:
                if self._controller.get_queue_item(self._exit_queue) is not None:
                    break
                self.process_data()
            self._controller.stop()

        def process_data(self):
            """Process data in the data queue"""
            item = self._controller.get_queue_item(self.data_queue)
            if item is None:
                return
            while item is not None:
                self.process_item(item)
                item = self._controller.get_queue_item(self.data_queue)

        def process_item(self, item: tuple):
            """
            Process a single item from the data_queue

            Valid items:
            ("press", key name)
            ("release", key name)
            ("press", "missile")
            ("release", "missile")
            """
            event, key = item
            print("[RGBController] Processing item:", item)

            if key in keygroups.pynput_rgb_keys:
                key = keygroups.pynput_rgb_keys[key]

            if "F" in key:
                if event == self.RELEASE:
                    return
                # New Power mode
                mode_keys = {"F{}".format(i): self.BLACK for i in range(1, 5)}
                mode_keys.update({key: self.FOREGROUND[key]})
                print("[RGBController] Scheduling new power mode")
                # self._controller.set_ind_color(0, mode_keys)

            elif key == "missile":
                effect = effects.build_breathe(self.RED, 3, keygroups.all, 0.05)
                print("[RGBController] Scheduling breathe effect")
                # self._controller.sched_effect(0.1, effect)
                # self._controller.set_ind_color(3.1, self._default)

            elif key == "space":
                print("[RGBController] Scheduling space lighting")
                # if event == self.PRESS:
                # self._controller.set_ind_color(0, {"space": self.PURPLE})
                # elif event == self.RELEASE:
                # self._controller.set_ind_color(0, {"space": self.BLACK})
                pass
            else:
                # one = effects.build_transition(
                #     self.BLACK, self.FOREGROUND[key], cooldown, key, 0.10)
                # two = effects.build_transition(
                #    self.WHITE, self.FOREGROUND[key], 2, key)
                print("[RGController] Scheduling cooldown effects")
                # self._controller.sched_effect(0, one)
                # self._controller.sched_effect(cooldown, two)
                trans = effects.build_transition(
                    (100, 100, 100), self.FOREGROUND[key], 2, effects.ALL_KEYS, 0.05)
                if self._effect is not None:
                    self._controller.cancel_effect(self._effect)
                self._effect = self._controller.sched_effect(0, trans)

        def stop(self):
            """Stop the thread"""
            self._exit_queue.put(True)
            self.join(timeout=2)

        def update_stats(self, stats: ShipStats):
            """Update the cooldowns in the cooldowns dictionary"""
            for key_name, key_ablt in self.ABILITY_KEYS.items():
                if key_ablt not in stats:
                    continue
                ablt_stats = stats[key_ablt]
                for stat_dict in (ablt_stats, ablt_stats["Base"]):
                    if "Cooldown" in stat_dict:
                        self._cooldowns[key_name] = int(stat_dict["Cooldown"])
                        break
            return

except ImportError:

    class RGBController(object):
        class DummyQueue(object):
            def put(self):
                pass

        enabled = False
        data_queue = DummyQueue()

