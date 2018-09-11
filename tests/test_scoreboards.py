"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from os import path
from unittest import TestCase
# Packages
from PIL import Image
# Project Modules
from parsing.scoreboards import ScoreboardParser
from parsing import tesseract
from utils.directories import get_assets_directory


class TestScoreboardParser(TestCase):
    """Test the ScoreboardParser(Process)"""

    def setUp(self):
        """Read image to parse"""
        self.image = Image.open(path.join(get_assets_directory(), "vision", "test_scoreboard.png"))
        self.match = datetime.fromtimestamp(0)
        self.parser = ScoreboardParser(self.match, self.image)

    def test_is_scoreboard(self):
        start = datetime.now()
        r = self.parser.is_scoreboard(self.image, 1.05)
        print("[TestScoreboardParser] Performance: {:04.2f}s".format((datetime.now() - start).total_seconds()))
        self.assertTrue(r)

    def test_parse_scoreboard(self):
        if not tesseract.is_installed():
            return
        r: dict = self.parser.parse_scoreboard()
        self.assertTrue(all(k in r for k in ("allies", "enemies", "score")))
        self.assertIsInstance(r, dict)
        self.assertIsInstance(r["allies"], list)
        self.assertIsInstance(r["enemies"], list)

    def test_run_scoreboard(self):
        if not tesseract.is_installed():
            return
        self.parser.start()
        while self.parser.is_alive():
            pass
