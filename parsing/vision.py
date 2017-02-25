# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import cv2
from PIL import Image
try:
    from PIL import ImageGrab
except ImportError:
    import testing as ImageGrab
import os
import numpy
import time
import math


def get_pointer_position():
    """
    Gets the position of the targeting pointer on the screen
    :return: A tuple with the coordinates of the top left corner of the pointer
    """
    pointer = cv2.imread(os.getcwd() + "/assets/vision/pointer.png")
    screen_pil = ImageGrab.grab()
    screen = pillow_to_numpy(screen_pil)
    results = cv2.matchTemplate(screen, pointer, cv2.TM_CCOEFF_NORMED)
    # TODO: Validate results before returning
    return numpy.unravel_index(results.argmax(), results.shape)


def get_pointer_middle(coordinates, size=(44, 44)):
    """
    Get the coordinates of the middle of the pointer
    :param coordinates: The coordinates of the top left corner of the pointer
    :param size: The size of the pointer in pixels tuple (x, y)
    :return: A tuple with coordinates of the middle of the pointer
    """
    if size[0] % 2 == 1 or size[1] % 2 == 1 or size[0] != size[1]:
        raise ValueError("The pointer image is of an invalid size.")
    return (coordinates[0] + size[0] / 2, coordinates[1] + size[1] / 2)


def pillow_to_numpy(pillow):
    """
    :param pillow: Image file in Pillow format
    :return: Image file in OpenCV compatible numpy array format
    """
    imagefile = numpy.array(pillow)
    return imagefile[:, :, ::-1].copy()


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


def get_tracking_degrees(distance, firingarc, pixelsperdegree):
    """
    :param distance: Distance in pixels by get_distance_from_center
    :param firingarc: The firing arc of the weapon used
    :param pixelsperdegree: The pixels per firing degree (resolution dependent)
    :return: The amount of degrees for tracking penalty
    """
    return round(distance * pixelsperdegree / firingarc, 2)


def get_tracking_penalty(degrees, tracking_penalty, upgrade_c=0):
    """
    :param degrees: The amount of degrees for tracking penalty
    :param tracking_penalty: The tracking penalty in %/degree
    :param upgrade_c: The upgrade constant
    :return:
    """
    return round(degrees * tracking_penalty - upgrade_c, 1)
