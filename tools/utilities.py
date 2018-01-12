"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

import os
from os import path
import sys
from PIL import Image
from PIL.ImageTk import PhotoImage as photo
from sys import platform
import tkinter as tk
from tkinter import messagebox


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


def open_icon_pil(image_name):
    """
    Open an image from the assets folder and return a PIL Image
    """
    # Type check for PyCharm completion
    if not isinstance(image_name, str):
        raise ValueError()
    icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
    if not image_name.endswith(".jpg"):
        image_name += ".jpg"
    filename = path.join(icons_path, image_name)
    if not path.exists(filename):
        messagebox.showinfo("Error", "A non-critical error occurred. The GSF Parser is missing an icon "
                                     "with the name {}. Please report this error if you did not modify the "
                                     "assets folder.".format(image_name))
        filename = path.join(icons_path, "imperial.png")
    return Image.open(filename)


def open_icon(image_name):
    """
    Open an image from the assets folder
    """
    return photo(open_icon_pil(image_name))


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
    from Xlib import display
    data = display.Display().screen().root.query_pointer()._data
    return data["root_x"], data["root_y"]


def get_cursor_position():
    """
    Calls the appropriate function to get the cursor position depending
    on the operating system.
    """
    if platform == "win32":
        return get_pointer_position_win32()
    elif platform == "linux":
        return get_pointer_position_linux()
    elif platform == "darwin":
        raise ValueError("This function does not support macOS")
    else:
        raise ValueError("Unknown platform detected")


def get_temp_directory():
    """
    Returns the absolute path to the directory that is to be used by the
    GSF Parser for the temporary files.
    """
    if sys.platform == "win32":
        import tempfile
        folder = os.path.abspath(os.path.join(tempfile.gettempdir(), "..", "GSF Parser"))
    elif sys.platform == "linux":
        folder = "/var/tmp/gsfparser"
    else:
        raise ValueError("Unsupported platform: %s" % sys.platform)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def get_assets_directory():
    """
    Returns the absolute path to the assets directory of the GSF Parser
    :return: str, absolute path
    """
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets"))
    return path


def get_screen_resolution():
    """
    Cross-platform way to get the screen resolution using Tkinter.
    Alternative methods include using GetSystemMetrics with win32api
    for Windows and screen_width()/screen_height() from the gtk.gdk
    module on Linux. For now, it seems best to use a cross-platform
    option
    :return: tuple, (width, height), such as (1920, 1080)
    """
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

