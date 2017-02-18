import unittest
import parse
from datetime import datetime


class TestParseFunctions(unittest.TestCase):
    def test_determinePlayerName(self):
        with open("CombatLog.txt") as log:
            self.assertEqual(parse.determinePlayerName(log.readlines()), "Redfantom")

    def test_determinePlayer(self):
        with open("CombatLog.txt") as log:
            self.assertEqual(parse.determinePlayer(log.readlines()),
                             ["20373000057112", "20477000009562"])

    def test_splitter(self):
        with open("CombatLog.txt") as log:
            player = parse.determinePlayer(log.readlines())
            file_cube, match_timings, spawn_timings = parse.splitter(log.readlines(), player)
            self.assertTrue(isinstance(file_cube, list))
            self.assertTrue(isinstance(match_timings, list))
            self.assertTrue(isinstance(spawn_timings, list))
            self.assertTrue(isinstance(file_cube[0], list))
            self.assertTrue(isinstance(file_cube[0][0], list))
            self.assertTrue(isinstance(match_timings[0], datetime.datetime))


unittest.main()
