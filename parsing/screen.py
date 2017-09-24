# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Own modules
from parsing.guiparsing import GSFInterface
from parsing.timer import TimerParser
from parsing.flytext import FlyTextParser
from tools.utilities import write_debug_log, get_temp_directory, get_cursor_position, get_screen_resolution
from . import vision
from .keys import keys
from toplevels.screenoverlay import HitChanceOverlay
import variables
# General imports
import threading
import pickle as pickle
import os
from datetime import datetime, timedelta
from queue import Queue
import time
import pynput
import mss
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from shutil import copyfile
from PIL import Image

"""
These classes use data in a dictionary structure, dumped to a file in the temporary directory of the GSF Parser. This
dictionary contains all the data acquired by screen parsing and is stored with the following structure:

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
spawn_dictionary["keys"] = keys_dict
    keys_dict[datetime_obj] = keyname
spawn_dictionary["health"] = health_dict
    health_dict[datetime_obj] = (hull, shieldsf, shieldsr), all ints
spawn_dictionary["distance"] = distance_dict
    distance_dict[datetime_obj] = distance, int
spawn_dictionary["target"] = target_dict
    target_dict[datetime_obj] = (type, name)


The realtime screen parsing uses Queue objects to communicate with other parts of the program. This is required because
the screen parsing takes place in a separate process for performance optimization and itself runs several threads to
monitor mouse and keyboard activity. This only gets recorded if the user is in a match, for otherwise it might be
possible to extract keylogs of different periods, and this would impose an extremely dangerous security issue. The Queue
objects used by the ScreenParser object are the following:

data_queue:         This Queue object receives any data from the realtime file parsing that is relevant for the
                    Screen Parser object. This includes data about the file watched, the match detected, the spawn
                    detected and other information. A list of expected data:
                    - ("file", str new_file_name)           new CombatLog watched
                    - ("match", True, datetime)             new match started
                    - ("match", False, datetime)            match ended
                    - ("spawn", datetime)                   new spawn
exit_queue:         This Queue object is checked to see if the ScreenParser should stop running or not. Because this
                    is running in a separate process, one cannot just simply call __exit__, all pending operations
                    must first be completed. A list of expected data:
                    - True                                  keep running
                    - False                                 exit ASAP
query_queue         This Queue object is for communication between the process and the realtime parsing thread in the
                    main process so the main process can receive data and display it in the overlay. A list of
                    expected data:
                    - "power_mgmt"                          return int power_mgmt
                    - "tracking"                            return int tracking degrees
                    - "health"                              return (hull, shieldsf, shieldsr), all ints
return_queue        The Queue in which the data requested from the query_queue is returned.
_internal_queue:    This Queue object is for internal communication between the various Thread objects running in this
                    Process object. A list of expected data:
                    - ("keypress", *args)                   key pressed
                    - ("mousepress", *args)                 mouse button pressed
                    - ("mouserelease", *args)               mouse button released
                    This is not yet a complete list.
"""


