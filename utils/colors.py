"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""


def color_darken(rgb: tuple, factor: float):
    """Reduce the brightness by 1 - factor"""
    return tuple(max(int(item * factor), 0) for item in rgb)


def color_tuple_to_hex(rgb: tuple):
    """Convert a color tuple to a hex color value"""
    rgb = tuple(int(round(item)) for item in rgb)
    return "#" + format(rgb[0] << 16 | rgb[1] << 8 | rgb[2], '06x')


def color_hex_to_tuple(hex: str):
    """Convert a hex color value to an RGB tuple"""
    return tuple(int(hex.replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))


def color_background(color: (str, tuple)):
    """Return appropriate white or black background for color"""
    if isinstance(color, str):
        color = color_hex_to_tuple(color)
    red, green, blue = color
    return "#000000" if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
