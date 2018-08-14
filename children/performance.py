"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Project Modules
from parsing import benchmarker


class PerformanceParser(object):
    """Tracks the performance of Screen Parsing features"""

    def __init__(self):
        """Create instance attributes"""
        self._string = "No slow screen parsing features"
        self._disabled = list()

    def update(self):
        """Check the performance of features, build a string"""
        for feature, count in benchmarker.SLOW.items():
            if feature in self._disabled:
                continue
            if count > 10:
                self._disabled.append(feature)
                print("[PerformanceParser] Disabled feature: '{}'".format(feature))
        string = ""
        for feature, (count, time) in benchmarker.PERF.items():
            if count == 0 or time / count < 0.25:  # Max 0.25s/cycle
                continue
            string += "{}: {:.3f}s".format(feature, time / count)
            if feature in self._disabled:
                string += ", disabled"
            string += "\n"
        self._string = string

    def string(self) -> str:
        """Return the string for display in the UI"""
        return self._string

    def disabled(self) -> list:
        """Return a list of disabled features"""
        return self._disabled
