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
from parsing import RealTimeParser
from parsing import tesseract
from utils.directories import get_assets_directory


class MockRealTimeParser(RealTimeParser):
    """RealTimeParser subclass to handle only Timer Parsing"""

    class _interface:
        global_scale: float = 1.05

    TIMER_MARGIN = 20

    def __init__(self):
        """Initialize attributes Timer Parsing requires"""
        self._waiting_for_timer: datetime = None
        self._spawn_time: datetime = None
        self._ready_button_img: Image.Image = None
        self.is_match: bool = False


class TestTimerParsing(TestCase):
    """Test the TimerParser within the RealTimeParser"""

    def setUp(self):
        self.parser = MockRealTimeParser()
        self.sample = Image.open(path.join(get_assets_directory(), "vision", "test_timer.png"))

    def test_timer_parser(self):
        """Test the TimerParser by asserting that it yields a result"""
        if not tesseract.is_installed():
            return  # Skip this test
        self.parser._waiting_for_timer = datetime.now()
        self.parser.update_timer_parser(self.sample, datetime.now())
        self.assertNotEqual(self.parser._spawn_time, None)
        self.assertIsInstance(self.parser._spawn_time, datetime)
