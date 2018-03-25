"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from ttkwidgets.frames import Balloon


class HoverInfo(Balloon):
    def __init__(self, parent, text="", width=70, headertext="Tooltip"):
        Balloon.__init__(self, master=parent, headertext=headertext, text=text, width=width * 5)

