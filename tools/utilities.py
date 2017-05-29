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
    """
    Calls the appropriate function to get the cursor position depending on the operating system and whether DEBUG mode
    is enabled or not. get_pointer_position_cv2() is not preferred because it's resource intensive.
    :param screen: cv2 array of screenshot
    :return:
    """
    if isinstance(screen, Image):
        from parsing.vision import pillow_to_numpy
        screen = pillow_to_numpy(screen)
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
    """
    Returns the appropriate Image object for the screen depending on the operating system and whether DEBUG mode is
    enabled or not. ImageGrab is used on Windows, but this does not support Linux, so the GTK toolkit is used.
    :return: Image object
    """
    if debug:
        return Image.open(os.path.join(get_assets_directory(), "vision", "testing.png"))
    elif platform == "win32":
        from PIL import ImageGrab
        return ImageGrab.grab()
    elif platform == "linux2":
        """
        Source: https://ubuntuforums.org/showthread.php?t=448160&p=2681009#post2681009
        """
        from gtk import gdk
        window = gdk.get_default_root_window()
        size = window.get_size()
        pixbuff = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, size[0], size[1])
        pixbuff = pixbuff.get_from_drawable(window, window.get_colormap(), 0, 0, 0, 0, size[0], size[1])
        if not pixbuff:
            raise ValueError("Obtaining screenshot failed")
        """
        Source: http://bredsaal.dk/converting-a-gtk-gdk-pixbuf-object-to-a-imageobject
        """
        image = Image.frombuffer("RGB", (pixbuff.get_width(), pixbuff.get_height()),
                                 pixbuff.pixel_array, 'raw', 'RGB', 0, 1)
        image.transpose(Image.FLIP_TOP_BOTTOM)
        return image
    elif platform == "darwin":
        raise ValueError("This function does not support macOS")
    else:
        raise ValueError("Unknown platform detected")


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
    """
    Returns the absolute path to the assets directory of the GSF Parser
    :return: str, absolute path
    """
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets"))
    return path
