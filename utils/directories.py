"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import os
import sys


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
    """Return the absolute path to the assets directory"""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets"))


def get_combatlogs_folder():
    """
    Returns absolute path to the CombatLogs folder in the user's
    Documents folder. Works on both Windows or Linux.
    """
    relative_path = os.path.join("Documents", "Star Wars - The Old Republic", "CombatLogs")
    user_path = os.path.expanduser("~")
    return os.path.realpath(os.path.join(user_path, relative_path))
