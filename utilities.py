# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import os
import sys


def get_temp_directory():
    """
    Returns the absolute path to the directory that is to be used by the GSF Parser for the temporary files.
    :return: str
    """
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