class ScreenParser(threading.Thread):
    """
    A Thread that takes automated screenshots and analyzes them in order to get more information from GSF matches
    """
    def __init__(self, data_queue, exit_queue, query_queue, return_queue, character_data, rgb=False, cooldowns=None,
                 powermgmt=True, health=True, name=True, ttk=True, tracking=True, ammo=True, distance=True,
                 cursor=True, timer=True):
        """
        :param data_queue: Queue that will inform about new matches, spawns, etc.
        :param exit_queue: Queue that will contain True if an exit is requested
        :param query_queue: Queue that will contain requests to get data from the ScreenParser
        :param return_queue: Queue that will contain the answers to the requests in the query_queue
        :param character_data: Character data for the character selected
        :param rgb: Parameter for feature that is not yet implemented
        :param cooldowns: Parameter for feature that is not yet implemented
        :param powermgmt: True if powermgmt function is enabled
        :param health: True if health amount function is enabled
        :param name: True if name feature is enabled (TODO)
        :param ttk: True if ttk feature is enabled (TODO)
        :param tracking: True if tracking degrees feature is enabled
        :param ammo: True if ammo amount function is enabled (TODO)
        :param distance: True if distance feature is enabled (TODO)
        :param cursor: True if cursor feature is enabled (TODO)
        """
        threading.Thread.__init__(self)
        # The rgb and cooldowns parameters offer the possibility of enabling LED effects on supported RGB keyboards
        if rgb and not cooldowns:
            write_debug_log("ScreenParser encountered the following error during initialization: "
                            "rgb requested but cooldowns not specified")
            raise ValueError("rgb requested but cooldowns not specified")
        # Interface filename
        interface = character_data["GUI"]
        # Get a GSFInterface instance for the selected character's GUI profile
        if not isinstance(interface, GSFInterface):
            interface = GSFInterface(interface)
        self.interface = interface
        # Parameters for unimplemented features
        self.rgb = rgb
        self.cooldowns = cooldowns
        # Queues (see docstring)
        self.query_queue = query_queue
        self.data_queue = data_queue
        self.exit_queue = exit_queue
        self._internal_queue = Queue()
        self.return_queue = return_queue
        # A Queue that receives line dictionaries from the realtime.Parser
        self.timer_line_queue = Queue()
        self.flytext_line_queue = Queue()
        self.line_queue = MultiQueue(self.timer_line_queue, self.flytext_line_queue)
        # The name of the realtime screen parsing database
        self.pickle_name = os.path.join(get_temp_directory(), "realtime.db")
        # A dictionary containing the values of the features
        self.features = {
            # Determine the power management setting (1-4)
            "powermgmt": powermgmt,
            # Determine the health numbers of the ship
            "health": health,
            # Determine the name of the target by using OCR
            "name": name,
            # Determine the time-to-kill in realtime (to use for queries)
            "ttk": ttk,
            # Determine the amount of tracking degrees
            "tracking": tracking,
            # Determine the amount of ammo of the equipped secondary weapon by using OCR
            "ammo": ammo,
            # Determine the distance to the target by using OCR
            "distance": distance,
            # Determine the cursor position
            "cursor": cursor,
            # Determine the spawn timer
            "timer": timer
        }
        # The data for the character selected in the RealtimeFrame
        self.character = character_data
        # List of features (str) generated from the feature dictionary
        self.features_list = [key for key, value in self.features.items() if value]
        # If debug is enabled, the ScreenParser will log various activities to the program wide debug log file
        write_debug_log("ScreenParser is opening the following database: %s" % self.pickle_name)
        # Set up the Overlay instance if that setting is enabled
        self.screenoverlay = HitChanceOverlay(variables.main_window) if \
            variables.settings_obj["realtime"]["screenparsing_overlay"] else None
        # The overlay moves with the cursor if this setting is enabled
        self.moving_overlay = variables.settings_obj["realtime"]["screenparsing_overlay_geometry"]

        # Open the realtime database file
        try:
            # Try to open the database (with a bytes-like object)
            with open(self.pickle_name, "rb") as fi:
                self.data_dictionary = pickle.load(fi)
        except IOError:
            # IOError means that there is no file with the correct name and a new database is created on the fly
            self.data_dictionary = {}
        except EOFError as e:
            # If an EOFError occurs, then the database was not saved correctly and the database cannot be restored by
            # any automated process. The user is offered the option to save the corrupted database to a different
            # location so it may be restored in some manual manner.
            messagebox.showerror("Error", "The realtime data database did not open correctly. The data in the file may "
                                          "be corrupted. You will now have the chance to dump the data to a separate "
                                          "location together with a debug log. After this, the data will be "
                                          "overwritten and all data in the file, including all data on tracking, "
                                          "health, maps, scores and other data will be lost.")
            if messagebox.askyesno("Debug dump", "Would you like to backup your old file with a debug log for the "
                                                 "developers?"):
                directory = filedialog.askdirectory(parent=variables.main_window, title="Choose directory...",
                                                    mustexist=True)
                copyfile(self.pickle_name, directory)
                with open(os.path.join(directory, "debug.txt"), "w") as f:
                    f.writelines(repr(e))
            # The data is now discarded
            self.data_dictionary = {}
        write_debug_log("ScreenParser is creating all required data variables")
        # String of filename
        self._file = ""
        # Datetime objects of start timings
        self._match = None
        self._spawn = None
        # Dictionaries to store temporary data
        self._file_dict = {}
        self._match_dict = {}
        self._spawn_dict = {}
        # More dictionaries to store temporary data
        self._power_mgmt_dict = {}
        self._cursor_pos_dict = {}
        self._tracking_dict = {}
        self._clicks_dict = {}
        self._keys_dict = {}
        self._health_dict = {}
        self._distance_dict = {}
        self._target_dict = {}
        self._ammo_dict = {}

        # Listeners for keyboard and mouse input
        self._kb_listener = pynput.keyboard.Listener(on_press=self.on_press_kb)
        self._ms_listener = pynput.mouse.Listener(on_click=self.on_click)

        self._current_match = None
        self._current_spawn = None
        self.file = None
        self.match = None
        self.is_match = False
        self.timer_parser = None

        self.flytext_parser = None

    def run(self):
        """
        Runs a loop in a separate Thread in order to collect the data that is required to perform the functionality
        """
        # Start the listeners for keyboard and mouse input
        write_debug_log("ScreenParser starting main functions")
        write_debug_log("Threads active: %s" % str(threading.enumerate()))
        # self._kb_listener.start()
        # self._ms_listener.start()
        # Python-MSS provides a ctypes library with very fast functions to capture the screen contents
        sct = mss.mss()
        resolution = get_screen_resolution()
        
        power_mgmt_cds = self.interface.get_ship_powermgmt_coordinates()
        health_cds = self.interface.get_ship_health_coordinates()
        name_cds = self.interface.get_target_name_coordinates()
        ship_type_cds = self.interface.get_target_shiptype_coordinates()
        player_buff_cds = self.interface.get_ship_buffs_coordinates()
        target_buff_cds = self.interface.get_target_buffs_coordinates()
        score_cds = self.interface.get_score_coordinates()
        spawn_timer_box = (1466, 835, 1536, 875)
        ammo_cds = self.interface.get_ammo_coordinates()
        distance_cds = self.interface.get_distance_coordinates()

        health_hull, health_shields_f, health_shields_r = None, None, None
        ammo, distance = None, None

        line = None
        waiting_for_timer = None
        self.timer_parser = None

        if "flytext" in self.features:
            self.flytext_parser = FlyTextParser(variables.main_window, self.flytext_line_queue)

        # Start the screen parsing loop
        while True:
            if self.timer_parser is not None:
                self.timer_parser.update()
            # If the exit_queue is not empty, get the value. If the value is False, exit the loop and start preparations
            # for terminating the process entirely by saving all the data collected.
            if not self.exit_queue.empty():
                print("ScreenParser exit_queue is not empty")
                if not self.exit_queue.get():
                    print("ScreenParser loop break")
                    break
            write_debug_log("ScreenParser started a cycle")
            # If the Line Queue is not empty, process the lines first
            while not self.timer_line_queue.empty():
                line, _ = self.timer_line_queue.get()
                if (self.is_match is False and waiting_for_timer is None and
                        isinstance(line, dict) and "Safe Login" in line["ability"] and self.timer_parser is None):
                    # If a Safe Login event is detected, a 60 second period is started to try and detect the timer
                    # status.
                    print("Starting to wait for a timer with event {}.".format(line))
                    waiting_for_timer = datetime.now()
                # If not waiting for a trigger event, the event must be discarded
                elif self.is_match is True and waiting_for_timer is None:
                    self.timer_line_queue.get()
                else:
                    pass
            # Check if a spawn timer must be started
            if waiting_for_timer is not None:
                screenshot = sct.grab(sct.monitors[0])
                image = Image.frombytes("RGB", screenshot.size, screenshot.rgb).crop(spawn_timer_box)
                timer = vision.get_timer_status(image)
                if timer is not None:
                    print("The timer was determined to be at {}".format(timer))
                    # If the timer has a value, a spawn timer was found in the correct location
                    # The TimerParser will run on MainThread
                    start_time = datetime.now() + timedelta(seconds=timer)
                    self.timer_parser = TimerParser(variables.main_window, start_time)
                    print("The TimerParser was initialized.")
                    waiting_for_timer = None
                # waiting_for_timer may be set to None again by the if above
                if waiting_for_timer is not None and (datetime.now() - waiting_for_timer).seconds > 60:
                    # The 60 second period has expired, the waiting for timer is stopped
                    # Note: This means that the GSF match environment must be loaded within
                    # 60 seconds after getting this event!
                    print("The wait for a timer was cancelled.")
                    waiting_for_timer = None
            # While data_queue is not empty, process the data in it
            if not self.data_queue.empty():
                data = self.data_queue.get()
                write_debug_log("ScreenParser received the following data from Parser: %s" % str(data))
                # (data[0], data[1], data[2])
                if not isinstance(data, tuple):
                    write_debug_log("ScreenParser encountered the following error: "
                                    "Unexpected data received: " + str(data))
                    raise ValueError("Unexpected data received: ", str(data))
                # ("file", filename)
                if data[0] == "file" and self.file is not data[1]:
                    self.data_dictionary[self.file] = self._file_dict
                    self.file = data[1]
                    self._file_dict.clear()
                # ("match", False, datetime)
                elif data[0] == "match" and not data[1] and self.is_match:
                    # Close down the TimerParser
                    if self.timer_parser is not None:
                        print("The TimerParser was closed")
                        self.timer_parser.exit_queue.put(True)
                        self.timer_parser = None
                    if not len(self._match_dict) == 0 or not len(self._spawn_dict) == 0:
                        self.set_new_match()
                    self._match_dict.clear()
                    self.is_match = False
                    self.match = None
                    self.screenoverlay.running = False
                    time.sleep(0.05)
                # ("match", True, datetime)
                elif data[0] == "match" and data[1] and not self.is_match:
                    self._match = data[2]
                    if not len(self._match_dict) == 0 or not len(self._spawn_dict) == 0:
                        self.set_new_match()
                    self.is_match = True
                # ("spawn", datetime)
                elif data[0] == "spawn":
                    self.set_new_spawn()
                    self._spawn = data[1]
                else:
                    write_debug_log("ScreenParser encountered the following error: "
                                    "Unexpected data received: " + str(data))
                    raise ValueError("Unexpected data received: ", str(data))
            if not self.is_match:
                write_debug_log("No match is active, so ScreenParser ends cycle")
                time.sleep(1)
                continue
            write_debug_log("Start pulling vision functions data")
            image = sct.grab(sct.monitors[0])
            pil_screen = Image.frombytes("RGB", image.size, image.rgb)
            screen = vision.pillow_to_numpy(pil_screen)
            pointer_cds = get_cursor_position(screen)
            current_time = datetime.now()

            if self.flytext_parser is not None:
                self.flytext_parser.update(pil_screen, pointer_cds)

            if "powermgmt" in self.features_list:
                power_mgmt = vision.get_power_management(screen, *power_mgmt_cds)
            self._power_mgmt_dict[current_time] = power_mgmt
            if "health" in self.features_list:
                health_hull = vision.get_ship_health_hull(screen)
                (health_shields_f, health_shields_r) = vision.get_ship_health_shields(pil_screen, health_cds)
            self._health_dict[current_time] = (health_hull, health_shields_f, health_shields_r)
            if "ttk" in self.features_list:
                # Calculate TTK
                pass
            else:
                # Assign None value
                pass
            if "name" in self.features_list:
                name = vision.perform_ocr(pil_screen, name_cds)
                ship_type = vision.perform_ocr(pil_screen, ship_type_cds)
                self._target_dict[current_time] = (ship_type, name)
            if "tracking" in self.features_list:
                distance = vision.get_distance_from_center(pointer_cds, resolution)
                tracking_degrees = vision.get_tracking_degrees(distance)
            self._tracking_dict[current_time] = tracking_degrees
            if "distance" in self.features_list:
                try:
                    distance = int(vision.perform_ocr(pil_screen, distance_cds))
                except ValueError as e:
                    print(e)
                    distance = None
            self._distance_dict[current_time] = distance
            if "ammo" in self.features_list:
                try:
                    ammo = int(vision.perform_ocr(pil_screen, ammo_cds))
                except ValueError as e:
                    print(e)
                    ammo = None
            self._ammo_dict[current_time] = ammo
            self._cursor_pos_dict[current_time] = pointer_cds
            if not self.exit_queue.empty():
                print("ScreenParser exit_queue is not empty")
                if not self.exit_queue.get():
                    print("ScreenParser loop break")
                    break
            if self.screenoverlay:
                self.screenoverlay.set_percentage(str(tracking_degrees) + "°")
            write_debug_log("Start logging and saving vision functions data")
            self._tracking_dict[current_time] = tracking_degrees * 1
            if not self._internal_queue.empty():
                data = self._internal_queue.get()
                write_debug_log("ScreenParser received the following data in the internal_queue: %s" % str(data))
                if "mouse" in data[0]:
                    self._clicks_dict[data[2]] = (data[0], data[1])
                else:
                    self._keys_dict[data[2]] = (data[0], data[1])
            if not self.query_queue.empty():
                command = self.query_queue.get()
                write_debug_log("ScreenParser received the following command: %s" % command)
                if not isinstance(command, str):
                    write_debug_log("ScreenParser encountered the following error: "
                                    "Command received was not of str type")
                    raise ValueError("Command received was not of str type")
                if command == "power_mgmt":
                    self.return_queue.put(power_mgmt)
                elif command == "health":
                    self.return_queue.put((health_hull, health_shields_f, health_shields_r))
                elif command == "tracking":
                    self.return_queue.put(tracking_degrees)
                else:
                    raise ValueError("Command not supported: {0}".format(command))
                write_debug_log("Requested data returned to in the return_queue")
            self._spawn_dict["power_mgmt"] = self._power_mgmt_dict
            self._spawn_dict["cursor_pos"] = self._cursor_pos_dict
            self._spawn_dict["clicks"] = self._clicks_dict
            self._spawn_dict["keys"] = self._keys_dict
            self._spawn_dict["health"] = self._health_dict
            self._spawn_dict["distance"] = self._distance_dict
            self._spawn_dict["target"] = self._target_dict
            self._spawn_dict["ammo"] = self._ammo_dict
            self._spawn_dict["tracking"] = self._tracking_dict
            self._match_dict[self._spawn] = self._spawn_dict
            self._file_dict[self._match] = self._match_dict
            self.data_dictionary[self._file] = self._file_dict
            self.save_data_dictionary()
            write_debug_log("Finished a screen parsing cycle")
        print("ScreenParser stopping activities")
        write_debug_log("ScreenParser stopping activities")
        try:
            self.screenoverlay.running = False
        except AttributeError:
            pass
        time.sleep(0.05)
        print("Calling self.close()")
        self.data_dictionary[self.file] = self._file_dict
        print("Saving data dictionary")
        self.save_data_dictionary()
        print("ScreenParser exit")

    def on_press_kb(self, key):
        if key in keys:
            key = keys[key]
        write_debug_log("A keypress was inserted in the internal_queue: %s" % str(key))
        self._internal_queue.put(("keypress", key, datetime.now()))

    def on_press_ms(self, key):
        if key in keys:
            key = keys[key]
        write_debug_log("A mousepress was inserted in the internal queue: %s" % str(key))
        self._internal_queue.put("mousepress", key, datetime.now())

    def on_release_ms(self, key):
        if key in keys:
            key = keys[key]
        write_debug_log("A mouserelease was inserted in the internal queue: %s" % str(key))
        self._internal_queue.put("mouserelease", key, datetime.now())

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.on_press_ms(button)
        else:
            self.on_release_ms(button)

    def close(self):
        self.__exit__()

    def __exit__(self):
        self.data_dictionary[self.file] = self._file_dict
        print("Saving data dictionary")
        self.save_data_dictionary()
        print("ScreenParser exit")

    def save_data_dictionary(self):
        write_debug_log("ScreenParser saving data dictionary")
        with open(self.pickle_name, "wb") as fo:
            pickle.dump(self.data_dictionary, fo)
        write_debug_log("ScreenParser successfully saved data dictionary")

    def set_new_spawn(self):
        write_debug_log("ScreenParser getting ready for a new spawn")
        self._match_dict[self._spawn] = self._spawn_dict
        self._spawn_dict.clear()
        self.clear_feature_dicts()

    def clear_feature_dicts(self):
        self._power_mgmt_dict.clear()
        self._cursor_pos_dict.clear()
        self._clicks_dict.clear()
        self._keys_dict.clear()
        self._health_dict.clear()
        self._distance_dict.clear()
        self._target_dict.clear()
        self._tracking_dict.clear()
        self._ammo_dict.clear()

    def set_new_match(self):
        write_debug_log("ScreenParser getting ready for a new match")
        self._match_dict[self._spawn] = self._spawn_dict
        self._file_dict[self._match] = self._match_dict
        self.data_dictionary[self._file] = self._file_dict
        self.save_data_dictionary()
        self._match_dict.clear()
        self._spawn_dict.clear()
        self.clear_feature_dicts()


class MultiQueue(object):
    def __init__(self, *args):
        self.queues = [queue for queue in args if isinstance(queue, Queue)]

    def put(self, *args):
        for queue in self.queues:
            queue.put(*args)

    def get(self):
        raise NotImplementedError
