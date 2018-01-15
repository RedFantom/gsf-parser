"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# General imports
import os
import configparser
# Own modules
from utils import directories
from settings.defaults import defaults
from settings.eval import config_eval
from settings.dictionary import SettingsDictionary


class Settings(object):
    """
    Class that provides an interface to a ConfigParser instance. The
    file parsed by the ConfigParser contains the settings for the GSF
    Parser. The settings interface is a safe one that provides backwards
    compatibility and uses a custom evaluation function to safely
    evaluate the settings to a valid Python value.
    """
    def __init__(self, file_name="settings.ini", directory=directories.get_temp_directory()):
        """
        :param file_name: Settings file filename
        :param directory: Directory to store the setting file in
        """
        self.directory = directory
        self.file_name = os.path.join(directory, file_name)
        self.conf = configparser.ConfigParser()
        self.settings = {key: SettingsDictionary(key) for key in defaults.keys()}
        self.read_settings()
        if self["misc"]["version"] != defaults["misc"]["version"]:
            self.write_settings({"misc": {"version": defaults["misc"]["version"]}})

    def write_defaults(self):
        """
        Write the default settings into the settings file
        """
        conf = configparser.ConfigParser()
        conf.read_dict(defaults)
        with open(self.file_name, "w") as fo:
            conf.write(fo)

    def write_settings(self, dictionary):
        """
        Write a dictionary of settings into the settings file. Settings
        are read directly afterwards to update the contents of the
        instance attribute storing the settings.
        :param dictionary: settings dictionary:
            {section : {setting: value}}
        """
        dictionary = {str(section): {str(key): str(value) for key, value in dictionary[section].items()}
                      for section in dictionary.keys()}
        conf = configparser.ConfigParser()
        for section in dictionary.keys():
            self.settings[section].update(dictionary[section])
        self.settings["misc"]["version"] = defaults["misc"]["version"]
        conf.read_dict(self.settings)
        with open(self.file_name, "w") as fo:
            conf.write(fo)
        self.read_settings()

    def read_settings(self):
        """
        Read the settings from the settings file using a ConfigParser
        and store them in the instance attribute so they can be
        retrieved using the __getitem__ function.
        """
        self.settings.clear()
        if os.path.basename(self.file_name) not in os.listdir(self.directory):
            self.write_defaults()
        with open(self.file_name, "r") as fi:
            self.conf.read_file(fi)
        for section, dictionary in self.conf.items():
            self.settings[section] = SettingsDictionary(section)
            for item, value in dictionary.items():
                self.settings[section][item] = config_eval(value)
        return

    def __getitem__(self, section):
        """
        Returns a SettingsDictionary for a section key. Also provides
        error handling for when the section is not found.
        """
        if section not in self.settings:
            self.write_defaults()
            self.read_settings()
        return self.settings[section]

    def __contains__(self, item):
        return item in self.settings
