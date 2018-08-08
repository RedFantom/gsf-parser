"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
# UI Libraries
import tkinter as tk
# Packages
from PIL import Image, ImageDraw, ImageFont
# Project Modules
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
        self._origs = {p: open_icon_pil(self.POOL_IMAGES[p]).convert("RGBA") for p in self.POOLS}
        try:
            self._font = ImageFont.truetype("FreeMonoBold", 16)
        except OSError:
            self._font = ImageFont.truetype("Calibri", 16)
        self._stats = {pool: {k: 0.0 for k in ("Delay", "Normal", "Recent")} for pool in self.POOLS}
        self._times = dict()
        self._remaining = dict()

    @staticmethod
    def position_str_to_tuple(position: str) -> tuple:
        return tuple(map(int, map(lambda s: str.strip(s, "x"), position.split("y"))))

    def set_power_pool_regen_rate(self, pool: str, string: str):
        """Set active power pool regen rate in the proper string"""
        raise NotImplementedError()

    def set_power_pool_regen_delay(self, pool: str, string: str, percentage: float):
        """Set the remaining regeneration delay for a power pool"""
        raise NotImplementedError()

    def generate_cooldown_image(self, text: str, percentage: float, size: tuple = (50, 50)) -> Image.Image:
        """Generate a cooldown image to combine with a normal image"""
        image = Image.new("RGBA", size=size, color=(255, 255, 255, 0))
        draw = ImageDraw.ImageDraw(image, "RGBA")
        w, h = draw.textsize(text, font=self._font)
        x, y = map(lambda t: (t[0] - t[1]) // 2, zip(size, (w, h)))
        draw.rectangle((0, int(size[1] * (1.0 - percentage)), 50, 50), fill=(0, 255, 255, 150))
        draw.text((x - 1, y - 1), text, fill="black", anchor=tk.CENTER, font=self._font)
        draw.text((x + 1, y - 1), text, fill="black", anchor=tk.CENTER, font=self._font)
        draw.text((x - 1, y + 1), text, fill="black", anchor=tk.CENTER, font=self._font)
        draw.text((x + 1, y + 1), text, fill="black", anchor=tk.CENTER, font=self._font)
        draw.text((x, y), text, fill="yellow", anchor=tk.CENTER, font=self._font)
        return image
    
    def update_state(self, results: dict):
        """Update the state of the self"""
        if results == "start":
            self.show()
            return
        elif results == "end":
            self.hide()
            return
        time = datetime.now()
        stats = results.pop("Stats", {})
        self._stats.update(stats)
        for pool, start in results.items():
            if pool not in self._times or self._times[pool] != start:
                self._times[pool] = start
        for pool, start in self._times.items():
            results[pool] = dict()
            elapsed = (time - start).total_seconds()
            if pool in self._remaining and abs(self._remaining[pool] - elapsed) < 0.1:
                continue
            self._remaining[pool] = elapsed
            remaining = max(0.0, self._stats[pool]["Delay"] - elapsed)
            delay = "{:.1f}s".format(remaining)
            if self._stats[pool]["Delay"] == 0.0:
                continue
            percentage = remaining / self._stats[pool]["Delay"]
            rate = self._stats[pool]["Normal"] if remaining == 0.0 else self._stats[pool]["Recent"]
            self.set_power_pool_regen_rate(pool, "{:.1f}".format(rate))
            self.set_power_pool_regen_delay(pool, delay, percentage)

    def show(self):
        raise NotImplementedError()

    def hide(self):
        raise NotImplementedError()


try:
    if variables.settings["screen"]["experimental"] is False:
        raise ImportError

    # Standard Library
    import os
    # Packages
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
    from numpy import array
    # Project Modules
    from utils.directories import get_assets_directory
    from widgets.overlays.overlay_gtk import GtkOverlay

    ROWS = {
        "Weapon": 0,
        "Shield": 1,
        "Engine": 2,
    }


    class DelayOverlay(GtkOverlay, _DelayOverlay):
        """Delay Overlay based on GtkOverlay"""

        FMT = '<span color="yellow" weight="bold" size="11500">{}</span>'

        def __init__(self, position: str, *args):
            """Initialize Widgets"""
            _DelayOverlay.__init__(self)
            position = self.position_str_to_tuple(position)
            GtkOverlay.__init__(self, position, standard=False)
            self._images, self._labels, self._texts = dict(), dict(), dict()

            for i, pool in enumerate(self.POOLS):
                path = os.path.join(get_assets_directory(), "icons", self.POOL_IMAGES[pool] + ".jpg")
                self._images[pool] = Gtk.Image.new_from_file(path)
                self._labels[pool] = Gtk.Label()
                self._labels[pool].set_use_markup(True)
                self._texts[pool] = Gtk.Label()
                self._texts[pool].set_use_markup(True)
                self.grid(self._images[pool], i, 0)
                self.grid(self._labels[pool], i, 1)
                self.grid(self._texts[pool], i, 0)

        def grid(self, widget: Gtk.Widget, row: int, column: int):
            """Configure widget in Gtk.Grid in self"""
            self._grid.attach(widget, column, row, 1, 1)
            self.show_all()

        def grid_forget(self, widget: Gtk.Widget):
            """Remove the widget from the Gtk.Grid"""
            self._grid.remove(widget)

        def set_power_pool_regen_rate(self, pool: str, string: str):
            """Update the power pool regeneration rate"""
            self._labels[pool].set_markup(self.FMT.format(string))

        def set_power_pool_regen_delay(self, pool: str, string: str, percentage: float):
            """Create a text on the Canvas on top of the image"""
            image = self.generate_cooldown_image(string, percentage)
            image = Image.composite(image, self._origs[pool], image)
            self.grid_forget(self._images[pool])
            self._images[pool] = Gtk.Image.new_from_pixbuf(self.image_to_pixbuf(image))
            self.grid(self._images[pool], ROWS[pool], 0)

        @staticmethod
        def image_to_pixbuf(image: Image.Image) -> GdkPixbuf.Pixbuf:
            """Convert a pillow Image to a Pixbuf"""
            data = GLib.Bytes.new(image.convert("RGB").tobytes())
            return GdkPixbuf.Pixbuf.new_from_bytes(
                data, GdkPixbuf.Colorspace.RGB, False, 8, *image.size, image.size[0] * 3)


    if __name__ == '__main__':
        overlay = DelayOverlay("x0y0")
        overlay.set_power_pool_regen_rate("Shield", "153.4")
        overlay.set_power_pool_regen_delay("Shield", "8.6s", 0.5)
        Gtk.main()


except ImportError:
    # Packages
    from PIL import ImageTk
    # Project Modules
    from widgets.overlays.overlay_tkinter import TkinterOverlay


    class DelayOverlay(TkinterOverlay, _DelayOverlay):
        """Simple DelayOverlay for Windows"""

        def __init__(self, position: str, master: tk.Tk):
            """Initialize as a proper Overlay window"""
            _DelayOverlay.__init__(self)
            tk.Toplevel.__init__(self, master, background="darkblue", width=120)
            self.setup_window()
            self.wm_geometry("+{}+{}".format(*self.position_str_to_tuple(position)))
            self._labels, self._texts, self._coords, self._refs = dict(), dict(), dict(), dict()
            self._canvas = tk.Canvas(self, background="darkblue", border=0, width=50, height=3 * 50)
            img_y = 0
            for pool, image in self._origs.items():
                self._labels[pool] = tk.Label(
                    self, foreground="yellow", background="darkblue", font=("default", 12, "bold"))
                self._origs[pool] = ImageTk.PhotoImage(image)
                iid = self._canvas.create_image(
                    0, img_y, anchor=tk.NW, image=self._origs[pool], tag="img")
                self._refs[pool] = iid
                x1, y1, x2, y2 = self._canvas.bbox(iid)
                x, y, w, h = x1, y1, (x2 - x1), (y2 - y1)
                img_y += h
                self._coords[pool] = (x + w // 2, y + h // 2)
            self._canvas.tag_lower("img")
            self.grid_widgets()

        def grid_widgets(self):
            """Configure widgets in grid geometry manager"""
            for i, pool in enumerate(self.POOLS):
                self._labels[pool].grid(row=i, column=1, sticky="nswe")
            self._canvas.grid(row=0, column=0, rowspan=3, sticky="nswe", padx=(0, 5))

        def set_power_pool_regen_rate(self, pool: str, string: str):
            """Update the power pool regeneration rate"""
            self._labels[pool].config(text=string)

        def set_power_pool_regen_delay(self, pool: str, string: str, percentage: float):
            """Create a text on the Canvas on top of the image"""
            if pool in self._texts:
                self._canvas.delete(*self._texts[pool])
            self._refs[pool + "Img"] = ImageTk.PhotoImage(self.generate_cooldown_image(string, percentage))
            x1, y1, x2, y2 = self._canvas.bbox(self._refs[pool])
            box = self._canvas.create_image(0, y2, anchor=tk.SW, image=self._refs[pool + "Img"])
            self._texts[pool] = (box,)
            self._canvas.tag_raise("text")

        def hide(self):
            """Hide the Overlay"""
            self.wm_attributes("-topmost", False)
            self.wm_iconify()

        def show(self):
            """Show the overlay"""
            self.wm_deiconify()
            self.wm_attributes("-topmost", True)


    if __name__ == '__main__':
        w = tk.Tk()
        overlay = DelayOverlay("x0y0", w)
        overlay.set_power_pool_regen_delay("Shield", "8.6s", 0.5)
        overlay.set_power_pool_regen_rate("Shield", "153.4")
        w.mainloop()
