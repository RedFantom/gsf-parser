"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
# Packages
from PIL import Image
# Project Modules
from parsing.benchmarker import benchmark
from parsing import GUIParser, Parser, vision


class SpawnParser(object):
    """Spawn Timer Parser"""

    INIT_ARGS = [GUIParser]

    MARGIN = 20

    def __init__(self, gui: GUIParser):
        """Create instance attributes"""
        self._start: datetime = None
        self._waiting: datetime = None
        self._scale: float = gui.get_element_scale("Global")

    @benchmark("Spawn Timer")
    def process_screenshot(self, screenshot: Image.Image, time: datetime):
        """Process a screenshot"""
        if self._start is not None or self._waiting is None:
            return
        if (time - self._waiting).total_seconds() < SpawnParser.MARGIN:
            print("[SpawnParser] Stopped waiting for a timer")
            self._waiting = None
            return
        print("[SpawnParser] Active")
        # TODO: Build a new implementation of Spawn Timer

    def process_event(self, event: dict, active_ids: list):
        """Enable SpawnParser if event is a Login event"""
        if Parser.is_login(event):
            self._waiting = datetime.combine(datetime.now().date(), event["time"].time())

    def string(self) -> str:
        """Return a properly formatted string for in the overlay"""
        return ""

    def match_end(self):
        """Callback for match end"""
        self._start, self._waiting = None, None

    def match_start(self):
        """Callback for match start"""
        self._waiting = None
