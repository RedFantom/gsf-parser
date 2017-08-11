# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import os
import sys
from datetime import datetime
from PIL import Image
import cv2
import numpy
from sys import platform
import tkinter as tk
import mss

debug = False

map_dictionary = {
    "tdm": {
        "km": "kuatmesas",
        "ls": "lostshipyards"
    },
    "dom": {
        "km": "kuatmesas",
        "ls": "lostshipyards",
        "de": "denonexosphere"
    }
}


def get_pointer_position_cv2(screen):
    """
    Gets the position of the targeting pointer on the screen
    :param screen: A cv2 array of a screenshot image
    :return: A tuple with the coordinates of the top left corner of the pointer
    """
    pointer = cv2.imread(os.getcwd() + "/assets/vision/pointer.png")
    results = cv2.matchTemplate(screen, pointer, cv2.TM_CCOEFF_NORMED)
    return numpy.unravel_index(results.argmax(), results.shape)


def get_pointer_position_win32():
    """
    Gets the position of the targeting pointer with win32gui
    :return: coordinates of pointer
    """
    import win32gui
    return win32gui.GetCursorPos()


def get_pointer_position_linux():
    """
    Gets the position of the targeting pointer with xlib
    :return:coordinates of the pointer
    """
    from xlib import display
    data = display.Display().screen().root.query_pointer()._data
    return data["root_x"], data["root_y"]


def get_cursor_position(screen):
    """
    Calls the appropriate function to get the cursor position depending on the operating system and whether DEBUG mode
    is enabled or not. get_pointer_position_cv2() is not preferred because it's resource intensive.
    :param screen: cv2 array of screenshot
    :return:
    """
    if debug:
        return get_pointer_position_cv2(screen)
    elif platform == "win32":
        return get_pointer_position_win32()
    elif platform == "linux":
        return get_pointer_position_linux()
    elif platform == "darwin":
        raise ValueError("This function does not support macOS")
    else:
        raise ValueError("Unknown platform detected")


def get_pillow_screen():
    """
    Returns the appropriate Image object
    :return: Image object
    """
    sct = mss.mss()
    sct.enum_display_monitors()
    sct.get_pixels(sct.monitors[0])
    return Image.frombytes("RGB", (sct.width, sct.height), sct.image)


def write_debug_log(line):
    """
    If the debug variable is set to True, enables logging to a file in the temporary files folder.
    :param line: line to write to the log
    :return: None
    """
    if not debug:
        return
    if not isinstance(line, str):
        raise ValueError("Logger received an object that is not of str type: %s" % str(line))
    line = (line.replace("\n", "") + "\n")
    line = "[" + datetime.now().strftime("%H:%M:%S") + "] " + line
    with open(os.path.join(get_temp_directory(), "debug.txt"), "a") as fo:
        fo.write(line)


def get_temp_directory():
    """
    Returns the absolute path to the directory that is to be used by the GSF Parser for the temporary files.
    :return: str
    """
    if debug:
        return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    if sys.platform == "win32":
        import tempfile
        path = os.path.abspath(os.path.join(tempfile.gettempdir(), "..", "GSF Parser"))
        try:
            os.makedirs(path)
        except OSError:
            pass
        return path
    elif sys.platform == "linux":
        path = "/var/tmp/gsfparser"
        try:
            os.makedirs(path)
        except OSError:
            raise ValueError("The GSF Parser was unable to gain access to the required temporary folder. "
                             "This folder is located in /var/tmp/gsfparser. Do you have the required permissions "
                             "to access this folder?")
        return path
    else:
        raise ValueError("Unsupported platform: %s" % sys.platform)


def get_swtor_directory():
    """
    Returns the absolute path to the directory that contains the SWTOR temporary files
    :return: str
    """
    if sys.platform == "win32":
        import tempfile
        path = os.path.abspath(os.path.join(tempfile.gettempdir(), "..", "SWTOR"))
        if not os.path.exists(path):
            raise ValueError("SWTOR directory not found. Is SWTOR installed?")
        return path
    else:
        raise NotImplementedError


def get_assets_directory():
    """
    Returns the absolute path to the assets directory of the GSF Parser
    :return: str, absolute path
    """
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets"))
    return path


def get_screen_resolution():
    """
    Cross-platform way to get the screen resolution using Tkinter. Alternative methods include using GetSystemMetrics
    with win32api for Windows and screen_width()/screen_height() from the gtk.gdk module on Linux. For now, it seems
    best to use a cross-platform option
    :return: tuple, (width, height), such as (1920, 1080)
    """
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height
