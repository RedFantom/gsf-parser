"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from ast import literal_eval


def config_eval(value):
    """
    Safely evaluate a string that can be a in a configuration file to a
    valid Python value. Performs error handling and checks special
    cases.
    """
    try:
        literal = literal_eval(value)
    except (ValueError, SyntaxError):
        return value
    if literal == 1:
        return True
    elif literal == 0:
        return False
    else:
        return literal
