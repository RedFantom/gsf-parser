"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
import os
import pickle
from threading import Lock
from typing import Dict, Tuple, Any
# UI Libraries
from tkinter import messagebox
# Project Modules
from utils.directories import get_temp_directory

DATA_DICT = Dict[str, Any]
SPAWN_DICT = Dict[datetime, DATA_DICT]
MATCH_DICT = Dict[datetime, SPAWN_DICT]
DATABASE = Dict[str, MATCH_DICT]


class RealTimeDB(object):
    """
    Read and Write interface for pickle only stored on disk, not in mem

    The interface is thread-safe and implements the dictionary
    interface, as the data is stored in a dictionary.

    file (str): {
            match (datetime): {
                spawn (datetime): {
                    key (str): data (dict, object, None)

    Each spawn offers the following data keys:
    >>> {
    >>> "clicks": Dict[datetime, Tuple[bool, Button]],
    >>> "cursor_pos": Dict[datetime, Tuple[int, int]],
    >>> "distance": Dict[datetime, float],
    >>> "health": Dict[datetime, Tuple[float, float, float]],
    >>> "keys": Dict[datetime, Tuple[str, bool]],
    >>> "map": Tuple[str, str],
    >>> "score": float,
    >>> "shots": Dict[datetime, Tuple[bool, int, int]],
    >>> "ship": Ship,
    >>> "tracking": Dict[datetime, float],
    >>> }
    """

    SPAWN_DICT = {
        "clicks": dict(),
        "cursor_pos": dict(),
        "distance": dict(),
        "health": dict(),
        "keys": dict(),
        "map": None,
        "score": None,
        "ship": None,
        "shots": dict(),
        "tracking": dict(),
    }

    LOCK = None

    def __init__(self):
        """Initialize dict, read data from disk and type"""
        self._path = os.path.join(get_temp_directory(), "realtime.db")
        self._file, self._match, self._spawn = None, None, None
        self._spawn_data: DATA_DICT = None
        if self.LOCK is None:
            self.LOCK = Lock()
        self._lock = self.LOCK

    def __getitem__(self, key: str) -> dict:
        """Return a file dictionary"""
        with self._lock and open(self._path, "rb") as fi:
            return pickle.load(fi)[key]

    def __setitem__(self, key: str, value: MATCH_DICT):
        """Set a file dictionary"""
        data = self.get_data()
        data[key] = value
        self.save_data(data)

    @property
    def data(self) -> (DATABASE, None):
        """Return a full copy of the data in the file"""
        try:
            with self._lock and open(self._path, "rb") as fi:
                return pickle.load(fi).copy()
        except EOFError:
            messagebox.showerror(
                "Error", "The GSF Parser real-time results database has been corrupted. "
                         "A new one will be created, discarding all your old data.")
            self.save_data(dict())
            return dict()

    def save_data(self, data: DATABASE):
        """Save data to the file in the right format"""
        with self._lock and open(self._path, "wb") as fo:
            pickle.dump(data, fo)

    @staticmethod
    def get_data() -> DATABASE:
        """Return a copy of the data without an instance"""
        return RealTimeDB().data

    def set_spawn(self, file: str, match: datetime, spawn: datetime):
        """Set a spawn as being active and cache the data for it"""
        match, spawn = map(self.replace_date, (match, spawn))
        if self._spawn_data is not None:
            self.write_spawn_data()
        with self._lock:
            self._file, self._match, self._spawn = file, match, spawn
        self.create_spawn()

    def create_spawn(self):
        """Create a new spawn dictionary with the data keys"""
        with self._lock:
            self._spawn_data = self.SPAWN_DICT.copy()
        self.write_spawn_data()

    def write_spawn_data(self):
        """Write the data stored in the current spawn dict to the file"""
        if None in (self._file, self._match, self._spawn):
            return
        data = self.data
        with self._lock:
            if self._file not in data:
                data[self._file] = dict()
            if self._match not in data:
                data[self._file][self._match] = dict()
            data[self._file][self._match][self._spawn] = self._spawn_data
        self.save_data(data)

    def set_for_spawn(self, key: str, *args: (Tuple[Any], Tuple[datetime, Any])):
        """Set a value for a spawn in either spawn or key dict"""
        if self._spawn_data is None:
            return
        with self._lock:
            if len(args) == 1:
                value, = args
                self._spawn_data[key] = value
            else:
                time, value = args
                self._spawn_data[key][time] = value

    def get_for_spawn(self, key: str) -> Any:
        """Get a value from the cached data for the set spawn"""
        if self._spawn_data is None:
            return None
        with self._lock:
            return self._spawn_data[key]

    @staticmethod
    def replace_date(moment: datetime) -> datetime:
        """Replace the date of a datetime if it is not set"""
        if moment.year != 1970:
            return moment
        return datetime.combine(datetime.now().date(), moment.time())
