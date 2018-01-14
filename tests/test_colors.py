"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from collections import OrderedDict
import mock
from data import colors
from settings.colors import ColorScheme


class TestColors(TestCase):
    def test_color_schemes(self):
        self.assertIsInstance(colors.default_colors, OrderedDict)
        self.assertIsInstance(colors.pastel_colors, OrderedDict)

    def test_color_scheme(self):
        color_scheme = ColorScheme()
        for key1, key2 in zip(color_scheme.current_scheme.keys(), colors.default_colors.keys()):
            self.assertEqual(key1, key2)
            self.assertIsInstance(key1, str)
            self.assertIsInstance(key2, str)
        return

    def test_color_scheme_modified(self):
        color_scheme = ColorScheme()
        color_scheme["default"] = ["#fff000", "#000fff"]
        color_scheme.write_custom()

    def test_color_scheme_options(self):
        color_scheme = ColorScheme()
        schemes = ["bright", "pastel", "custom"]
        for scheme in schemes:
            with mock.patch("tkinter.messagebox.showinfo"):
                color_scheme.set_scheme(scheme)
        return

