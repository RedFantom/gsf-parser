# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE


def get_similarity(image_one, image_two):
    """
    Compares two images and returns the similarity ratio. Based upon code of a StackOverflow question that I can't seem
    to find to put the link here. Anyway, RedFantom has rewritten this code to work with Python 3 and to comply with
    PEP-8.
    :param image_one: Image object or path
    :param image_two: Image object or path
    :return: ratio
    """
    if image_one.size != image_two.size:
        raise ValueError("These images are not the same size.")
    pairs = zip(image_one.getdata(), image_two.getdata())
    diff = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))
    ncomponents = image_one.size[0] * image_one.size[1] * 3
    return (diff / 255.0 * 100) / ncomponents
