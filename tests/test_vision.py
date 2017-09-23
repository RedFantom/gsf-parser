# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from unittest import TestCase
from parsing.vision import *
from PIL import Image
from tools.utilities import get_assets_directory
from os import path, listdir
from parsing.guiparsing import GSFInterface


class TestVision(TestCase):
    def setUp(self):
        self.filename = path.join(get_assets_directory(), "vision", "testing.png")
        self.image = Image.open(self.filename)
        self.screen = pillow_to_numpy(self.image)
        self.gui = GSFInterface("Default")

    def test_get_timer_status(self):
        for filename in listdir(path.join(get_assets_directory(), "timers")):
            image_path = path.join(get_assets_directory(), "timers", filename)
            source = Image.open(image_path)
            result = get_timer_status(source)
            self.assertEqual(result, int(filename.replace(".jpg", "")))
        return

    def test_get_power_management(self):
        coordinates = self.gui.get_ship_powermgmt_coordinates()
        power_management = get_power_management(self.screen, *coordinates)
        self.assertEqual(power_management, 3)

    def test_get_ship_health_shields(self):
        coordinates = self.gui.get_ship_health_coordinates()
        print(coordinates)
        result = get_ship_health_shields(self.image, coordinates)
        self.assertEqual(len(result), 2)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])
        self.assertEqual(result, (87.5, 87.5))
