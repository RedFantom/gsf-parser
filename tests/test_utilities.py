"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from PIL.ImageTk import PhotoImage

import data.maps
from utils import utilities
import tkinter as tk
import mock


class TestUtilities(TestCase):
    GAME_MODES = ("dom", "tdm")

    def test_get_pointer_position(self):
        position = utilities.get_cursor_position()
        self.assertIsInstance(position, tuple)
        self.assertEqual(len(position), 2)

    def test_get_screen_resolution(self):
        resolution = utilities.get_screen_resolution()
        self.assertIsInstance(resolution, tuple)
        self.assertEqual(len(resolution), 2)

    def test_map_dictionary(self):
        self.assertIsInstance(data.maps.map_dictionary, dict)
        for mode in self.GAME_MODES:
            self.assertTrue(mode in data.maps.map_dictionary)
            self.assertIsInstance(data.maps.map_dictionary[mode], dict)
        return

    def test_open_icon(self):
        tk.Tk()
        photo = utilities.open_icon("missilesalvo")
        self.assertIsInstance(photo, PhotoImage)
        photo = utilities.open_icon("improvedelectronicwarfarepod.jpg")
        self.assertIsInstance(photo, PhotoImage)
        self.assertRaises(ValueError, lambda: utilities.open_icon(b"missilesalvo"))
        with mock.patch("tkinter.messagebox.showinfo"):
            photo = utilities.open_icon("very_much_invalid")
        self.assertIsInstance(photo, PhotoImage)
