"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from typing import Any, Dict, Iterable, List, Tuple
# Packages
from PIL import Image


Color = Tuple[int, int, int]


def outer_to_inner(l: List[Any]) -> Iterable[Any]:
    """Create tuples of (first, last), (second, first-to-last), etc."""
    return list((list(l)[i], list(reversed(l))[i]) for i in range(len(l) // 2))


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


def get_similarity(template: Image.Image, to_match: Image.Image):
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


def get_similarity_monochrome(template: Image.Image, to_match: Image.Image) -> float:
    """Determine the similarity of two monochrome images"""
    t_edges, m_edges = detect_edges(template), detect_edges(to_match)
    return sum(abs(v2 - v1) < 15 for v1, v2 in zip(t_edges, m_edges) if v1 != 0) / template.height


def detect_edges(image: Image.Image) -> List[int]:
    """Detect the edges in an image"""
    results = list()
    pixels = image.load()
    for y in range(image.height):
        appended = False
        for x in range(image.width):
            if sum(pixels[x, y]) < 128:
                results.append(x)
                appended = True
                break
        if appended is False:
            results.append(0)
    return results


def get_similarity_pixels(rgb1: tuple, rgb2: tuple):
    """Return the similarity ration between two pixel tuples"""
    return 100 - sum(abs(one - two) / 255 * 100 for one, two in zip(rgb1, rgb2)) / 3


def get_brightest_pixel(image, color: int=None):
    """Return the pixel value of the brightest pixel in an image"""
    return max(image.getdata(), key=lambda pair: sum(pair if color is None else (pair[color],)))


def get_brightest_pixel_loc(image: Image.Image, color: int=None):
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


def get_brightest_pixel_cl(image: Image.Image, color: int=None):
    """Return the coordinates and color tuple for the brightest pixel"""
    max_value = 0
    max_coords: Tuple[int, int] = None
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            total = sum(pixels[i, j] if color is None else (pixels[i, j][color],))
            if not total > max_value:
                continue
            max_coords = (i, j)
            max_value = total
    return max_coords, image.getpixel(max_coords)


def get_dominant_color(image: Image.Image) -> Tuple[int, int, int]:
    """Return the dominant colour in an image"""
    colors: Iterable[Tuple[Tuple[int, int, int], int]] = image.getcolors(image.width * image.height)
    colors: Dict[Tuple[int, int, int], int] = {color: count for count, color in colors}
    return max(colors, key=lambda e: colors[e])


def replace_color(image: Image.Image, source: Color, target: Color) -> Image.Image:
    """Convert a single RGB color with another color"""
    destination = image.copy().convert("RGB")
    pixels = destination.load()

    for x in range(destination.width):
        for y in range(destination.height):
            if pixels[x, y] == source:
                pixels[x, y] = target

    return destination


if __name__ == '__main__':
    import os
    from utils.directories import get_assets_directory
    folder = os.path.join(get_assets_directory(), "digits")
    x = Image.open(os.path.join(get_assets_directory(), "digits", "1.png"))
    for digit in os.listdir(folder):
        if not digit.endswith(".png"):
            continue
        image = Image.open(os.path.join(folder, digit))
        s = get_similarity_monochrome(image, x)
        print("{}: {}".format(digit, s))
        # assert s == 1.0
