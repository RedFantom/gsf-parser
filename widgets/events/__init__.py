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
    print("[ImportSystem] Importing GtkEventsOverlay")
    try:
        from widgets.events.gtk import GtkEventsOverlay as EventOverlay
    except ImportError as e:
        print("[ImportSystem] Could not import GtkEventsOverlay: {}".format(e))
        from widgets.events.tkinter import EventOverlay
else:
    print("[ImportSystem] Importing default EventsOverlay")
    from widgets.events.tkinter import EventOverlay
