# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import os
import sys
from datetime import datetime
from PIL import Image, ImageGrab
import cv2
import numpy
from sys import platform

debug = False


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
    if debug:
        return get_pointer_position_win32()
    elif platform == "win32":
        return get_pointer_position_cv2(screen)
    elif platform == "linux2":
        return get_pointer_position_linux()
    elif platform == "darwin":
        raise ValueError("This function does not support macOS")
    else:
        raise ValueError("Unknown platform detected")


def get_pillow_screen():
    if debug:
        return Image.open(os.path.join(get_assets_directory(), "vision", "testing.png"))
    else:
        return ImageGrab.grab()


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
    elif sys.platform == "linux2":
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
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets"))
    return path
