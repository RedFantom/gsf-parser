# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import unittest
from datetime import datetime
import os
from PIL import Image
import mock
import sys


class TestParseFunctions(unittest.TestCase):
    def setUp(self):
        with open("CombatLog.txt", "r") as log:
            self.lines = log.readlines()

    def test_determinePlayerName(self):
        self.assertEqual(parse.determinePlayerName(self.lines), "Redfantom")

    def test_determinePlayer(self):
        self.assertEqual(parse.determinePlayer(self.lines),
                         {'20477000009562': 3, '20373000057112': 7})

    def test_splitter(self):
        player = parse.determinePlayer(self.lines)
        file_cube, match_timings, spawn_timings = parse.splitter(self.lines, player)
        self.assertIsInstance(file_cube, list)
        self.assertIsInstance(match_timings, list)
        self.assertIsInstance(spawn_timings, list)
        self.assertIsInstance(file_cube[0], list)
        self.assertIsInstance(file_cube[0][0], list)
        self.assertIsInstance(match_timings[0], datetime)

    def test_parse_spawn_one(self):
        player = parse.determinePlayer(self.lines)
        file_cube, match_timings, spawn_timings = parse.splitter(self.lines, player)
        stats_tuple = parse.parse_spawn(file_cube[0][0], player)
        self.assertIsInstance(stats_tuple, tuple)
        self.assertEqual(len(stats_tuple), 12)
        self.assertIsInstance(stats_tuple[0], dict)    # abilities
        self.assertIsInstance(stats_tuple[1], int)     # damagetaken
        self.assertIsInstance(stats_tuple[2], int)     # damagedealt
        self.assertIsInstance(stats_tuple[3], int)     # healingreceived
        self.assertIsInstance(stats_tuple[4], int)     # selfdamage
        self.assertIsInstance(stats_tuple[5], list)    # enemies
        self.assertIsInstance(stats_tuple[6], int)     # criticalcount
        self.assertIsInstance(stats_tuple[7], float)   # criticalluck
        self.assertIsInstance(stats_tuple[8], int)     # hitcount
        self.assertIsInstance(stats_tuple[9], list)    # ships_list
        self.assertIsInstance(stats_tuple[10], dict)   # enemydamaged
        self.assertIsInstance(stats_tuple[11], dict)   # enemydamaget
        self.assertEqual(len(stats_tuple[0]), 3)
        self.assertTrue("Cluster Missiles" in stats_tuple[0])
        self.assertTrue("Nullify" in stats_tuple[0])
        self.assertTrue("Charged Plating" in stats_tuple[0])
        self.assertEqual(stats_tuple[1], 0)
        self.assertEqual(stats_tuple[2], 1450)
        self.assertEqual(stats_tuple[3], 120)
        self.assertEqual(stats_tuple[4], 378)
        self.assertEqual(len(stats_tuple[5]), 3)
        self.assertEqual(len(stats_tuple[10]), 3)
        self.assertEqual(len(stats_tuple[11]), 3)
        for enemy in stats_tuple[5]:
            self.assertTrue(enemy in stats_tuple[10] and enemy in stats_tuple[11])
        self.assertEqual(stats_tuple[6], 0)
        self.assertEqual(stats_tuple[7], 0.0)
        self.assertEqual(stats_tuple[8], 3)
        self.assertEqual(len(stats_tuple[9]), 3)
        self.assertTrue("Decimus" in stats_tuple[9])
        self.assertTrue("Quell" in stats_tuple[9])
        self.assertTrue("Rycer" in stats_tuple[9])

    def test_parse_spawn_two(self):
        player = parse.determinePlayer(self.lines)
        file_cube, match_timings, spawn_timings = parse.splitter(self.lines, player)
        stats_tuple = parse.parse_spawn(file_cube[1][0], player)
        self.assertIsInstance(stats_tuple, tuple)
        self.assertEqual(len(stats_tuple), 12)
        self.assertIsInstance(stats_tuple[0], dict)    # abilities
        self.assertIsInstance(stats_tuple[1], int)     # damagetaken
        self.assertIsInstance(stats_tuple[2], int)     # damagedealt
        self.assertIsInstance(stats_tuple[3], int)     # healingreceived
        self.assertIsInstance(stats_tuple[4], int)     # selfdamage
        self.assertIsInstance(stats_tuple[5], list)    # enemies
        self.assertIsInstance(stats_tuple[6], int)     # criticalcount
        self.assertIsInstance(stats_tuple[7], float)   # criticalluck
        self.assertIsInstance(stats_tuple[8], int)     # hitcount
        self.assertIsInstance(stats_tuple[9], list)    # ships_list
        self.assertIsInstance(stats_tuple[10], dict)   # enemydamaged
        self.assertIsInstance(stats_tuple[11], dict)   # enemydamaget
        self.assertEqual(stats_tuple[0], {'Ion Railgun': 1,
                                          'Distortion Field': 1,
                                          'Barrel Roll': 1})
        self.assertEqual(stats_tuple[9], ["Mangler"])
        self.assertEqual(stats_tuple[1], 624)
        self.assertEqual(stats_tuple[2], 1400)
        self.assertEqual(stats_tuple[3], 0)
        self.assertEqual(stats_tuple[4], 0)
        self.assertEqual(stats_tuple[5], ["20477000009322", "20477000009356"])
        self.assertEqual(stats_tuple[6], 0)
        self.assertEqual(stats_tuple[7], 0.0)
        self.assertEqual(stats_tuple[8], 1)
        self.assertEqual(stats_tuple[10], {"20477000009322": 624,
                                           "20477000009356": 0})
        self.assertEqual(stats_tuple[11], {"20477000009356": 1400,
                                           "20477000009322": 0})


class TestVision(unittest.TestCase):
    def test_get_pointer_position(self):
        example_image = Image.open(os.getcwd() + "/assets/vision/testing.png")
        if sys.platform == "win32":
            with mock.patch('PIL.ImageGrab.grab', return_value=example_image):
                coordinates = vision.get_pointer_position()
        else:
            coordinates = vision.get_pointer_position()
        self.assertEqual(coordinates, (491, 914))
        mid_coord = vision.get_pointer_middle(coordinates)
        self.assertEqual(mid_coord, (513, 936))
        distance = vision.get_distance_from_center(mid_coord)
        self.assertEqual(distance, 597.18)
        tracking_degrees = vision.get_tracking_degrees(distance, 20, 0.1)
        self.assertEqual(tracking_degrees, 2.99)
        tracking_penalty = vision.get_tracking_penalty(tracking_degrees, 2)
        self.assertEqual(tracking_penalty, 6.0)


def grab():
    return Image.open(os.getcwd() + "/assets/vision/testing.png")

if __name__ == "__main__":
    print "\n"
    from parsing import parse, vision
    unittest.main()
