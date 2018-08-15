"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
from typing import Tuple, Dict, List
import xml.etree.cElementTree as et
# UI Libraries
from tkinter import messagebox
# Project Modules
from utils.utilities import get_screen_resolution
from utils.directories import get_assets_directory
from utils.swtor import get_swtor_directory
from data.servers import server_ini


def get_gui_profiles() -> List[str]:
    """Return a list of all GUI Profile Names in the SWTOR directory"""
    return [
        item.replace(".xml", "") for item in
        os.listdir(os.path.join(get_swtor_directory(), "swtor", "settings", "GUIProfiles"))
    ]


def get_player_guiname(player_name: str, server: str) -> str:
    """
    Returns the GUI Profile name for a certain player name. Does not
    work if there are multiple characters with the same name on the same
    account used on the same computer and also doesn't work if the name
    is misspelled. Credit for finding this reference to the GUI state
    files in the SWTOR settings files goes to Ion.
    :param player_name: Name of this character
    :param server: Server code for this character (DM, TL, etc.)
    :return: GUI profile name, not XML file
    """
    if not isinstance(player_name, str):
        raise ValueError("player_name is not of str type: {0}".format(player_name))
    if player_name == "":
        raise ValueError("player_name is an empty str")
    dir = os.path.join(get_swtor_directory(), "swtor", "settings")
    if not os.path.exists(dir):
        messagebox.showerror("Error", "SWTOR settings path not found. Is SWTOR correctly installed?")
        raise ValueError("SWTOR settings path not found")
    correct_file = None
    if server is None:
        for file_name in os.listdir(dir):
            if not file_name.endswith(".ini"):
                continue
            elif player_name in file_name:
                correct_file = file_name
                break
    else:
        correct_file = "{}_{}_PlayerGUIState.ini".format(server_ini[server], player_name)
    if not correct_file:
        raise ValueError("Could not find a player settings file with name: {0}".format(player_name))
    with open(os.path.join(dir, correct_file)) as settings_file:
        lines = settings_file.readlines()
    gui_profile = None
    for line in lines:
        elements = line.split("=")
        if elements[0] == "GUI_Current_Profile ":
            gui_profile = str(elements[1])
            break
    if not gui_profile:
        raise ValueError("Could not find GUI_Current_Profile in settings file {0}".format(correct_file))
    if "preferences" in gui_profile:
        return "Default"
    return gui_profile[1:].replace("\n", "")


