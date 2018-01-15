"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from parsing import vision
from PIL import Image
from utils.directories import get_assets_directory
from parsing.gsfinterface import GSFInterface
from os import path


class TestVision(TestCase):
    def setUp(self):
        self.image = Image.open(path.join(get_assets_directory(), "vision", "test.png"))
        self.gui_parser = GSFInterface("Default.xml")

    def test_attributes(self):
        self.assertIsInstance(vision.colors, dict)
        self.assertIsInstance(vision.timer_boxes, dict)

    def test_get_pointer_middle(self):
        result = vision.get_pointer_middle((960, 540))
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_get_tracking_degrees(self):
        result = vision.get_tracking_degrees(234)
        self.assertIsInstance(result, float)

    def test_get_tracking_penalty(self):
        result = vision.get_tracking_penalty(10, 5, 5, 38)
        self.assertIsInstance(result, (float, int))
        self.assertGreaterEqual(result, 0)

    def test_get_ship_health_shields(self):
        coords = self.gui_parser.get_ship_health_coordinates()
        result = vision.get_ship_health_shields(self.image, coords)
        print(result)







