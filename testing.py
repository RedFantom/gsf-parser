# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import unittest
import parse
from datetime import datetime


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
        print file_cube
        print match_timings
        print spawn_timings
        self.assertTrue(isinstance(file_cube, list))
        self.assertTrue(isinstance(match_timings, list))
        self.assertTrue(isinstance(spawn_timings, list))
        self.assertTrue(isinstance(file_cube[0], list))
        self.assertTrue(isinstance(file_cube[0][0], list))
        self.assertTrue(isinstance(match_timings[0], datetime))


unittest.main()
