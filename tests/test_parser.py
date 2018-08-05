"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
from unittest import TestCase
from datetime import datetime
# Project Modules
from parsing.parser import Parser
from utils.directories import get_assets_directory


class TestParser(TestCase):
    LINE = "[22:00:04.473] " \
           "[2963000048128] " \
           "[2963000048240] " \
           "[Quad Laser Cannon {3292272821010432}] " \
           "[ApplyEffect {836045448945477}: Damage {836045448945501}] " \
           "(296 kinetic {836045448940873})\n"
    FILE = os.path.join(get_assets_directory(), "log.txt")
    EFFECT = "[22:00:34.080] " \
             "[2963000049645] " \
             "[2963000049645] " \
             "[Wingman {3314872938921984}] " \
             "[Event {836045448945472}: AbilityActivate {836045448945479}] " \
             "()\n"

    def test_read_file(self):
        lines = Parser.read_file(self.FILE)
        self.assertIsInstance(lines, list)
        self.assertIsInstance(lines[0], dict)

    def test_line_to_dictionary(self):
        line_dict = Parser.line_to_dictionary(self.LINE)
        self.assertIsInstance(line_dict, dict)
        KEYS = ["time", "source", "target", "target", "amount", "ability", "effect"]
        for key in KEYS:
            self.assertTrue(key in line_dict)
        self.assertIsInstance(line_dict["time"], datetime)
        if not isinstance(line_dict["time"], datetime):
            raise ValueError
        self.assertEqual(line_dict["time"].hour, 22)
        self.assertEqual(line_dict["source"], "2963000048128")
        self.assertEqual(line_dict["target"], "2963000048240")
        self.assertEqual(line_dict["ability"], "Quad Laser Cannon")
        self.assertTrue("Damage" in line_dict["effect"])
        self.assertEqual(int(line_dict["amount"]), 296)

    def test_get_abilities_dict(self):
        lines = Parser.read_file(self.FILE)
        abilities = Parser.get_abilities_dict(lines)
        self.assertIsInstance(abilities, dict)

    def test_get_effects_ability_eligible(self):
        with open(self.FILE) as fi:
            lindex = fi.readlines()
            index = lindex.index(self.EFFECT)
            no_effect = lindex.index(self.LINE)
        lines = Parser.read_file(self.FILE)
        line = Parser.line_to_dictionary(lines[index])
        effect = Parser.get_effects_ability(line, lines, "2963000049645")
        self.assertIsInstance(effect, dict)
        self.assertTrue(len(effect) > 0)
        # Tests get_effects_eligible
        self.assertFalse(Parser.get_effects_ability(lines[no_effect], lines, "2963000048240"))

    def test_get_event_category(self):
        line = Parser.line_to_dictionary(self.LINE)
        self.assertEqual(Parser.get_event_category(line, "2963000048240"), "dmgt_pri")
        line = Parser.line_to_dictionary(self.EFFECT)
        self.assertEqual(Parser.get_event_category(line, "2963000049645"), "other")

    def test_compare_ids(self):
        self.assertTrue(Parser.compare_ids("id", "id"))
        self.assertFalse(Parser.compare_ids("id", "id1"))
        self.assertTrue(Parser.compare_ids("id", ["id1", "id2", "id"]))
        self.assertFalse(Parser.compare_ids("id", ["id1", "id2"]))
        self.assertRaises(ValueError, lambda: Parser.compare_ids("id", ("id1", "id2")))

    def test_get_player_name(self):
        with open(self.FILE) as fi:
            lines = fi.readlines()
        self.assertEqual(Parser.get_player_name(lines), "Redfantom")

    def test_get_player_id_list(self):
        lines = Parser.read_file(self.FILE)
        ids = Parser.get_player_id_list(lines)
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)

    def test_get_effect_allied(self):
        line = Parser.line_to_dictionary(self.LINE)
        effect = Parser.line_to_dictionary(self.EFFECT)
        self.assertTrue(Parser.get_effect_allied(effect["ability"]))
        self.assertFalse(Parser.get_effect_allied(line["ability"]))

    def test_get_gsf_in_file(self):
        self.assertTrue(Parser.get_gsf_in_file(self.FILE))

    def test_parse_filename(self):
        result = Parser.parse_filename("combat_2017-12-26_11_27_00_541263.txt")
        self.assertIsInstance(result, datetime)
        dt = {"year": 2017, "month": 12, "day": 26, "hour": 11, "minute": 27, "second": 00}
        for key, value in dt.items():
            self.assertEqual(getattr(result, key), value)
