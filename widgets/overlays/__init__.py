"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from sys import platform
# Project Modules
from variables import settings

if settings["screen"]["experimental"] is True and platform == "win32":
    from widgets.overlays.overlay_windows import WindowsOverlay as Overlay
else:
    from widgets.overlays.overlay_tkinter import TkinterOverlay as Overlay

