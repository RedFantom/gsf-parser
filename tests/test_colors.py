"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from unittest import TestCase
import mock
# Project Modules
from data import colors
from settings.colors import ColorScheme
from utils.colors import \
    color_darken, \
    color_background, \
    color_hex_to_tuple, \
    color_tuple_to_hex


class TestColorScheme(TestCase):
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


class TestColorsModule(TestCase):
    def test_color_darken(self):
        darken = {
            ((250, 250, 250), 0.8): (200, 200, 200),
            ((250, 0, 0), 0.8): (200, 0, 0),
            ((255, 255, 255), 0.0): (0, 0, 0),
            ((255, 255, 255), 1.0): (255, 255, 255)
        }
        for (value, factor), result in darken.items():
            self.assertEqual(color_darken(value, factor), result)

    def test_color_conversion(self):
        values = {
            "#ffffff": (255, 255, 255),
            "#ff0000": (255, 0, 0),
            "#00ff00": (0, 255, 0),
            "#0000ff": (0, 0, 255),
            "#ffcc00": (255, 204, 0),
            "#9900cc": (153, 0, 204)
        }
        for hex, tup in values.items():
            self.assertEqual(color_tuple_to_hex(tup), hex)
            self.assertEqual(color_hex_to_tuple(hex), tup)
            self.assertEqual(color_tuple_to_hex(color_hex_to_tuple(hex)), hex)

    def test_color_background(self):
        backgrounds = {
            "#000000": "#ffffff",
            "#ffffff": "#000000",
            "#9900cc": "#ffffff",
            "#ffcc00": "#000000"
        }
        for key, result in backgrounds.items():
            self.assertEqual(color_background(key), result)

