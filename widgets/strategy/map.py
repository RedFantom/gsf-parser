"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
# Packages
from PIL import Image, ImageTk
# Project Modules
from parsing.strategies import *
from data.maps import map_dictionary
from utils.directories import get_assets_directory
from widgets.strategy.item import CreateItem


class Map(ttk.Frame):
    """
    Provides an interactive Tkinter Canvas to allow the user to create
    and edit markers on a large GSF Map image to plan Strategies
    and Tactics.
    """

    def __init__(self, *args, **kwargs):
        """
        :param canvaswidth: Width of the Tkinter Canvas
        :param canvasheight: Height of the Tkinter Canvas
        :param additem_callback: Callback called upon Menu selection
            for adding item. Arguments:
            item: str, coords: tuple, text: str, font: tuple,
            color: (str, tuple)
        :param moveitem_callback: Callback called upon movement
            of an item.  Arguments:
            item: str, x: float, y: float
        :param delitem_callback: Callback called upon Menu selection
            for deleting an item. Arguments:
            item: str, rectangle: int, text: int
        """
        # Arguments and Attributes
        self.current, self.client = None, None
        self.items = dict()
        self._canvas_width = width = kwargs.pop("canvaswidth", 768)
        self._canvas_height = height = kwargs.pop("canvasheight", 768)
        self.readonly = kwargs.pop("readonly", False)
        self._add_item_cb = kwargs.pop("additem_callback", None)
        self._move_item_cb = kwargs.pop("moveitem_callback", None)
        self._del_item_cb = kwargs.pop("delitem_callback", None)

        ttk.Frame.__init__(self, *args, **kwargs)

        # Setup Canvas
        self._max_x = self._canvas_width - 10
        self._max_y = self._canvas_height - 10
        self.canvas = tk.Canvas(self, width=width, height=height)
        self._image = None
        self._background = None
        self.setup_bindings()

        # Setup Menus
        self.item_menu = tk.Menu(self, tearoff=False)
        self.frame_menu = tk.Menu(self, tearoff=False)
        self.setup_menus()

        self.grid_widgets()
        self.client = None

    def setup_menus(self):
        """Add Commands to the Menu widgets"""
        self.item_menu.add_command(label="Edit", command=self.edit_item)
        self.item_menu.add_command(label="Delete", command=self.del_item)
        self.frame_menu.add_command(label="New", command=self.new_item)

    def setup_bindings(self):
        """Configure the bindings of the Canvas"""
        if self.readonly is True:
            self.canvas.tag_unbind("item", "<ButtonPress-1>")
            self.canvas.tag_unbind("item", "<ButtonRelease-1>")
            self.canvas.tag_unbind("item", "<B1-Motion>")
            self.canvas.tag_unbind("item", "<ButtonPress-3>")
            self.canvas.unbind("<ButtonPress-3>")
            return
        self.canvas.tag_bind("item", "<ButtonPress-1>", self.left_press)
        self.canvas.tag_bind("item", "<ButtonRelease-1>", self.left_release)
        self.canvas.tag_bind("item", "<B1-Motion>", self.left_motion)
        self.canvas.tag_bind("item", "<ButtonPress-3>", self.right_press)
        self.canvas.bind("<ButtonPress-3>", self.frame_right_press)
        self.canvas.bind("<ButtonPress-1>", self.frame_left_press)

    def frame_right_press(self, event):
        """
        Callback for Tkinter ButtonPress-3 event on self

        Opens the self.frame_menu in the event location
        """
        self.frame_menu.post(event.x_root, event.y_root)

    def frame_left_press(self, event):
        """
        Callback for Tkinter ButtonPress-1 event on self

        Closes the self.frame_menu
        """
        self.frame_menu.unpost()

    def left_press(self, event):
        """
        Callback for the Tkinter ButtonPress-1 event on Canvas

        Configures the active item on the Canvas
        """
        # Deselects item if one is active
        if self.current:
            self.canvas.itemconfigure(self.current, fill="black")
            self.current = None
            return
        # Select a new one if one is pressed
        results = self.canvas.find_withtag(tk.CURRENT)
        if len(results) == 0:
            return
        self.current = results[0]
        self.canvas.itemconfigure(self.current, fill="blue")

    def left_release(self, event):
        """
        Callback for the Tkinter ButtonRelease-1 event on Canvas

        This event follows a B1-Motion event. Resets UI if required.
        Additionally sends the new location of the moved item to the
        server if the GSF Parser is connected to one.

        The StrategyServer is only notified once the item is
        dropped to reduce amount of messages sent.
        """
        self.config(cursor="")
        if not self.current:
            self.canvas.itemconfigure(tk.CURRENT, fill="black")
        if self.client is not None and self.client.logged_in is True:
            item = self.canvas.find_withtag(tk.CURRENT)[0]
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            args = (self.canvas.itemcget(item, "text"), int(x / self._canvas_width * 768),
                    int(y / self._canvas_height * 768))
            self.client.move_item(self.master.list.selected_strategy, self.master.list.selected_phase, *args)

    def left_motion(self, event):
        """
        Callback for the Tkinter B1-Motion event on Canvas

        Moves the selected item to a new location indicated by the
        movement, then drops it and sets it as not-active. Additionally
        calls the callback to notify the parent.
        """
        self.current = None
        item = self.active
        rectangle = self.items[item][0]
        self.config(cursor="exchange")
        self.canvas.itemconfigure(item, fill="blue")
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        x = self._max_x if x > self._max_x else x
        y = self._max_y if y > self._max_y else y
        x = 0 if x < 0 else x
        y = 0 if y < 0 else y
        self.canvas.coords(item, x, y)
        self.canvas.coords(rectangle, self.canvas.bbox(item))
        if callable(self._move_item_cb):
            args = (
                self.canvas.itemcget(item, "text"),
                int(x / self._canvas_width * 768),
                int(y / self._canvas_height * 768)
            )
            self._move_item_cb(*args)

    def right_press(self, event):
        """
        Callback for the Tkinter ButtonPress-3 event on Canvas

        Opens the item_menu if an item is selected
        """
        if self.current is None:
            return
        self.item_menu.post(event.x_root, event.y_root)

    def grid_widgets(self):
        """Configures widgets in grid geometry manager"""
        self.canvas.grid(sticky="nswe")

    def set_background(self, type: str, map: str):
        """
        Updates the background map set for the Canvas
        :param type: match type, 'tdm' or 'dom'
        :param map: specific map, see data.maps.map_dictionary
        """
        image_name = map_dictionary[type][map]  # FQN for Map
        self._image = Image.open(os.path.join(get_assets_directory(), "maps", "{0}_{1}.jpg".format(type, image_name)))
        self._image = self._image.resize((self._canvas_width, self._canvas_height), Image.ANTIALIAS)
        self._image = ImageTk.PhotoImage(self._image)
        self._background = self.canvas.create_image(0, 0, image=self._image, anchor=tk.NW, tag="background")
        self.canvas.tag_lower("background")

    def add_item(self, text, font: tuple=("default", 12, "bold"), color="yellow"):
        """
        Create a new item on the Map in the origin location
        :param text: text of the item
        :param font: font for the text of the item
        :param color: background color of the item
        """
        if text in self.items:
            # Prevent adding of duplicate items
            rectangle, item = self.items[text]
            return item, rectangle, text, font, color
        # ttkwidgets.font support
        if isinstance(font, tuple) and len(font) == 2 and isinstance(font[1], tkfont.Font):
            font = font[0]
        # StrategyClient font support, must then be tuple
        if isinstance(font, str):
            font = literal_eval(font)
        item = self.canvas.create_text(0, 0, anchor=tk.NW, text=text, font=font, fill="black", tag="item")
        rectangle = self.canvas.create_rectangle(self.canvas.bbox(item), fill=color)
        self.canvas.tag_lower(rectangle, item)
        self.items[item] = (rectangle, item)
        self.items[text] = (rectangle, item)
        return item, rectangle, text, font, color

    def add_item_callback(self, *args, **kwargs):
        """
        Callback for the AddItem Toplevel to create the item and, if
        required notify the StrategyServer.

        Note that add_item does not notify the StrategyServer, as the
        item may have been created by another Client on the Server and
        thus notifying the StrategyServer would cause infinite
        recursion. This function prevents that.
        """
        item, rectangle, text, font, color = self.add_item(*args, **kwargs)
        if callable(self._add_item_cb):
            self._add_item_cb(item, self.canvas.coords(rectangle), text, font, color)
        if self.client and self.client.logged_in:
            self.client.add_item(
                self.master.list.selected_strategy, self.master.list.selected_phase, text, font, color)

    def new_item(self):
        """
        Callback for New Item command of frame_menu

        Opens an AddItem Toplevel and waits for teh window to close
        """
        window = CreateItem(callback=self.add_item_callback)
        if hasattr(self.master, "list"):
            # Else master is MapToplevel and this is done elsewhere
            self.master.list.tree.column("#0", width=150)
        window.wait_window()

    def del_item(self):
        """
        Callback for Delete Item command of item_menu

        Deletes the selected item from the Map, calling the callback
        to notify the parent. Deletes the item from the Strategy
        in the StrategyDatabase and immediately saves to prevent
        data loss.
        """
        item = self.current
        rectangle = self.items[item][0]
        text = self.canvas.itemcget(item, "text")
        if callable(self._del_item_cb):
            self._del_item_cb(item, rectangle, text)
        if self.client and self.client.logged_in and self.master.list.selected_phase:
            self.client.del_item(self.master.list.selected_strategy, self.master.list.selected_phase, text)
        if text in self.master.list.db[self.master.list.selected_strategy][self.master.list.selected_phase]:
            del self.master.list.db[self.master.list.selected_strategy][self.master.list.selected_phase][text]
            self.master.list.db.save_database()
        self.master.list.db.save_database()
        self.canvas.delete(item, rectangle)

    def update_map(self, phase: Phase):
        """Update the contents of the Map to represent Phase"""
        self.canvas.delete("all")
        self.items.clear()
        type, map = phase.map
        self.set_background(type, map)
        for _, value in phase:
            item, rectangle, _, _, _ = self.add_item(text=value["name"], color=value["color"], font=value["font"])
            self.canvas.coords(
                item, int(value["x"] / 768 * self._canvas_width), int(value["y"] / 768 * self._canvas_height))
            self.canvas.coords(rectangle, self.canvas.bbox(item))
        self.canvas.tag_lower("background")
        self.canvas.tag_raise("item")

    def edit_item(self):
        """TODO: Implement editing of item"""
        pass

    def set_readonly(self, readonly=False):
        """Update read-ony state of the Map"""
        self.readonly = readonly
        self.setup_bindings()

    @property
    def active(self):
        """Return the currently selected item if there is one"""
        result = self.canvas.find_withtag(tk.CURRENT)  # : tuple
        if result is None or len(result) == 0:
            return None
        return result[0]
