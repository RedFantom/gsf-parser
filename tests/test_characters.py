"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from unittest import TestCase
# Project Modules
from parsing.characters import CharacterDatabase


class TestCharacterDatabase(TestCase):
    def setUp(self):
        self.db = CharacterDatabase()

    def test_initialization(self):
        self.assertTrue(("DM", "Example") in self.db)

    def test_update_servers(self):
        UPDATED = {
            "DM": "DM1",
            "SF": "SF1",
            "TL": "TL1",
            "TF": "TF1"
        }
        self.db.update_servers(UPDATED)
        self.assertTrue(("DM1", "Example") in self.db)

    def test_get_dictionaries(self):
        legacies = self.db.get_player_legacies()
        servers = self.db.get_player_servers()
        self.assertIsInstance(legacies, dict)
        self.assertIsInstance(servers, dict)
        self.assertTrue(legacies["Example"] == "E_Legacy")
        self.assertTrue(servers["Example"] == "DM")
