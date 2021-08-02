"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from widgets.general.toggledframe import *
from widgets.general.scrollframe import *
from widgets.builds.crew import *
from widgets.builds.crew_list import *
from widgets.builds.ships import *
from widgets.builds.component_list import *
from widgets.builds.component import *
from widgets.overlays.tkinter import TkinterOverlay as Overlay
from ttkwidgets.frames import Tooltip


class Balloon(Tooltip):
    """Balloon widget override with default kwargs"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("width", 400)
        kwargs.setdefault("timeout", 0.5)
        Tooltip.__init__(self, *args, **kwargs)
