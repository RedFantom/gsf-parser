"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
import math
import operator
# Packages
from PIL import Image
import numpy
import cv2 as opencv
# Project Modules
from data.maps import map_dictionary
from utils.directories import get_assets_directory, get_temp_directory
from parsing.imageops import \
    get_similarity, get_similarity_pixels, \
    get_brightest_pixel, get_brightest_pixel_loc

colors = {
    "blue": (2, 95, 133),
    "green": (0, 166, 0),
    "yellow": (132, 157, 0),
    "orange": (165, 94, 0),
    "red": (164, 1, 1),
    "none": (0, 0, 0)
}

timer_boxes = {
    (1920, 1080): (1466, 835, 1536, 875),
}

MIN_MATCHES = 30


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


def get_distance_from_center(coordinates=(960, 540), resolution=(1920, 1080)):
    """
    Calculates the distance in pixels of the middle of the screen to the middle
    of the targeting pointer
    :param coordinates: coordinates of the **middle** of the targeting pointer
    :param resolution: tuple of resolution
    :return: distance in pixels from center
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
    """
    return max(round(min(degrees, firing_arc) * tracking_penalty - upgrade_c, 1), 0)


def get_timer_status(source, treshold=15.0):
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
        if similarity < treshold:
            image_similarity[img.replace(".jpg", "")] = similarity
    if len(image_similarity) == 0:
        return None
    return int(min(image_similarity.items(), key=operator.itemgetter(1))[0])


def get_ship_health_hull(image):
    """
    Uses the PIL library to determine the color of the ship icon in the
    UI to make an approximation of the ship hull health.
    """
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
    Uses the PIL library to determine the color of the ship icon in the
    UI to make an approximation of the ship shield health.

    Two elements, each with their own color. Each color represents 10%
    Red, orange, yellow, green, bright green and blue when power to
    shields is enabled to make for total of 112.5% shield power.
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
                break
    return (health[results["f1"]] + health[results["f2"]],
            health[results["r1"]] + health[results["r2"]])


def get_minimap_location(minimap: Image.Image):
    """
    Determine the location of a ship on the given (cropped-screenshot)
    minimap image. Uses pixel matching to determine the brightest green
    spot in the minimap image.
    """
    result = get_brightest_pixel_loc(minimap, 1)
    if result is None:
        return None, None
    x, y = result
    width, height = minimap.size
    return x / width, y / height


def image_to_opencv(image: Image.Image):
    """Convert a PIL image into a cv2 compatible array"""
    return numpy.array(image)[:, :, ::-1].copy()


def get_map(image: Image.Image):
    """Use feature matching to determine match and map type"""
    path = os.path.join(get_temp_directory(), "temp.png")
    map_directory = os.path.join(get_assets_directory(), "maps")
    image.save(path)
    image = opencv.imread(path, 0)
    orb = opencv.ORB_create()
    image_kp, image_ds = orb.detectAndCompute(image, None)
    map_results = dict()
    bf = opencv.BFMatcher(opencv.NORM_L1, crossCheck=False)
    for match_type, maps in map_dictionary.items():
        for map, file_name in maps.items():
            file_name = "{}_{}".format(match_type, file_name + ".jpg")
            path = os.path.join(map_directory, file_name)
            Image.open(path).resize((200, 200), Image.ANTIALIAS).save(os.path.join(get_temp_directory(), file_name))
            template = opencv.imread(os.path.join(get_temp_directory(), file_name), 0)
            template_kp, template_ds = orb.detectAndCompute(template, None)
            matches = bf.knnMatch(image_ds, template_ds, k=2)
            good = list()
            for m, n in matches:
                if m.distance < 0.8 * n.distance:
                    good.append(m)
            map_results[(match_type, map)] = len(good)
    map = max(map_results, key=lambda key: map_results[key])
    if map_results[map] < MIN_MATCHES:
        return None
    return map


def get_score(image: Image.Image):
    """
    Implementation:

    1. Crop the image
    2. (Optional) Use template matching to detect score card
       Whether this is required highly depends on the accuracy of the
       coordinates. If the coordinates are not accurate, it is
       impossible to determine the actual score based on the fill
       ratio of the coloured score bars.
    3. Use brightest pixel detection to get score location
    4. Compute the ratio filled of the score bars
    5. Compute the score
    6. Detect the presence of satellite markers
    7. Calculate the score from ratio and match type

    If the length of the coloured bar cannot be determined, then it
    must be assumed that one of the bars is full, and thus has gained
    full points. The ratio can then be determined with the other bar,
    moving in the left direction only horizontally, continuing for as
    long as the pixels are coloured and not black.
    """
    image.save("temp.png")
    red, green = get_brightest_pixel_loc(image, 0), get_brightest_pixel_loc(image, 1)
    rc, gc = image.getpixel(red), image.getpixel(green)
    print("[Vision.get_score] Coordinates: {} (red), {} (green)".format(red, green))
    print("[Vision.get_score] Colors: {} (red), {} (green)".format(rc, gc))
    # Assume one of the bars is full
    xr, xg = red[0], green[0]

