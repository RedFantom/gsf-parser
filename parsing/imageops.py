"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from PIL import Image


def get_similarity_transparent(template: Image.Image, to_match: Image.Image):
    """Compare two images in RGBA format"""
    if template.size != to_match.size:
        raise ValueError("These images are not the same size")
    if not template.mode == "RGBA":
        template = template.convert("RGBA")
    if not to_match.mode == "RGBA":
        to_match.convert("RGBA")
    diff = sum(abs(c1 - c2) for p1, p2 in zip(template.getdata(), to_match.getdata())
               for c1, c2 in zip(p1[:3], p2[:3]) if not p1[3] == 0)
    n_comps = template.size[0] * template.size[1] * 3
    return 100 - (diff / 255.0 * 100) / n_comps


def get_similarity(template, to_match):
    """
    Compares two images and returns the similarity ratio. Based upon
    code of a StackOverflow question that I can't seem to find to put
    the link here. Anyway, RedFantom has rewritten this code to work
    with Python 3 and to comply with PEP-8.
    :param template: Image object or path
    :param to_match: Image object or path
    :return: similarity ratio between the two images
    """
    if template.size != to_match.size:
        raise ValueError("These images are not the same size. One: {}, Two: {}.".format(template.size, to_match.size))
    diff = sum(abs(color_one - color_two) for pair_one, pair_two in zip(template.getdata(), to_match.getdata())
               for color_one, color_two in zip(pair_one, pair_two) if not pair_two == (255, 255, 255))
    n_comps = template.size[0] * template.size[1] * 3
    return 100 - (diff / 255.0 * 100) / n_comps


def get_similarity_pixels(rgb1: tuple, rgb2: tuple):
    """Return the similarity ration between two pixel tuples"""
    return 100 - sum(abs(one - two) / 255 * 100 for one, two in zip(rgb1, rgb2)) / 3


def get_brightest_pixel(image, color: int=None):
    """Return the pixel value of the brightest pixel in an image"""
    return max(image.getdata(), key=lambda pair: sum(pair if color is None else (pair[color],)))


def get_brightest_pixel_loc(image, color: int=None):
    """Return the coordinates of the brightest pixel"""
    max_value = 0
    max_coords = None
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            total = sum(pixels[i, j] if color is None else (pixels[i, j][color],))
            if not total > max_value:
                continue
            max_coords = (i, j)
            max_value = total
    return max_coords


def get_brightest_pixel_cl(image, color: int=None):
    """Return the coordinates and color tuple for the brightest pixel"""
    max_value = 0
    max_coords = None
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            total = sum(pixels[i, j] if color is None else (pixels[i, j][color],))
            if not total > max_value:
                continue
            max_coords = (i, j)
            max_value = total
    return max_coords, image.getpixel(max_coords)
