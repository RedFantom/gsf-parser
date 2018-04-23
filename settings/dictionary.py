"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import os
from settings.defaults import defaults


class SettingsDictionary(object):
    """
    Object with a dictionary-like interface that improves backwards
    compatibility and provides some special options that the settings
    of this program require.
    """
    def __init__(self, section):
        """
        :param section: section name this SettingsDictionary stores
                        the settings for
        """
        self._section = section
        self._data = {}
        self.items = self._data.items
        self.update = self._data.update

    def __getitem__(self, item):
        """
        Provides an interface for settings with backwards compatibility
        and also basic error handling: if a setting cannot be found,
        the default value will be stored and then returned to the user
        to prevent errors.
        """
        if item not in self._data:
            self._data[item] = defaults[self._section][item]
        return self._data[item]

    def __contains__(self, item):
        return item in self._data

    def __setitem__(self, key, value):
        """
        Sets a settings like a dictionary would. If the given value is
        of str type and it is not a path, then the string is lowered
        in order to preserve backwards compatibility with older code.
        """
        if isinstance(value, str) and not os.path.exists(value) and "@" not in value:
            value = value.lower()
        self._data[key] = value
