"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from sys import platform
from os import path
# UI Libraries
from tkinter import messagebox
import tkinter as tk
# Packages
from PIL import Image
from PIL.ImageTk import PhotoImage as Photo
from screeninfo import get_monitors
# Project Modules
from utils.directories import get_assets_directory


def open_icon_pil(image_name, size=None, ext=".jpg"):
    """Open an image from the assets folder and return a PIL Image"""
    # Type check for PyCharm completion
    if not isinstance(image_name, str):
        raise ValueError()
    icons_path = path.join(get_assets_directory(), "icons")
    if not image_name.endswith(ext):
        image_name += ext
    filename = path.join(icons_path, image_name)
    if not path.exists(filename):
        messagebox.showinfo(
            "Error", "A non-critical error occurred. The GSF Parser is missing an icon "
                     "with the name {}. Please report this error if you did not modify the "
                     "assets folder.".format(image_name))
        filename = path.join(icons_path, "imperial.png")
    image = Image.open(filename)
    if size is not None:
        image = image.resize(size)
    return image


def open_icon(*args, **kwargs):
    """Open an image from the assets folder"""
    return Photo(open_icon_pil(*args, **kwargs))


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
    raise ValueError("Unknown platform detected")


def get_screen_resolution():
    """
    Uses screeninfo or alternatively Tkinter to determine screen
    resolution as reported by OS. On some Linux window managers the
    result of Tkinter is that of all monitors combined. On Windows,
    Tkinter reports the primary monitor resolution.
    Screeninfo returns a list of monitors of which the resolution of
    the primary monitor is extracted.
    :return: tuple, (width, height), such as (1920, 1080)
    """
    try:  # Not supported on Travis-CI
        monitors = get_monitors()
        return monitors[0].width, monitors[1].height
    except (NotImplementedError, ValueError):
        window = tk.Tk()
        width, height = window.winfo_screenwidth(), window.winfo_screenheight()
        window.destroy()
        return width, height
