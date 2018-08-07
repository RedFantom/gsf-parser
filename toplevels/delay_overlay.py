"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from PIL import Image, ImageDraw, ImageFont
from utils.utilities import open_icon_pil
import variables


class _DelayOverlay(object):
    """Mixin for DelayOverlays to support image and text generation"""

    POOLS = ["Weapon", "Shield", "Engine"]

    POOL_IMAGES = {
        "Engine": "spvp_enginepower",
        "Shield": "spvp_shieldpower",
        "Weapon": "spvp_weaponpower",
    }

    def __init__(self):
        self._images = {p: open_icon_pil(self.POOL_IMAGES[p]).convert("RGBA") for p in self.POOLS}

    def generate_image(self, pool: str, delay: float, elapsed: float, rate: float):
        """Generate an Image and string  to use in the Overlay"""
        pass

    @staticmethod
    def position_str_to_tuple(position: str) -> tuple:
        return tuple(map(int, map(lambda s: str.strip(s, "x"), position.split("y"))))


try:
    if variables.settings["realtime"]["experimental"] is False:
        raise ImportError

    # Packages
    from gi.repository import Gtk, Gdk, GdkPixBuf
    from numpy import array
    # Project Modules
    from widgets.overlays.overlay_gtk import GtkOverlay


    class DelayOverlay(GtkOverlay, _DelayOverlay):
        """Delay Overlay based on GtkOverlay"""

        def __init__(self, position: str):
            """Initialize Widgets"""
            _DelayOverlay.__init__(self)
            position = self.position_str_to_tuple(position)
            GtkOverlay.__init__(self, position, standard=False)

        def _create_label(self, row: int, ):
            pass

        @staticmethod
        def image_to_gtk(image: Image.Image) -> GdkPixBuf.GdkPixBuf:
            """Convert a PIL Image to a Gdk PixBuf Image"""
            return GdkPixBuf.PixBuf.new_from_array(array(image), GdkPixBuf.Colorspace.RGB, 8)


except ImportError:
    # UI Libraries
    import tkinter as tk
    # Packages
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    # Project Modules
    from widgets.overlays.overlay_tkinter import TkinterOverlay


    class DelayOverlay(tk.Toplevel, TkinterOverlay, _DelayOverlay):
        """Simple DelayOverlay for Windows"""

        def __init__(self, position: tuple, master: tk.Tk):
            """Initialize as a proper Overlay window"""
            tk.Toplevel.__init__(self, master)
            self.setup_window()
            self.wm_geometry("+{}+{}".format(*self.position_str_to_tuple(position)))

        @staticmethod
        def image_to_tkinter(image: Image.Image) -> ImageTk.PhotoImage:
            """Convert an Image to a Tkinter compatible format"""
            return ImageTk.PhotoImage(image)
