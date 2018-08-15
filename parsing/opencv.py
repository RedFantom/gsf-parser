"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
import os
import sys
# Project Modules
from utils.directories import get_temp_directory
# Packages
from PIL import Image
import cv2 as cv
import numpy


def image_to_opencv(image: Image.Image)->numpy.array:
    """Convert a PIL image to a OpenCV compatible array"""
    path = os.path.join(get_temp_directory(), "temp.png")
    image.save(path)
    return cv.imread(path, 0)


def opencv_to_image(arr: numpy.array)->Image.Image:
    """Convert an OpenCV image to a PIL image"""
    return Image.fromarray(cv.cvtColor(arr, cv.COLOR_BGR2RGB))


def feature_match(image: Image.Image, template: Image.Image)->int:
    """Return the amount of features matched with ORB"""
    orb = cv.ORB_create()
    matcher = cv.BFMatcher(cv.NORM_L1, crossCheck=False)
    template = image_to_opencv(template.convert("RGB"))
    tp_kp, tp_ds = orb.detectAndCompute(template, None)
    image = image_to_opencv(image.convert("RGB"))
    im_kp, im_ds = orb.detectAndCompute(image, None)
    try:
        matches = matcher.knnMatch(tp_ds, im_ds, k=2)
    except cv.error as e:
        return 0
    result = 0
    for value in matches:
        if len(value) != 2:
            continue
        m, n = value
        if m.distance < 0.8 * n.distance:
            result += 1
    return result


def template_match(image: Image.Image, template: Image.Image, margin: float = 95, similarity: bool=False):
    """Use template matching and similarity to return template score"""
    image_cv, template_cv = map(image_to_opencv, (image, template))
    result = cv.matchTemplate(image_cv, template_cv, cv.TM_CCOEFF)
    _, _, _, loc = cv.minMaxLoc(result)
    image = image.crop((loc[0], loc[1], loc[0] + template.width, loc[1] + template.height))
    ratio = get_similarity(image, template)
    ratio = (ratio > margin) if similarity is False else ratio
    return ratio, loc


def get_similarity(template: Image.Image, to_match: Image.Image)->float:
    """Compares two images and returns the similarity ratio."""
    if template.size != to_match.size:
        raise ValueError("These images are not the same size. One: {}, Two: {}.".format(template.size, to_match.size))
    diff = sum(abs(color_one - color_two) for pair_one, pair_two in zip(template.getdata(), to_match.getdata())
               for color_one, color_two in zip(pair_one, pair_two) if not sum(pair_two) > 3 * 255 - 1)
    n_comps = template.size[0] * template.size[1] * 3
    return 100 - (diff / 255.0 * 100) / n_comps
