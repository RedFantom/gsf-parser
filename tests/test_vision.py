# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import unittest
import os
from PIL import Image
import mock
from tools import utilities
from parsing import vision


class TestVision(unittest.TestCase):
    def test_get_pointer_position(self):
        os.chdir(os.path.realpath(os.path.dirname(__file__)))
        example_image = Image.open(os.path.join(utilities.get_assets_directory(), "vision", "testing.png"))
        with mock.patch('PIL.ImageGrab.grab', return_value=example_image):
            self.assertEqual(vision.pillow_to_numpy(example_image).all(), vision.get_cv2_screen(testing=True).all())
        example_screen = vision.pillow_to_numpy(example_image)
        coordinates = utilities.get_cursor_position(example_screen)
        self.assertEqual(coordinates, (491, 914))
        mid_coord = vision.get_pointer_middle(coordinates)
        self.assertEqual(mid_coord, (513, 936))
        distance = vision.get_distance_from_center(mid_coord)
        self.assertEqual(distance, 597.18)
        tracking_degrees = vision.get_tracking_degrees(distance, 20)
        self.assertEqual(tracking_degrees, 2.99)
        tracking_penalty = vision.get_tracking_penalty(tracking_degrees, 2)
        self.assertEqual(tracking_penalty, 6.0)

    def test_vision(self):
        os.chdir(os.path.realpath(os.path.dirname(__file__)))
        example_image = Image.open(os.path.join(utilities.get_assets_directory(), "vision", "testing.png"))
        example_screen = vision.pillow_to_numpy(example_image)
        cds = vision.get_power_management_cds(example_screen)
        self.assertEqual(vision.get_power_management(example_screen, cds), 3)
