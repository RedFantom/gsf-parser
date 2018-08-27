"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import colorsys
from datetime import datetime
from multiprocessing import Process, Pool
from time import sleep
from typing import List, Tuple
# Packages
import numpy as np
from PIL import Image
from pytesseract import image_to_string
# Project Modules
from parsing import gui
from parsing.tesseract import is_installed as is_tesseract_installed
from utils.colors import color_hex_to_tuple

Color = Tuple[int, int, int]


class ChatParser(Process):
    """Parser that runs in a separate Process to read chat messages"""

    def __init__(self, player: str, server: str, conn):
        """Initialize process and retrieve required data"""
        if not is_tesseract_installed():
            raise RuntimeError("Tesseract is not installed")

        Process.__init__(self)

        self.conn = conn
        config = gui.get_player_config(player, server)["Settings"]
        self.colors = self.convert_colors(config["ChatColors"])
        ui = gui.GUIParser(config["GUI_Current_Profile"], {"ChatPanel_1": (None, None)})
        self.box = ui.get_box_coordinates("ChatPanel_1")

    def run(self):
        """Run the message reading loop"""
        print("[ChatParser] Started")
        # screenshotter = mss()
        # screenshot = screenshotter.grab(self.box)
        # image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        image = Image.open("before.png")
        results = self.parse_messages(image, self.colors)
        print("[ChatParser] Results: {}".format(results))
        self.conn.send(results)
        sleep(5)
        print("[ChatParser] Stopped")

    @staticmethod
    def compare_colors(color: Color, colors: List[Color]) -> bool:
        """Compare color to colors in HSV format"""
        for template in colors:
            if sum(abs(v1 - v2) for v1, v2 in zip(color, template)) < 60:
                return True
        return False

    @staticmethod
    def rgb_to_hsv(color: Color) -> Color:
        """Convert a color to the HSV color space"""
        h, s, v = colorsys.rgb_to_hsv(*color)
        h, s = map(lambda v: int(v * 255), (h, s))
        return h, s, v

    @staticmethod
    def convert_colors(colors: str) -> List[Color]:
        """Convert the colors in a colors list to a colors list"""
        colors: List[str] = [c.strip() for c in colors.split(";") if c.strip() != ""]
        return list(map(lambda k: color_hex_to_tuple("#" + k), colors))

    def prepare_image(self, image: Image.Image, colors: list) -> Image.Image:
        """Prepare an image by filtering its text"""
        self.conn.send("Processing colors...")
        colors: List[Color] = list(set(map(ChatParser.rgb_to_hsv, colors)))
        pixels = np.array(image)
        new = Image.new("L", (image.width, image.height), color=255)
        new_pixels = np.array(new)
        img_colors = image.getcolors(image.width * image.height)
        cmp_colors = list()
        for count, color in img_colors:
            color = ChatParser.rgb_to_hsv(color)
            if count > 1 and ChatParser.compare_colors(color, colors):
                cmp_colors.append(color)
        for y in range(image.height):
            self.conn.send("Pre-processing image... {:.1f}%".format(((y + 1) / image.height) * 100))
            for x in range(image.width):
                color = ChatParser.rgb_to_hsv(pixels[y, x])
                if ChatParser.compare_colors(color, cmp_colors):
                    new_pixels[y, x] = 0
        return Image.fromarray(new_pixels, "L")

    def perform_ocr(self, image: Image.Image, colors: List[Color]) -> str:
        """Perform OCR on an image"""
        image.save("before.png")
        image = self.prepare_image(image, colors)
        image.save("after.png")
        self.conn.send("Performing OCR...")
        return image_to_string(image)

    def parse_messages(self, image: Image.Image, colors: List[Color]) -> List[tuple]:
        """Return a list of individual messages given an image"""
        string = self.perform_ocr(image, colors)
        self.conn.send("Parsing OCR results...")
        return [(datetime.now(), "", "", string)]
