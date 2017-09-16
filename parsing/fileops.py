# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import os
from datetime import datetime
import variables
from parsing import parse


def get_valid_combatlogs():
    """
    Return a list of valid CombatLog filenames
    """
    # Generate a list of filenames
    path = variables.settings_obj["parsing"]["cl_path"]
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
    file_string = file_time.strftime(
        "%Y-%m-%d   %H:%M" if variables.settings_obj["gui"]["date_format"] == "ymd" else "%Y-%d-%m   %H:%M"
    )
    return file_string


def get_id_numbers_from_file():
    pass
