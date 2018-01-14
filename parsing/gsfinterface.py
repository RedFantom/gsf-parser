"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from tkinter import messagebox
from parsing.guiparsing import GUIParser


class GSFInterface(GUIParser):
    def __init__(self, file_name, target_items=None):
        if target_items is None:
            target_items = {
                "FreeFlightQuickBar": (230, 70),
                "FreeFlightShipStatus": (190, 180),
                "FreeFlightPlayerStatusEffects": (245, 50),
                "FreeFlightTargetStatusEffects": (280, 50),
                "FreeFlightShipAmmo": (170, 90),
                "FreeFlightTargetingComputer": (345, 260),
                "FreeFlightPowerSettings": (80, 180),
                "FreeFlightMissileLockIndicator": (90, 80),
                "FreeFlightMiniMap": (325, 245),
                "FreeFlightScorecard": (420, 120),
                "FreeFlightCopilotBark": (245, 90),
                "Global": (0, 0)
            }
        GUIParser.__init__(self, file_name, target_items)

    def get_element_coordinates(self, element_name):
        """
        Get element screen coordinates
        :param element_name: str name
        :return: (x, y)
        """
        element = self.get_element_object(element_name)
        x_offset, y_offset, alpha = self.get_essential_element_values(element)
        anchor = self.get_element_anchor(element)
        if alpha is not 0:
            messagebox.showerror("Error", "The GSF Parser cannot work with GUI profiles for GSF that have an opacity "
                                          "level higher than 0. Please adjust your GUI profile.")
            raise ValueError("opacity for element {0} is higher than zero".format(element_name))
        return self.get_element_absolute_coordinates(self.anchor_dictionary, anchor, x_offset, y_offset)

    def get_ship_health_coordinates(self):
        temp_cds = self.get_box_coordinates("FreeFlightShipStatus")
        temp_scale = self.get_element_scale(self.get_element_object("FreeFlightShipStatus"))
        front_one = (temp_cds[0] + int(25 * temp_scale), temp_cds[1] + int(70 * temp_scale))
        front_two = (temp_cds[0] + int(40 * temp_scale), temp_cds[1] + int(70 * temp_scale))
        back_one = temp_cds[0] + int(25 * temp_scale), temp_cds[1] + int(120 * temp_scale)
        back_two = temp_cds[0] + int(40 * temp_scale), temp_cds[1] + int(120 * temp_scale)
        return front_one, front_two, back_one, back_two

    def get_ship_buffs_coordinates(self):
        return self.get_box_coordinates("FreeFlightPlayerStatusEffects")

    def get_target_name_coordinates(self):
        temp_cds = self.get_box_coordinates("FreeFlightTargetingComputer")
        try:
            temp_scale = self.get_element_scale("FreeFlightTargetingComputer")
        except AttributeError:
            # TODO: Figure this out
            temp_scale = 1.0
        x_one = temp_cds[0] + int(95 * temp_scale)
        y_one = temp_cds[1] + int(14 * temp_scale)
        x_two = temp_cds[0] + int(305 * temp_scale)
        y_two = temp_cds[1] + int(28 * temp_scale)
        return x_one, y_one, x_two, y_two

    def get_target_shiptype_coordinates(self):
        temp_cds = self.get_box_coordinates("FreeFlightTargetingComputer")
        try:
            temp_scale = self.get_element_scale("FreeFlightTargetingComputer")
        except AttributeError:
            # TODO: Figure this out
            temp_scale = 1.0
        x_one = temp_cds[0] + int(80 * temp_scale)
        y_one = temp_cds[1] + int(165 * temp_scale)
        x_two = temp_cds[0] + int(220 * temp_scale)
        y_two = temp_cds[1] + int(175 * temp_scale)
        return x_one, y_one, x_two, y_two

    def get_target_distance_coordinates(self):
        temp_cds = self.get_box_coordinates("FreeFlightTargetingComputer")
        try:
            temp_scale = self.get_element_scale("FreeFlightTargetingComputer")
        except AttributeError:
            # TODO: Figure this out
            temp_scale = 1.0
        x_one = temp_cds[0] + int(120 * temp_scale)
        y_one = temp_cds[1] + int(183 * temp_scale)
        x_two = temp_cds[0] + int(185 * temp_scale)
        y_two = temp_cds[1] + int(193 * temp_scale)
        return x_one, y_one, x_two, y_two

    def get_target_buffs_coordinates(self):
        return self.get_box_coordinates("FreeFlightTargetStatusEffects")

    def get_pixels_per_degree(self):
        obj = self.get_element_object("Global")
        return self.get_item_value(obj, "GlobalScale") * 10

    def get_secondary_icon_coordinates(self):
        # (95, 16)
        box = self.get_box_coordinates("FreeFlightShipAmmo")
        scale = self.get_element_scale(self.get_element_object("FreeFlightShipAmmo"))
        x = box[0] + int(95 * scale)
        y = box[1] + int(16 * scale)
        return x, y
