"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from settings.settings import Settings, SettingsDictionary
from settings.defaults import defaults
from settings.eval import config_eval


class TestSettings(TestCase):
    def test_dictionary(self):
        for section, options in defaults.items():
            dictionary = SettingsDictionary(section)
            for option, value in options.items():
                self.assertEqual(dictionary[option], value)
        return

    def test_settings(self):
        settings = Settings()
        for section, options in defaults.items():
            self.assertIsInstance(settings[section], SettingsDictionary)

    def test_settings_write(self):
        settings = Settings()
        settings.write_settings(defaults)

    def test_settings_defaults(self):
        settings = Settings()
        settings.write_defaults()

    def test_eval(self):
        params = [
            ("5.5", 5.5),
            ("v4.0.2", "v4.0.2"),
            ("True", True),
            (True, True),
            ("advanced", "advanced"),
            ("[\"option\"]", ["option"])
        ]
        for param, expec in params:
            self.assertEqual(config_eval(param), expec)
