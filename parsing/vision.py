"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import os
import math
import cv2
from PIL import Image
import numpy
from tools.utilities import get_assets_directory
from parsing.imgcompare import get_similarity, get_similarity_pixels, get_brightest_pixel
import operator

colors = {
    "blue": (2, 95, 133),
    "green": (0, 166, 0),
    "yellow": (132, 157, 0),
    "orange": (165, 94, 0),
    "red": (164, 1, 1),
    "none": (0, 0, 0)
}


def get_pointer_middle(coordinates, size=(44, 44)):
    """
    Get the coordinates of the middle of the pointer
    :param coordinates: The coordinates of the top left corner of the pointer
    :param size: The size of the pointer in pixels tuple (x, y)
    :return: A tuple with coordinates of the middle of the pointer
    """
    if size[0] % 2 == 1 or size[1] % 2 == 1 or size[0] != size[1]:
        raise ValueError("The pointer image is of an invalid size.")
    return coordinates[0] + size[0] / 2, coordinates[1] + size[1] / 2


def pillow_to_numpy(pillow):
    """
    :param pillow: Image file in Pillow format
    :return: Image file in OpenCV compatible numpy array format
    """
    imagefile = numpy.array(pillow)
    return imagefile[:, :, ::-1].copy()


def numpy_to_pillow(array):
    pillow = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    return Image.fromarray(pillow)


def get_xy_tuple(xy):
    (x, y) = xy
    return int(x), int(y)


'''
The following functions were written with the help of Close-shave, who provided
the formula for calculating the tracking penalty:
max(0, (([cursor_x] - [centerscreen_x])^2 + ([cursor_y] - [centerscreen_y])^2)^0.5 / [circumference_length] * \
    [tracking_penalty]) - [upgrade_constant]
'''


def get_distance_from_center(coordinates=(960, 540), resolution=(1920, 1080)):
    """
    Calculates the distance in pixels of the middle of the screen to the middle
    of the targeting pointer
    :param coordinates: coordinates of the **middle** of the targeting pointer
    :param resolution: tuple of resolution
    :return:
    """
    middle_screen = (resolution[0] / 2, resolution[1] / 2)
    a_squared = math.pow(abs(coordinates[0] - middle_screen[0]), 2)
    b_squared = math.pow(abs(coordinates[1] - middle_screen[1]), 2)
    c_squared = a_squared + b_squared
    c = float(math.sqrt(c_squared))
    return round(c, 2)


def get_tracking_degrees(distance, pixelsperdegree=10):
    """
    :param distance: Distance in pixels by get_distance_from_center
    :param pixelsperdegree: The pixels per firing degree (resolution dependent)
    :return: The amount of degrees for tracking penalty
    """
    return round(distance / pixelsperdegree, 2)


def get_tracking_penalty(degrees, tracking_penalty, upgrade_c, firing_arc):
    """
    :param degrees: The amount of degrees for tracking penalty
    :param tracking_penalty: The tracking penalty in %/degree
    :param upgrade_c: The upgrade constant
    :return:
    """
    return max(round(min(degrees, firing_arc) * tracking_penalty - upgrade_c, 1), 0)


def get_timer_status(source):
    """
    Determines the state of the spawn countdown timer by performing
    template matching on the cv2 array of a screenshot to find a match
    for one of the timers in the folder.
    """
    folder = os.path.join(get_assets_directory(), "timers")
    image_similarity = {}
    for img in os.listdir(folder):
        if not img.endswith(".jpg"):
            continue
        image_path = os.path.join(folder, img)
        image = Image.open(image_path)
        similarity = get_similarity(source, image)
        if similarity < 15.0:
            image_similarity[img.replace(".jpg", "")] = similarity
    if len(image_similarity) == 0:
        return None
    return int(min(image_similarity.items(), key=operator.itemgetter(1))[0])


def get_power_management(screen, weapon_cds, shield_cds, engine_cds):
    """
    Uses template matching to determine how the user has divided the power
    among the different ship components.
    :param screen: cv2 array of screenshot
    :param weapon_cds:
    :param shield_cds:
    :param engine_cds:
    :return: int 1, 2, 3, 4
             1: power to weapons
             2: power to shields
             3: power to engines
             4: power to all
    """
    try:
        weapon_rgb = screen[weapon_cds[0]][weapon_cds[1]]
        engine_rgb = screen[shield_cds[0]][shield_cds[1]]
        shield_rgb = screen[engine_cds[0]][engine_cds[1]]
    except IndexError:
        return None
    weapon_power = list((value > 25) for value in weapon_rgb)
    engine_power = list((value > 25) for value in engine_rgb)
    shield_power = list((value > 25) for value in shield_rgb)
    if True in weapon_power:
        power_mgmt = 1
    elif True in engine_power:
        power_mgmt = 3
    elif True in shield_power:
        power_mgmt = 2
    else:
        power_mgmt = 4
    return power_mgmt


def get_ship_health_hull(image, coordinates):
    """
    Uses the PIL library to determine the color of the ship icon in the UI
    to make an approximation of the ship hull health.
    """
    x, y = coordinates
    image = image.crop((*coordinates, x + 20, y + 20))
    rgb = get_brightest_pixel(image)
    health = {
        "red": 25,
        "orange": 50,
        "yellow": 75,
        "green": 100
    }
    for name, pair in colors.items():
        if get_similarity_pixels(rgb, pair) >= 80:
            if name not in health:
                return None
            return health[name]
    return None


def get_ship_health_shields(image, coordinates):
    """
    Uses the PIL library to determine the color of the ship icon in the UI
    to make an approximation of the ship shield health.

    Two elements, each with their own color. Each color represents 10%
    Red, orange, yellow, green, bright green and blue when power to shields
    is enabled to make for total of 112.5% shield power.
    """
    elements = ["f1", "f2", "r1", "r2"]
    generator = zip(elements, coordinates)
    results = {key: None for key in elements}
    health = {
        "blue": 62.5,
        "green": 50.0,
        "yellow": 37.5,
        "orange": 25.0,
        "red": 12.5,
        "none": 0.0,
        None: 0.0
    }

    for element, coord in generator:
        rgb = image.getpixel(coord)
        for name, color in colors.items():
            if get_similarity_pixels(color, rgb) >= 80:
                results[element] = name
    return (health[results["f1"]] + health[results["f2"]],
            health[results["r1"]] + health[results["r2"]])
