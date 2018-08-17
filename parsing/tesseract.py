"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
from subprocess import Popen, PIPE
# Packages
from PIL import Image, ImageFilter
from pytesseract import pytesseract as tesseract
# Project Modules
from parsing import imageops
from utils.directories import get_assets_directory

DIGITS = ["kills", "assists", "deaths", "damage", "hit", "objectives", "score"]

START, END, DIFF = 650, 400, 20
ROWS = 17.2
WHITELIST = \
    "-c tessedit_char_whitelist=\"" \
    "abcdefghijklmnopqrstuvwxyz" \
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
    "-áàäúùüóòöéèëíìï'\""

NUMBERS = "-c tessedit_char_whitelist=\"0123456789\""


def is_installed() -> bool:
    """Determine whether Tesseract-OCR is installed in PATH"""
    cmd = tesseract.tesseract_cmd
    p = Popen([cmd, "--help"], stdout=PIPE)
    p.wait()
    out, err = p.communicate()
    return b"Usage" in out


def high_pass_invert(image: Image.Image, treshold: int) -> Image.Image:
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


def perform_ocr(image: Image.Image) -> (None, str):
    """Perform OCR on an Image"""
    if not is_installed():
        print("[Tesseract] Critical error: Tesseract is not installed!")
        return None
    result = None
    for threshold in range(START, END, -DIFF):
        template: Image.Image = high_pass_invert(image, threshold)
        result: str = tesseract.image_to_string(template)
        if result == "":
            continue
        break
    if result == "":
        return None
    return result


def perform_ocr_scoreboard(image: Image.Image, column: str, start=START, end=END, diff=DIFF)->(str, int, None):
    """Perform OCR on a part of an image"""
    result = None
    is_number = column in DIGITS
    for treshold in range(start, end, -diff):  # Continue until result is valid
        template = high_pass_invert(image, treshold)
        result = tesseract.image_to_string(template, config="" if column in DIGITS else WHITELIST)
        if is_number and not result.isdigit():  # Try again for numbers
            result = tesseract.image_to_string(template, config="-psm 10")
        if is_number and not result.isdigit():
            template = template.filter(ImageFilter.GaussianBlur())
            result = tesseract.image_to_string(template, config="-psm 10")
        if result == "" or (is_number and not result.isdigit()):
            continue
        break
    if is_number and not result.isdigit():
        result = match_digit(high_pass_invert(image, 650))
    if result == "" or (is_number and not result.isdigit()):
        return 0 if is_number else None
    if is_number:
        return int(result)
    return result.replace("\n", "").replace("  ", "")


def match_digit(image: Image.Image)->str:
    """Match the digit in the image to a template in the assets folder"""
    image = image.convert("RGB")
    folder = os.path.join(get_assets_directory(), "digits")
    digits = os.listdir(folder)
    results = dict()
    pixels = image.load()
    min_x, min_y = image.width - 1, image.height - 1
    max_x, max_y = 0, 0
    for x in range(image.width):
        for y in range(image.height):
            if sum(pixels[x, y]) < 128:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    box = (min_x - 3, min_y - 3, max_x + 3, max_y + 3)
    image = image.crop(box).resize((50, 50), Image.BICUBIC)
    for digit in sorted(digits):
        if not digit.endswith(".png"):
            continue
        template: Image.Image = Image.open(os.path.join(folder, digit)).convert("RGB")
        digit = digit[:-4]
        results[digit] = imageops.get_similarity_monochrome(template, image)
        print("Rows: {} -> {}".format(digit, results[digit]))
    return max(results, key=lambda key: results[key])
