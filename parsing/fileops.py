"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
import os
from datetime import datetime
from variables import settings
from parsing import parse


def get_valid_combatlogs():
    """
    Return a list of valid CombatLog filenames
    """
    # Generate a list of filenames
    path = settings["parsing"]["path"]
    files = os.listdir(path)
    valid_combatlogs = []
    # Loop over the files to check whether they are valid GSF CombatLogs
    for filename in files:
        # First check filetype
        if not filename.endswith(".txt"):
            continue
        # Check file name
        try:
            datetime.strptime(filename[:-10], "combat_%Y-%m-%d_%H_%M_%S_")
        except ValueError:
            continue
        # File has passed all checks
        valid_combatlogs.append(filename)
    return valid_combatlogs


def get_valid_gsf_combatlogs():
    """
    Return a list of valid GSF CombatLog filenames
    """
    valid_combatlogs = get_valid_combatlogs()
    valid_gsf_combatlogs = []
    for item in valid_combatlogs:
        if not parse.check_gsf(item):
            continue
        valid_gsf_combatlogs.append(item)
    return valid_gsf_combatlogs


def get_file_string(file_name):
    """
    Return a nicely formatted string for a given filename
    """
    try:
        file_time = datetime.strptime(file_name[:-10], "combat_%Y-%m-%d_%H_%M_%S_")
    except ValueError:
        return None
    file_string = file_time.strftime("%Y-%m-%d   %H:%M")
    return file_string


def get_id_numbers_from_file():
    pass