class GUIParser(object):
    """
    Parses an SWTOR GUI profile by first reading the file into an
    ElementTree and then allowing the user to retrieve data values from
    the profile by providing tuples or directly calculating coordinates
    the user needs. Example piece
    of GSF GUI profile section:
    <FreeFlightPlayerStatusEffects>
        <anchorAlignment Type="3" Value="2.000000" />
        <anchorXOffset Type="3" Value="25.000000" />
        <anchorYOffset Type="3" Value="-200.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightPlayerStatusEffects>
    All GSF GUI elements provide the attributes anchorAlignment,
    anchorXOffset, anchorYOffset, scale, enabled and alpha. The amount
    of GSF GUI elements is, luckily, quite limited, a list of items is
    available in the class' __init__ function.

    The alignment of the GUI element works as follows:
    - The anchorXOffset and anchorYOffset are in pixels
    - The offsets are counted from one out of nine points on the screen,
    to the same respective point on the GUI element
    - The points are these:
             X    Y
      * 1: Left top
      * 2: Left bottom
      * 3: Left center
      * 4: Right top
      * 5: Right bottom
      * 6: Right center
      * 7: Center top
      * 8: Center bottom
      * 9: Center center

    So, if the anchorXOffset is 50, the anchorYOffset is 0 and the
    anchor is 8, then the bottom center of the GUI element is 50 pixels
    to the right from the bottom center of the screen.

    All the credit for this incredibly useful information goes to Ion,
    who has written a SWTOR UI layout generator that you can find here:
    https://github.com/ion1/swtor-ui

    Important Note: Not all GUI elements in the SWTOR XML files have
    the same capitalization in their elements. Such as the different
    variants AnchorXOffset, anchorXOffset and even anchorOffsetX! Please
    check what format your option uses before using it in this class.
    """

    debug = True

    def __init__(self, file_name: str, target_items: dict):
        """
        Initializes the class by reading the XML file and setting things
        up for access by the user
        :param file_name: a GUI profile file_name, either an absolute
                          path or a plain file_name
        :param target_items: Dictionary with GUI elements as keys and
                             size tuples as values
        """
        target_items.update({"Global": (0, 0)})
        file_name = os.path.basename(file_name)
        if ".xml" not in file_name:
            file_name += ".xml"
        if "Default.xml" in file_name or file_name == "default":
            file_name = os.path.join(get_assets_directory(), "vision", "Default_Interface.xml")
        if not os.path.exists(file_name):
            file_name = os.path.join(get_swtor_directory(), "swtor", "settings", "GUIProfiles", file_name)
        if not os.path.exists(file_name):
            raise FileNotFoundError("file_name specified is not valid: {0}".format(file_name))
        self.file_name = file_name
        self.tree = et.parse(file_name)
        self.root = self.tree.getroot()
        self.gui_elements = {}
        self.target_items = [item for item in target_items]
        self.target_sizes = target_items
        for item in self.target_items:
            self.gui_elements[item] = self.root.find(item)
            if not self.gui_elements[item]:
                raise ValueError("Could not find {0} in GUI profile".format(item))
        resolution = get_screen_resolution()
        self.anchor_dictionary = self.get_anchor_dictionary(resolution)

    @property
    def global_scale(self) -> float:
        """Return the Global UI Scale"""
        obj = self.get_element_object("Global")
        return self.get_item_value(obj, "GlobalScale")

    def __getitem__(self, key: Tuple[et.Element, et.Element, str]) -> str:
        """
        Returns the requested data to the user
        :param key: (element, item, attribute)
        :return: value in str type
        """
        if not isinstance(key, tuple):
            raise ValueError("key requested not a tuple: {0}".format(key))
        if not len(key) is 3:
            raise ValueError("key requested not with len 3: {0}".format(key))
        return self.gui_elements[key[0]].find(key[1]).get(key[2])

    def __setitem__(self, key, value):
        raise ValueError("Manipulating GUI profiles is not supported")

    @staticmethod
    def get_anchor_dictionary(resolution: Tuple[int, int]) -> Dict[int, Tuple[int, int]]:
        """
        Get a dictionary of the absolute pixel points for each of the
        nine anchor points in the docstring of this class
        by performing the required calculations.
        :param resolution: (width, height) tuple
        :return: anchor_point dict
        """
        x_left = 0
        x_center = int(round(resolution[0] / 2, 0)) - 5
        x_right = resolution[0] - 5
        y_top = 0
        y_center = int(round(resolution[1] / 2, 0))
        y_bottom = resolution[1]
        anchor_points = {
            1: (x_left, y_top),
            2: (x_left, y_bottom),
            3: (x_left, y_center),
            4: (x_right, y_top),
            5: (x_right, y_bottom),
            6: (x_right, y_center),
            7: (x_center, y_top),
            8: (x_center, y_bottom),
            9: (x_center, y_center)
        }
        return anchor_points

    @staticmethod
    def get_element_absolute_coordinates(
            anchor_points: Dict[int, Tuple[int, int]], anchor: int, x_offset: int, y_offset: int) -> Tuple[int, int]:
        """Get absolute screen pixel coordinates for an element by name"""
        return anchor_points[anchor][0] + x_offset, anchor_points[anchor][1] + y_offset

    @staticmethod
    def get_item_value(element: et.Element, name: str) -> int:
        """Get an int value from an element"""
        return int(round(float(element.find(name).get("Value")), 0))

    def get_element_scale(self, element: et.Element):
        """
        As the scale is a float value, not an int, the normal class
        method can't be used for this item
        :param element: element object
        :return: float
        """
        return round(float(element.find("scale").get("Value")), 3) * self.global_scale

    @staticmethod
    def get_scale_corrected_value(value: int, scale: float) -> int:
        """Correct a value for a float scale value"""
        return int(round(value * scale, 0))

    def get_essential_element_values(self, element: et.Element):
        """Get the essential element values for a GSF GUI element"""
        x_offset = self.get_item_value(element, "anchorXOffset")
        y_offset = self.get_item_value(element, "anchorYOffset")
        alpha = self.get_item_value(element, "anchorAlignment")
        return x_offset, y_offset, alpha

    def get_element_object(self, element_name: str) -> et.Element:
        """
        Check the element name passed as argument and return an
        appropriate element object
        :param element_name: str name
        :return: element object
        """
        if element_name not in self.gui_elements:
            raise KeyError(
                "element requested that was not in target_items initializer argument: {0}".format(element_name))
        return self.gui_elements[element_name]

    def get_element_anchor(self, element: et.Element) -> int:
        """Get the element anchor number"""
        return self.get_item_value(element, "anchorAlignment")

    def get_box_coordinates(self, element_name: str) -> Tuple[int, int, int, int]:
        """Get a tuple with the box coordinates for an element"""
        element = self.get_element_object(element_name)
        print("[GUI] Getting data for element: {0}".format(element_name))
        x_offset, y_offset, alpha = self.get_essential_element_values(element)
        scale = self.get_element_scale(element)
        anchor = self.get_element_anchor(element)
        print("[GUI] element_name, x_offset, y_offset, alpha, scale, anchor: {0}, {1}, {2}, {3}, {4}, {5}".format(
            element_name, x_offset, y_offset, alpha, scale, anchor))

        if anchor is 1:
            # Anchor left top
            x_one = self.anchor_dictionary[anchor][0] + x_offset
            y_one = self.anchor_dictionary[anchor][1] + y_offset
        elif anchor is 2:
            # Anchor left bottom
            x_one = self.anchor_dictionary[anchor][0] + x_offset
            y_one = self.anchor_dictionary[anchor][1] + y_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][1], scale)
        elif anchor is 3:
            # Anchor left center
            x_one = self.anchor_dictionary[anchor][0] + x_offset
            y_one = self.anchor_dictionary[anchor][1] + y_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][1] * .5, scale)
        elif anchor is 4:
            # Anchor right top
            x_one = self.anchor_dictionary[anchor][0] + x_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][0], scale)
            y_one = self.anchor_dictionary[anchor][1] + y_offset
        elif anchor is 5:
            # Anchor right bottom
            x_one = self.anchor_dictionary[anchor][0] + x_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][0], scale)
            y_one = self.anchor_dictionary[anchor][1] + y_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][1], scale)
        elif anchor is 6:
            # Anchor right center
            x_one = self.anchor_dictionary[anchor][0] + x_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][0], scale)
            y_one = self.anchor_dictionary[anchor][1] + y_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][1] * 0.5, scale)
        elif anchor is 7:
            # Anchor center top
            x_one = self.anchor_dictionary[anchor][0] + x_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][0] * 0.5, scale)
            y_one = self.anchor_dictionary[anchor][1] + y_offset
        elif anchor is 8:
            # Anchor center bottom
            x_one = self.anchor_dictionary[anchor][0] + x_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][0] * 0.5, scale)
            y_one = self.anchor_dictionary[anchor][1] + y_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][1], scale)
        elif anchor is 9:
            # Anchor center center
            x_one = self.anchor_dictionary[anchor][0] + x_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][0] * 0.5, scale)
            y_one = self.anchor_dictionary[anchor][1] + y_offset - self.get_scale_corrected_value(
                self.target_sizes[element_name][1] * 0.5, scale)
        else:
            raise ValueError("Invalid anchor value found: {0}".format(anchor))
        x_two = x_one + self.get_scale_corrected_value(self.target_sizes[element_name][0], scale)
        y_two = y_one + self.get_scale_corrected_value(self.target_sizes[element_name][1], scale)
        return x_one, y_one, x_two, y_two
