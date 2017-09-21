# This file contains utility code NOT written by RedFantom or Daethyra, though it may have been edited to suit a
# particular purpose better. This code was written by others. For the credits, see the block-comment in each class.
# This file is excluded from the copyright of RedFantom, Daethyra and Sprigellania, but the code in this file
# IS redistributed under the license found in LICENSE, so you only have to accept one License when using the
# software.
from ttkwidgets.frames import Balloon


class HoverInfo(Balloon):
    def __init__(self, parent, text="", width=70, headertext="Tooltip"):
        Balloon.__init__(self, master=parent, headertext=headertext, text=text, width=width * 5)
