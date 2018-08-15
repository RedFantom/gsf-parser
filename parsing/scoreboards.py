"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from multiprocessing import Process
import os
from os import path
from shelve import Shelf
import shelve
from PIL import Image
from typing import Any, Dict, List
# Project Modules
from parsing import opencv, tesseract
from utils.directories import get_temp_directory, get_assets_directory


class ScoreboardDatabase(object):
    """Shelf that stores the results of Scoreboard parsing"""

    def __init__(self):
        """Initialize the Shelf and open the file"""
        self._path = path.join(get_temp_directory(), "scoreboards.db")
        self._shelf: Shelf = shelve.open(self._path, writeback=True)

    def save_scoreboard(self, match: datetime, scoreboard: Dict[str, Any]):
        """Save a scoreboard in the database"""
        self._shelf[match] = scoreboard

    @staticmethod
    def get_scoreboard(match: datetime):
        """Return the scoreboard for a match given the datetime key"""
        with ScoreboardDatabase() as db:
            if match not in db:
                return None
            return db[match]

    def __enter__(self):
        """Context manager: Open shelf"""
        return self

    def __exit__(self):
        """Context manager: Close shelf"""
        self._shelf.close()

    def __getitem__(self, item: datetime):
        """Dict accessor for shelf"""
        return self._shelf[item]


class ScoreboardParser(Process):
    """
    Parse a Scoreboard in a separate Process and save its results

    Runs the parsing in a separate process to ensure that the main
    process is not influenced. Saves the data in the ScoreboardDatabase,
    with the match start time (single datetime) as key.
    """

    FOLDER = path.join(get_assets_directory(), "headers")
    SCALES: Dict[float, Image.Image] = {
        float(file[:-4]): Image.open(path.join(FOLDER, file)) for file in os.listdir(FOLDER)}

    def __init__(self, screenshot: Image.Image):
        pass

    @staticmethod
    def is_scoreboard(screenshot: Image.Image) -> (None, float):
        """Determine whether the screenshot is a screenshot of a scoreboard"""
        ratios: Dict[float: float] = {
            opencv.template_match(screenshot, template, True)[2]: scale
            for scale, template in ScoreboardParser.SCALES.items()}
        ratio: float = max(ratios.keys())
        if ratio < 90:
            return None
        return ratios[ratio]
