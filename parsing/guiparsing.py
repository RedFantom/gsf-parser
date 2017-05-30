# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from tools.utilities import get_swtor_directory
import xml.etree.cElementTree as ET
import os


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
    element is 50 pixels to the left from the bottom center of the screen

    All the credit for this incredibly useful information goes to Ion, who has written a SWTOR UI layout generator
    that you can find here: https://github.com/ion1/swtor-ui
    """

    def __init__(self, file_name):
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
        self.target_items = [
            "FreeFlightQuickBar", "FreeFlightShipStatus", "FreeFlightPlayerStatusEffects",
            "FreeFlightTargetStatusEffects", "FreeFlightShipAmmo", "FreeFlightTargetingComputer",
            "FreeFlightPowerSettings", "FreeFlightMissileLockIndicator", "FreeFlightMiniMap",
            "FreeFlightScorecard", "FreeFlightCopilotBark"
        ]
        for item in self.target_items:
            try:
                self.gui_elements[item.replace("FreeFlight", "")] = self.root.find(item)
            except IndexError:
                raise ValueError("Could not find {0} in GUI profile".format(item))
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

    def get_player_health_coordinates(self):
        pass

    def get_enemy_health_coordinates(self):
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
