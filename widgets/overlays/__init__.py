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

if settings["screen"]["experimental"] is True and platform == "linux":
    print("[ImportSystem] Importing GtkOverlay")
    try:
        from widgets.overlays.gtk import GtkOverlay as Overlay
    except ImportError as e:
        print("[ImportSystem] Could not import GtkOverlay: {}".format(e))
        from widgets.overlays.tkinter import TkinterOverlay as Overlay
else:
    print("[ImportSystem] Importing default TkinterOverlay")
    from widgets.overlays.tkinter import TkinterOverlay as Overlay
