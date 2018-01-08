# -*- coding: utf-8 -*-

"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""


def get_similarity(template, to_match):
    """
    Compares two images and returns the similarity ratio. Based upon code of a StackOverflow question that I can't seem
    to find to put the link here. Anyway, RedFantom has rewritten this code to work with Python 3 and to comply with
    PEP-8.
    :param template: Image object or path
    :param to_match: Image object or path
    :return: ratio
    """
    if template.size != to_match.size:
        raise ValueError("These images are not the same size. One: {}, Two: {}.".format(template.size, to_match.size))
    diff = sum(abs(color_one - color_two) for pair_one, pair_two in zip(template.getdata(), to_match.getdata())
               for color_one, color_two in zip(pair_one, pair_two) if not pair_two == (255, 255, 255))
    ncomponents = template.size[0] * template.size[1] * 3
    return (diff / 255.0 * 100) / ncomponents


def get_similarity_pixels(rgb1, rgb2):
    return sum(abs(one - two) for one, two in zip(rgb1, rgb2)) / 255.0


def get_brightest_pixel(image):
    return max(image.getdata(), key=lambda pair: sum(pair))
