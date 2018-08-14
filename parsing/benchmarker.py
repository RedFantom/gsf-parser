"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from typing import Any, Dict, Tuple
# Project Modules
import variables


PERF: Dict[str, Tuple[int, float]] = dict()
SLOW: Dict[str, float] = dict()


def benchmark(key: str) -> callable:
    """Function decorator that records the performance of function"""
    global PERF, SLOW

    def outer(func: callable) -> callable:
        """Enable function performance measurement if enabled"""
        if not variables.settings["screen"]["perf"] is True:
            return func

        def benchmark(*args) -> Tuple[Any, float]:
            """Call the function and record its performance"""
            start = datetime.now()
            r = func(*args)
            elapsed = (datetime.now() - start).total_seconds()
            PERF[key][0] += 1
            PERF[key][1] += elapsed
            return r, elapsed

        # Record slow features if disabling them is enabled
        if variables.settings["screen"]["disable"] is True:
            def inner(*args) -> Any:
                r, elapsed = benchmark(*args)
                v = 1.0 if elapsed > 0.25 else -0.5
                if key not in SLOW:
                    SLOW[key] = 0
                SLOW[key] += v
                return r
        else:
            def inner(*args) -> Any:
                return benchmark(*args)[0]

        return inner
    return outer
