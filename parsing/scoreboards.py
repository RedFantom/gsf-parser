"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from multiprocessing import Process, Pipe, Event
import os
from os import path
import pickle
from PIL import Image
from typing import Any, Dict, List, Tuple
# Project Modules
from parsing import imageops, opencv, tesseract
from utils.directories import get_temp_directory, get_assets_directory

FOLDER = path.join(get_assets_directory(), "headers")


class ScoreboardDatabase(object):
    """Shelf that stores the results of Scoreboard parsing"""

    def __init__(self):
        """Initialize the Shelf and open the file"""
        self._path = path.join(get_temp_directory(), "scoreboards.db")
        self._shelf: dict = self.read_database()

    def read_database(self) -> dict:
        """Open the pickle and read from it"""
        if not path.exists(self._path):
            self._shelf = dict()
            self.save_database()
        with open(self._path, "rb") as fi:
            return pickle.load(fi)

    def save_database(self):
        """Save the data to the pickle"""
        with open(self._path, "wb") as fo:
            pickle.dump(self._shelf, fo)

    def save_scoreboard(self, match: datetime, scoreboard: Dict[str, Any]):
        """Save a scoreboard in the database"""
        if match in self._shelf:
            scoreboard = self.merge_scoreboards(self._shelf[match], scoreboard)
        self._shelf[match] = scoreboard
        self.save_database()

    @staticmethod
    def merge_scoreboards(scoreboard1: Dict[str, Any], scoreboard2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two scoreboards to a single scoreboard"""
        allies1, allies2 = scoreboard1["allies"], scoreboard2["allies"]
        enemies1, enemies2 = scoreboard1["enemies"], scoreboard2["enemies"]
        allies1.extend(allies2)
        enemies1.extend(enemies2)
        allies = list(set(allies1))
        enemies = list(set(enemies1))
        scoreboard1["allies"], scoreboard1["enemies"] = allies, enemies
        return scoreboard1

    @staticmethod
    def get_scoreboard(match: datetime):
        """Return the scoreboard for a match given the datetime key"""
        with ScoreboardDatabase() as db:
            if match not in db._shelf:
                return None
            return db[match]

    def __enter__(self):
        """Context manager: Open shelf"""
        return self

    def __exit__(self, exception: Exception, value: int, traceback: str):
        """Context manager: Close shelf"""
        if exception is not None:
            print("[ScoreboardDatabase] Unhandled context error: {}, {}, {}".format(
                exception, value, traceback))
        self.save_database()

    def __getitem__(self, item: datetime):
        """Dict accessor for shelf"""
        if item not in self._shelf:
            return None
        return self._shelf[item]


class ScoreboardParser(Process):
    """
    Parse a Scoreboard in a separate Process and save its results

    Runs the parsing in a separate process to ensure that the main
    process is not influenced. Saves the data in the ScoreboardDatabase,
    with the match start time (single datetime) as key.
    """
    SCALES: Dict[float, Image.Image] = {
        float(file[:-4]): Image.open(path.join(FOLDER, file)) for file in os.listdir(FOLDER)}
    HEIGHT: int = 430
    WIDTH: int = 1190
    COLUMNS: List[str] = ["name", "kills", "assists", "deaths", "damage", "hit", "objectives"]
    WIDTHS: Dict[str, float] = {
        "name": 280 / WIDTH,
        "kills": 130 / WIDTH,
        "assists": 130 / WIDTH,
        "deaths": 130 / WIDTH,
        "damage": 130 / WIDTH,
        "hit": 130 / WIDTH,
        "objectives": 130 / WIDTH,
    }

    def __init__(self, match_start: datetime, screenshot: Image.Image):
        """Initialize a scoreboard parsing process"""
        self._match: datetime = match_start
        self._screenshot: Image.Image = screenshot
        self._db: ScoreboardDatabase = None
        self._recv, self._send = Pipe(False)
        self._progress: float = 0.0
        self._done = Event()
        self._started = Event()

    def start(self):
        """Handler to start the Process"""
        if self._started.is_set():
            return
        self._started.set()
        Process.start(self)

    def run(self):
        """Parse the Scoreboard and save its data"""
        result = self.parse_scoreboard()
        with ScoreboardDatabase() as db:
            db.save_scoreboard(self._match, result)
        self._send.send(-1)
        self._done.set()

    def parse_scoreboard(self) -> Dict[str, Any]:
        """Parse the scoreboard"""
        print("[ScoreboardParser] Parsing scoreboard")
        scoreboard: Dict[str, Any] = {"allies": list(), "enemies": list()}
        scale, location = self.get_scale_location(self._screenshot)
        rows: List[List[Image.Image]] = self.split_scoreboard(self._screenshot, scale, location)
        todo, done = sum(len(row) for row in rows), 0
        for i, row in enumerate(rows):
            columns: List[(str, int)] = list()
            allied = self.is_allied(row[1])
            for name, column in zip(ScoreboardParser.COLUMNS, row):
                r = tesseract.perform_ocr_scoreboard(column, name)
                columns.append(r)
                print("[ScoreboardParser] {}: {} -> {}".format(i, name, r), flush=True)
                done += 1
                self._send.send(done / todo)
            scoreboard["allies" if allied else "enemies"].append(columns)
        scoreboard["score"] = self.get_score(self._screenshot, scale, location)
        return scoreboard

    @staticmethod
    def get_score(screenshot: Image.Image, scale: float, location: Tuple[int, int]) -> Tuple[int, int, int]:
        """Parse the score on the scoreboard to (left, right, self)"""
        x, y = location
        y1, y2 = int(y - 35 * scale), int(y - 20 * scale)
        x1_l, x2_l, x1_r, x2_r = x + 50 * scale, x + 75 * scale, x + 180 * scale, 205 * scale
        left: Image.Image = screenshot.crop(tuple(map(int, (x1_l, y1, x2_l, y2))))
        right: Image.Image = screenshot.crop(tuple(map(int, (x1_r, y1, x2_r, y2))))
        score_l, score_r = map(lambda i: tesseract.perform_ocr_scoreboard(i, "score", 420, 360), (left, right))
        return score_l, score_r, list(map(ScoreboardParser.is_allied, (left, right))).index(True)

    @staticmethod
    def crop_scoreboard(image: Image.Image, scale: float, location: Tuple[int, int]) -> Image.Image:
        """Crop a screenshot of a scoreboard to only the scoreboard"""
        (w, h), (x, y) = ScoreboardParser.SCALES[scale].size, location
        return image.crop((x, y + h, x + w, int(y + h + ScoreboardParser.HEIGHT * scale)))

    @staticmethod
    def get_scale_location(screenshot: Image.Image) -> Tuple[float, Tuple[int, int]]:
        """Determine the location and scale of a scoreboard"""
        ratios: Dict[float, float] = dict()
        locations: Dict[float, Tuple[int, int]] = dict()
        for scale, template in ScoreboardParser.SCALES.items():
            ratio, location = opencv.template_match(screenshot, template, 0, True)
            ratios[ratio] = scale
            locations[scale] = location
            print("[ScoreboardParser] Scale: {}, Match ratio: {}, Location: {}".format(scale, ratio, location))
        scale: float = ratios[max(ratios.keys())]
        return scale, locations[scale]

    @staticmethod
    def is_scoreboard(image: Image.Image, scale: float):
        """Determine whether a screenshot is an image of a scoreboard"""
        return opencv.template_match(image, ScoreboardParser.SCALES[scale], 0, True)[0] > 90

    @staticmethod
    def is_allied(subsection: Image.Image) -> bool:
        """Determine whether a row is of an allied or enemy player"""
        dominant: Tuple[int, int, int] = imageops.get_dominant_color(subsection)
        return dominant[1] > dominant[0]  # Green more dominant than red

    @staticmethod
    def split_scoreboard(image: Image.Image, scale: float, location: Tuple[int, int]) -> List[List[Image.Image]]:
        """Build a matrix of sub-images of the rows of the scoreboard"""
        COLUMNS = ScoreboardParser.COLUMNS.copy()
        image = ScoreboardParser.crop_scoreboard(image, scale, location)
        result: List[List[Image.Image]] = list()
        for i in range(16):
            row_box = (0, i * (image.height / 16), image.width, (i + 1) * (image.height / 16))
            row: Image.Image = image.crop(row_box)
            columns: List[Image.Image] = list()
            for name in ScoreboardParser.COLUMNS:
                start = sum([ScoreboardParser.WIDTHS[c] * image.width for c in COLUMNS[:COLUMNS.index(name)]])
                end = start + ScoreboardParser.WIDTHS[name] * image.width
                column: Image.Image = row.crop((start, 0, end, row.height))
                columns.append(column.resize((int(30 / image.height * image.width), 30), Image.LANCZOS))
            result.append(columns)
        return result

    @property
    def string(self):
        """Return a formatted progress string"""
        while self._recv.poll():
            self._progress = self._recv.recv()
        if self._progress == -1:
            return "Scoreboard: Complete\n"
        return "Scoreboard: {:03.1f}%\n".format(self._progress * 100)

    def is_done(self):
        return self._done.is_set()
