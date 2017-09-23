# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import os
import math
import win32api
import cv2
from PIL import Image
import numpy
from tools.utilities import write_debug_log, get_assets_directory
from parsing.imgcompare import get_similarity
import pytesseract
import operator


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


def get_tracking_penalty(degrees, tracking_penalty, upgrade_c=0):
    """
    :param degrees: The amount of degrees for tracking penalty
    :param tracking_penalty: The tracking penalty in %/degree
    :param upgrade_c: The upgrade constant
    :return:
    """
    return round(degrees * tracking_penalty - upgrade_c, 1)


def get_timer_status(source):
    """
    Determines the state of the spawn countdown timer by performing
    template matching on the cv2 array of a screenshot to find a match
    for one of the timers in the folder.    :param screen: A cv2 array of the screenshot
    :return: An int of how many seconds are left
    """
    folder = os.path.join(get_assets_directory(), "timers")
    image_similarity = {}
    for img in os.listdir(folder):
        if not img.endswith(".jpg"):
            continue
        image_path = os.path.join(folder, img)
        image = Image.open(image_path)
        similarity =get_similarity(source, image)
        image_similarity[img.replace(".jpg", "")] = similarity
    return int(min(image_similarity.items(), key=operator.itemgetter(1))[0])


def get_enemy_brackets(screen):
    """
    Determines the amount and places of the red brackets of the enemies on
    the screen using template matching, at the default size.
    :param screen: cv2 array of screenshot
    :return: list of (x, y) tuples
    """
    pass


def perform_ocr(pil_screen, coordinates):
    """
    Perform OCR on a screenshot to determine the ship type of the enemy player
    currently targeted by the user.
    :param pil_screen: PIL Image
    :param coordinates: (x, y, x, y) box tuple
    :return: string of ship type
    """
    pil_screen.crop(coordinates, Image.ANTIALIAS)
    return pytesseract.image_to_string(pil_screen)


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
    power_mgmt = 4
    try:
        weapon_rgb = screen[weapon_cds[0]][weapon_cds[1]]
        engine_rgb = screen[shield_cds[0]][shield_cds[1]]
        shield_rgb = screen[engine_cds[0]][engine_cds[1]]
    except IndexError:
        return None
    weapon_power = list((value > 50) for value in weapon_rgb)
    engine_power = list((value > 50) for value in engine_rgb)
    shield_power = list((value > 50) for value in shield_rgb)
    if True in weapon_power:
        power_mgmt = 1
    if True in engine_power:
        if power_mgmt != 4:
            pass
        power_mgmt = 3
    if True in shield_power:
        if power_mgmt != 4:
            pass
        power_mgmt = 2
    return power_mgmt


def get_ship_health_hull(screen):
    """
    Uses the PIL library to determine the color of the ship icon in the UI
    to make an approximation of the ship hull health.

    Red:            01%-20%
    Orange:         21%-40%
    Yellow:         41%-60%
    Green:          61%-80%
    Bright green:   81%-100%

    :param screen: cv2 array of screenshot or pillow object
    :return: int with percentage
    """
    pass


def get_ship_health_shields(image, cds):
    """
    Uses the PIL library to determine the color of the ship icon in the UI
    to make an approximation of the ship shield health.

    Two elements, each with their own color. Each color represents 10%
    Red, orange, yellow, green, bright green and blue when power to shields
    is enabled to make for total of 110% shield power.

    :param screen: cv2 array of screenshot or pillow object
    :return: int with percentage
    """
    front_one, front_two, back_one, back_two = cds

    colors = {
        "blue": (2, 95, 133),
        "green": (0, 166, 0),
        "yellow": (132, 157, 0),
        "orange": (165, 94, 0),
        "red": (164, 1, 1),
        "none": (0, 0, 0)
    }
    colors_health = {
        "blue": 62.5,
        "green": 50.0,
        "yellow": 37.5,
        "orange": 25.0,
        "red": 12.5,
        "none": 0.0
    }
    f_one_rgb = image.getpixel((front_one[0], front_one[1]))
    f_two_rgb = image.getpixel((front_two[0], front_two[1]))
    b_one_rgb = image.getpixel((back_one[0], back_one[1]))
    b_two_rgb = image.getpixel((back_two[0], back_two[1]))
    shields_rgb = (f_one_rgb, f_two_rgb, b_one_rgb, b_two_rgb)
    color_shields = []

    for shield_index, rgb_code in enumerate(shields_rgb):
        for color_name, color_rgb_tuple in colors.items():
            valid = True
            for index, color in enumerate(color_rgb_tuple):
                if not color - 25 <= rgb_code[index] <= color + 25:
                    valid = False
                    break
            if valid is True:
                color_shields.append(color_name)
                break

    f = colors_health[color_shields[0]] + colors_health[color_shields[1]]
    b = colors_health[color_shields[2]] + colors_health[color_shields[3]]
    return f, b


def get_leftbutton_pressed():
    """
    Wrapper around win32api.GetKeyState for left button state
    :return: boolean, True when pressed
    """
    if win32api.GetKeyState(0x01) >= 0:
        return True
    else:
        return False


def get_rightbutton_pressed():
    """
    Wrapper around win32api.GetKeyState for right button state
    :return: boolean, True when pressed
    """
    if win32api.GetKeyState(0x02) >= 0:
        return True
    else:
        return False
