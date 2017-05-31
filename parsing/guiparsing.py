# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from tools.utilities import get_swtor_directory, get_screen_resolution
import xml.etree.cElementTree as ET
import os
from configparser import ConfigParser
from tkinter import messagebox


def get_gui_profiles():
    """
    Returns a list of all GUI profiles available in the SWTOR directory
    :return: list
    """
    dir = get_swtor_directory()
    return [item.replace(".xml", "") for item in os.listdir(dir)]


def get_player_guiname(player_name):
    """
    Returns the GUI Profile name for a certain player name. Does not work if there are multiple characters with the same
    name on the same account used on the same computer and also doesn't work if the name is misspelled. Credit for
    finding this reference to the GUI state files in the SWTOR settings files goes to Ion.
    :param player_name: name of the player
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
    configparser = ConfigParser()
    correct_file = None
    for file_name in os.listdir(dir):
        if not file_name.endswith(".ini"):
            continue
        elif player_name in file_name:
            correct_file = file_name
            break
    if not correct_file:
        raise ValueError("Could not find a player settings file with name: {0}".format(player_name))
    configparser.read(os.path.join(dir, correct_file))
    return configparser.get("settings", "GUI_Current_Profile")


class GUIParser(object):
    """
    Parses an SWTOR GUI profile by first reading the file into an ElementTree and then allowing the user to retrieve
    data values from the profile by providing tuples or directly calculating coordinates the user needs. Example piece
    of GSF GUI profile section:
    <FreeFlightPlayerStatusEffects>
        <anchorAlignment Type="3" Value="2.000000" />
        <anchorXOffset Type="3" Value="25.000000" />
        <anchorYOffset Type="3" Value="-200.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightPlayerStatusEffects>
    All GSF GUI elements provide the attributes anchorAlignment, anchorXOffset, anchorYOffset, scale, enabled and alpha
    The amount of GSF GUI elements is, luckily, quite limited, a list of items is available in the class' __init__
    function.

    The alignment of the GUI element works as follows:
    - The anchorXOffset and anchorYOffset are in pixels
    - The offsets are counted from one out of nine points on the screen, to the same respective point on the GUI element
    - The points are these:
             X    Y
      * 1: Left center
      * 2: Left bottom
      * 3: Left center
      * 4: Right top
      * 5: Right bottom
      * 6: Right center
      * 7: Center top
      * 8: Center bottom
      * 9: Center center

    So, if the anchorXOffset is 50, the anchorYOffset is 0 and the anchor is 8, then the bottom center of the GUI
    element is 50 pixels to the right from the bottom center of the screen

    All the credit for this incredibly useful information goes to Ion, who has written a SWTOR UI layout generator
    that you can find here: https://github.com/ion1/swtor-ui

    Important Note: Not all GUI elements in the SWTOR XML files have the same capitalization in their elements. Such as
    the different variants AnchorXOffset, anchorXOffset and even anchorOffsetX! Please check what forrmat your option
    uses before using it in this class.
    """

    def __init__(self, file_name,
                 target_items=("FreeFlightQuickBar", "FreeFlightShipStatus", "FreeFlightPlayerStatusEffects",
                               "FreeFlightTargetStatusEffects", "FreeFlightShipAmmo", "FreeFlightTargetingComputer",
                               "FreeFlightPowerSettings", "FreeFlightMissileLockIndicator", "FreeFlightMiniMap",
                               "FreeFlightScorecard", "FreeFlightCopilotBark")):
        """
        Initializes the class by reading the XML file and setting things up for access by the user
        :param file_name: a GUI profile file_name, either an absolute path or a plain file_name
        """
        file_name = os.path.basename(file_name)
        if ".xml" not in file_name:
            file_name += ".xml"
        if not os.path.exists(file_name):
            file_name = os.path.join(get_swtor_directory(), "swtor", "settings", "GUIProfiles", file_name)
        if not os.path.exists(file_name):
            raise ValueError("file_name specified is not valid: {0}".format(file_name))
        self.file_name = file_name
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        self.gui_elements = {}
        self.target_items = [item for item in target_items]
        for item in self.target_items:
            item_name = item.replace("FreeFlight", "")
            self.gui_elements[item_name] = self.root.find(item)
            if not self.gui_elements[item_name]:
                raise ValueError("Could not find {0} in GUI profile".format(item))
        resolution = get_screen_resolution()
        self.anchor_dictionary = self.get_anchor_dictionary(resolution)
        return

    def __getitem__(self, key):
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
    def get_anchor_dictionary(resolution):
        """
        Get a dictionary of the absolute pixel points for each of the nine anchor points in the docstring of this class
        by performing the required calculations.
        :param resolution: (width, height) tuple
        :return: anchor_point dict
        """
        x_left = 0
        x_center = int(round(resolution[0] / 2, 0))
        x_right = resolution[0]
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
    def get_element_absolute_coordinates(anchor_points, anchor, x_offset, y_offset):
        """
        Get absolute screen pixel coordinates for an element by name
        :param anchor_points: dictionary anchor_points
        :param anchor: anchor number (must be in anchor_points dict)
        :param x_offset: int offset
        :param y_offset: int offset
        :return: (x, y) tuple
        """
        return anchor_points[anchor][0] + x_offset, anchor_points[anchor][1] + y_offset

    @staticmethod
    def get_item_value(element, name):
        """
        Get an int value from an element
        :param element: XML parser element
        :param name: sub-element name
        :return: int value
        """
        return int(round(float(element.find(name).get("Value")), 0))

    def get_essential_element_values(self, element):
        """
        Get the essential element values for a GSF GUI element (for the position)
        :param element: XML parser element
        :return: anchor number, x_offset int, y_offset int, alpha percentage
        """
        anchor = self.get_item_value(element, "anchorAlignment")
        x_offset = self.get_item_value(element, "anchorXOffset")
        y_offset = self.get_item_value(element, "anchorYOffset")
        alpha = self.get_item_value(element, "anchorAlignment")
        return anchor, x_offset, y_offset, alpha

    def check_element_name(self, element_name):
        """
        Check the element name passed as argument and return an appropriate element object
        :param element_name: str name
        :return: element object
        """
        element_name = element_name.replace("FreeFlight", "")
        if element_name not in self.gui_elements:
            raise ValueError("element requested that was not in target_items initializer argument: {0}".
                             format(element_name))
        return self.gui_elements[element_name]

    def get_element_scale(self, element_name):
        """
        As the scale is a float value, not an int, the normal class method can't be used for this item
        :param element_name: str name
        :return: float
        """
        element = self.check_element_name(element_name)
        return round(float(element.find("scale").get("Value")), 3)

    def get_element_coordinates(self, element_name):
        """
        Get element screen coordinates
        :param element_name: str name
        :return: (x, y)
        """
        element = self.check_element_name(element_name)
        anchor, x_offset, y_offset, alpha = self.get_essential_element_values(element)
        if alpha is not 0:
            messagebox.showerror("Error", "The GSF Parser cannot work with GUI profiles for GSF that have an opacity "
                                          "level higher than 0. Please adjust your GUI profile.")
            raise ValueError("opacity for element {0} is higher than zero".format(element_name))
        return self.get_element_absolute_coordinates(self.anchor_dictionary, anchor, x_offset, y_offset)

    def get_player_health_coordinates(self):
        pass

    def get_enemy_health_coordinates(self):
        pass

    def get_player_powermgmt_coordinates(self):
        pass

    def get_element_offsets(self):
        pass

    def get_element_anchorpoint(self):
        pass

    def get_max_min_coordinates(self, output=False):
        """
        Originally for reverse engineering only
        :param output: if True prints results
        :return: (x_min, x_max, y_min, y_max), all float
        """
        x_values = []
        y_values = []
        for child in self.root:
            valid = False
            for item in child:
                if item.tag != "anchorXOffset":
                    continue
                else:
                    valid = True
                    break
            if not valid:
                continue
            x_values.append(float(child.find("anchorXOffset").get("Value")))
            y_values.append(float(child.find("anchorYOffset").get("Value")))
        if output:
            print("Minimum X Value: ", min(x_values), "\nMaximum X Value: ", max(x_values))
            print("Minimum Y Value: ", min(y_values), "\nMaximum Y Value: ", max(y_values))
        return min(x_values), max(x_values), min(y_values), max(y_values)


if __name__ == '__main__':
    """
    This code is for debugging purposes
    """
    GUIParser("Redfantom 1.xml").get_max_min_coordinates(output=True)
