"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import os
import sys
from configparser import ConfigParser
from tkinter import messagebox, filedialog


def get_swtor_directory_win32():
    """
    Return an absolute path to the SWTOR temporary directory or raise an
    error if it cannot be found.
    """
    import tempfile
    path = os.path.abspath(os.path.join(tempfile.gettempdir(), "..", "SWTOR"))
    if not os.path.exists(path):
        messagebox.showerror("Error",
                             "Could not determine the SWTOR temporary files directory. Is SWTOR installed?")
        raise ValueError("SWTOR directory not found. Is SWTOR installed?")
    return path


def get_swtor_directory_linux():
    """
    Return an absolute path to the SWTOR temporary directory in the
    correct Wine Bottle for a Windows. Requires a lot of user
    interaction, which is provided through messageboxes and dialogs.
    """
    import variables
    if "temp_dir" not in variables.settings["misc"] or variables.settings["misc"]["temp_dir"] is None or \
            not os.path.exists(variables.settings["misc"]["temp_dir"]):
        messagebox.showinfo(
            "Info",
            "It appears that you are running SWTOR on Linux. The GSF Parser will now attempt to automatically "
            "determine the location of the SWTOR temporary files directory."
        )
        bottle = os.path.realpath("~/.wine")
        if not os.path.exists(bottle):
            messagebox.showinfo(
                "Info",
                "It appears that you are not using the default Wine Bottle location. Please point the GSF Parser "
                "to the location of your Bottle for SWTOR."
            )
            bottle = filedialog.askdirectory(title="SWTOR Bottle")
            if bottle is None or not os.path.exists(bottle):
                messagebox.showerror("Error", "This is not a valid Bottle location.")
                raise ValueError("Invalid SWTOR Bottle location")
        swtor_path = os.path.join(bottle, "drive_c", "Program Files (x86)", "Electronic Arts", "BioWare",
                                  "Star Wars - The Old Republic")
        if not os.path.exists(swtor_path):
            messagebox.showerror("Error", "Could not find SWTOR in the default installation directory.")
            raise ValueError("SWTOR install path not found: {}".format(swtor_path))
        import getpass
        username = getpass.getuser()
        user_dir = os.path.join(bottle, "drive_c", "users", username)
        if not os.path.exists(user_dir):
            messagebox.showerror("Error", "Could not find a Wine user directory for the current user in this folder.")
            raise ValueError("No Wine user directory for current user found: {}".format(user_dir))
        temp_dir = os.path.join(user_dir, "Local Settings", "Application Data", "SWTOR")
        if not os.path.exists(temp_dir):
            messagebox.showerror("Error", "Determined SWTOR temporary directory as {}, but the folder does not exist. "
                                          "Is SWTOR correctly installed and run at least once?".format(temp_dir))
            raise ValueError("Temporary SWTOR directory does not exist")
        if temp_dir is None:
            raise ValueError()
        variables.settings["misc"]["temp_dir"] = temp_dir
        variables.settings.write_settings({"misc": {"temp_dir": temp_dir}})
    return variables.settings["misc"]["temp_dir"]


def get_swtor_directory():
    """
    Returns the absolute path to the directory that contains the SWTOR
    temporary files
    """
    if sys.platform == "win32":
        return get_swtor_directory_win32()
    else:
        return get_swtor_directory_linux()


def get_swtor_screen_mode():
    """
    Return the SWTOR Screen Mode as a String, or None if it cannot
    reliably be determined.
    """
    config_path = os.path.join(get_swtor_directory(), "swtor", "settings", "client_settings.ini")
    if not os.path.exists(config_path):
        return FileNotFoundError
    config_parser = ConfigParser()
    with open(config_path, "r") as fi:
        config_parser.read_file(fi)
    if "Renderer" not in config_parser.sections():
        return ValueError
    renderer_settings = config_parser["Renderer"]
    if "FullScreen" not in renderer_settings:
        return ValueError
    full_screen = renderer_settings["FullScreen"]
    if full_screen is False or full_screen == "false":
        return "Windowed"
    if "D3DFullScreen" not in renderer_settings:
        return "FullScreen (Windowed)"
    d3d_full_screen = renderer_settings["D3DFullScreen"]
    if d3d_full_screen is True or d3d_full_screen == "true":
        return "FullScreen"
    return "FullScreen (Windowed)"
