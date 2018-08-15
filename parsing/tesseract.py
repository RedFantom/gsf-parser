"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from os import path
from subprocess import Popen, PIPE
# Packages
from PIL import Image, ImageFilter
from pytesseract import pytesseract as tesseract
# Project Modules
from utils.directories import get_temp_directory


START, END, DIFF = 650, 550, 20


def is_installed()->bool:
    """Determine whether Tesseract-OCR is installed in PATH"""
    cmd = tesseract.tesseract_cmd
    p = Popen([cmd, "--help"], stdout=PIPE)
    p.wait()
    out, err = p.communicate()
    return b"Usage" in out


def high_pass_invert(image: Image.Image, treshold: int)->Image.Image:
    """Perform a high-pass filter on an image and invert"""
    result = image.copy()  # Do not modify original image
    pixels = result.load()
    for x in range(image.width):
        for y in range(image.height):
            pixel = pixels[x, y]
            if sum(pixel) < treshold:
                pixels[x, y] = (255, 255, 255)
                continue
            pixels[x, y] = (0, 0, 0)
    return result


def perform_ocr(image: Image.Image, is_number: bool = False) -> (None, str, int):
    """Perform OCR on an Image"""
    if not is_installed():
        print("[Tesseract] Critical error: Tesseract is not installed!")
        return None
    result = None
    for threshold in range(START, END, -DIFF):
        template: Image.Image = high_pass_invert(image, threshold)
        result: str = tesseract.image_to_string(template)
        if is_number and not result.isdigit():
            result = tesseract.image_to_string(template, config="-psm 10")
        print("[Tesseract] {} -> {}".format(threshold, result))
        if result == "" or (is_number and not result.isdigit()):
            continue
        break
    if result == "" or (is_number and not result.isdigit()):
        return None
    if is_number:
        return int(result)
    return result
