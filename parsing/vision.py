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
import math
import win32gui
import win32api


def get_cv2_screen():
    """
    Gets a screenshot in cv2 format
    :return: cv2 screenshot array
    """
    screen_pil = ImageGrab.grab()
    return pillow_to_numpy(screen_pil)


def get_pointer_position_cv2(screen):
    """
    Gets the position of the targeting pointer on the screen
    :param screen: A cv2 array of a screenshot image
    :return: A tuple with the coordinates of the top left corner of the pointer
    """
    pointer = cv2.imread(os.getcwd() + "/assets/vision/pointer.png")
    results = cv2.matchTemplate(screen, pointer, cv2.TM_CCOEFF_NORMED)
    return numpy.unravel_index(results.argmax(), results.shape)


def get_pointer_position_win32():
    """
    Gets the position of the targeting pointer with win32gui
    :return: coordinates of pointer
    """
    return win32gui.GetCursorPos()


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


def get_tracking_degrees(distance, firingarc, pixelsperdegree=10):
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


def get_timer_status_cv2(screen):
    """
    Determines the state of the spawn countdown timer by performing
    template matching on the cv2 array of a screenshot to find a match
    for one of the timers in the folder.
    :param screen: A cv2 array of the screenshot
    :return: An int of how many seconds are left
    """
    folder = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/assets/timers"
    for img in os.listdir(folder):
        pass


def get_timer_status_ocr(screen):
    """
    Determines the state of the spawn countdown timer by performing
    OCR on the characters found in a certain section of the screen, that
    is found by performing template matching.
    :param screen: cv2 array of the screenshot
    :return:
    """
    if not isinstance(screen, Image):
        screen_pil = numpy_to_pillow(screen)
        screen_cv2 = screen
    else:
        screen_pil = screen
        screen_cv2 = pillow_to_numpy(screen)
    pass


def get_enemy_brackets(screen):
    """
    Determines the amount and places of the red brackets of the enemies on
    the screen using template matching, at the default size.
    :param screen: cv2 array of screenshot
    :return: list of (x, y) tuples
    """
    pass


def get_targeting_computer_pos(screen):
    """
    Determines the position of the targeting computer on the screen using
    template matching.
    :param screen: cv2 array of screenshot
    :return: (x, y) tuple
    """
    pass


def get_targeting_computer_shiptype(screen):
    """
    Perform OCR on a screenshot to determine the ship type of the enemy player
    currently targeted by the user.
    :param screen: cv2 array of screenshot
    :return: string of ship type
    """
    pass


def get_targeting_computer_targetname(screen):
    """
    Perform OCR on a screenshot to determine the name of the enemy player
    currently targeted by the user.
    :param screen: cv2 array of screenshot
    :return: string of player name
    """
    pass


def get_power_management(screen):
    """
    Uses template matching to determine how the user has divided the power
    among the different ship components.
    :param screen: cv2 array of screenshot
    :return: int 1, 2, 3, 4
             1: power to weapons
             2: power to shields
             3: power to engines
             4: power to all
    """
    image = cv2.imread(os.getcwd() + "/assets/vision/power_management.png")
    screen_pil = numpy_to_pillow(screen)
    results = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
    x, y = numpy.unravel_index(results.argmax(), results.shape)
    weapon_cds = (x + 10, y - 50)
    shield_cds = (x + 32, y - 50)
    engine_cds = (x + 54, y - 50)
    power_mgmt = 4
    weapon_rgb = screen_pil.getpixel(weapon_cds)
    engine_rgb = screen_pil.getpixel(engine_cds)
    shield_rgb = screen_pil.getpixel(shield_cds)
    weapon_power = list((value > 50) for value in weapon_rgb)
    engine_power = list((value > 50) for value in engine_rgb)
    shield_power = list((value > 50) for value in shield_rgb)
    if True in weapon_power:
        power_mgmt = 1
    if True in engine_power:
        if power_mgmt != 4:
            raise ValueError("Power management was already set.")
        power_mgmt = 3
    if True in shield_power:
        if power_mgmt != 4:
            raise ValueError("Power management was already set.")
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


def get_ship_health_forwardshields(screen):
    """
    Uses the PIL library to determine the color of the ship icon in the UI
    to make an approximation of the ship shield health.

    Two elements, each with their own color. Each color represents 10%
    Red, orange, yellow, green, bright green and blue when power to shields
    is enabled to make for total of 110% shield power.

    :param screen: cv2 array of screenshot or pillow object
    :return: int with percentage
    """
    pass


def get_ship_health_rearshields(screen):
    """
    Uses the PIL library to determine the color of the ship icon in the UI
    to make an approximation of the ship shield health.

    Two elements, each with their own color. Each color represents 10%
    Red, orange, yellow, green, bright green and blue when power to shields
    is enabled to make for total of 110% shield power.

    :param screen: cv2 array of screenshot or pillow object
    :return: int with percentage
    """
    pass


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
