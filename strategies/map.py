# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from strategies.tools import *
from strategies.strategies import *
import os
from PIL import Image, ImageTk
from ttkwidgets.color import askcolor
from ttkwidgets.font import FontSelectFrame
from ast import literal_eval


class Map(ttk.Frame):
    def __init__(self, *args, **kwargs):
        # Setup Frame
        self.current = None
        self.items = {}
        width = kwargs.pop("canvaswidth", 768)
        height = kwargs.pop("canvasheight", 768)
        self.readonly = kwargs.pop("readonly", False)
        self._additem_callback = kwargs.pop("additem_callback", None)
        self._moveitem_callback = kwargs.pop("moveitem_callback", None)
        self._delitem_callback = kwargs.pop("delitem_callback", None)
        self._map = kwargs.pop("map", None)
        ttk.Frame.__init__(self, *args, **kwargs)
        self._canvaswidth = width
        self._canvasheight = height
        # Setup Canvas
        self._max_x = self._canvaswidth - 10
        self._max_y = self._canvasheight - 10
        self.canvas = tk.Canvas(self, width=width, height=height)
        self._image = None
        self._background = None
        # Setup event bindings
        if not self.readonly:
            self.canvas.tag_bind("item", "<ButtonPress-1>", self.left_press)
            self.canvas.tag_bind("item", "<ButtonRelease-1>", self.left_release)
            self.canvas.tag_bind("item", "<B1-Motion>", self.left_motion)
            self.canvas.tag_bind("item", "<ButtonPress-3>", self.right_press)
            self.canvas.bind("<ButtonPress-3>", self.frame_right_press)
        # Setup item menu
        self.item_menu = tk.Menu(self, tearoff=0)
        self.item_menu.add_command(label="Edit", command=self.edit_item)
        self.item_menu.add_command(label="Delete", command=self.del_item)
        # Setup frame menu
        self.frame_menu = tk.Menu(self, tearoff=0)
        self.frame_menu.add_command(label="New", command=self.new_item)
        # Call grid_widgets last
        self.grid_widgets()
        self.client = None

    def frame_right_press(self, event):
        self.frame_menu.post(event.x_root, event.y_root)

    def left_press(self, event):
        if self.current:
            self.canvas.itemconfigure(self.current, fill="black")
            self.current = None
            return
        results = self.canvas.find_withtag(tk.CURRENT)
        if len(results) is 0:
            return
        self.current = results[0]
        self.canvas.itemconfigure(self.current, fill="blue")

    def left_release(self, event):
        self.config(cursor="")
        print("Left release")
        if not self.current:
            self.canvas.itemconfigure(tk.CURRENT, fill="black")

    def left_motion(self, event):
        self.current = None
        item = self.canvas.find_withtag(tk.CURRENT)[0]
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
        args = (self.canvas.itemcget(item, "text"), int(x / self._canvaswidth * 768), int(y / self._canvasheight * 768))
        self._moveitem_callback(*args)
        if self.client and self.client.logged_in:
            self.client.move_item(self.master.list.selected_strategy, self.master.list.selected_phase, *args)

    def right_press(self, event):
        if not self.current:
            return
        self.item_menu.post(event.x_root, event.y_root)

    def grid_widgets(self):
        self.canvas.grid(sticky="nswe")

    def set_background(self, type, map):
        if type != "tdm" and type != "dom":
            raise ValueError("Not a valid type value: {0}".format(type))
        if map != "de" and map != "km" and map != "ls":
            raise ValueError("Not a valid map value: {0}".format(map))
        map = map_dictionary[type][map]
        self._image = Image.open(os.path.join(get_assets_directory(), "{0}_{1}.jpg".format(type, map)))
        self._image = self._image.resize((self._canvaswidth, self._canvasheight), Image.ANTIALIAS)
        self._image = ImageTk.PhotoImage(self._image)
        self._background = self.canvas.create_image(0, 0, image=self._image, anchor=tk.NW, tag="background")
        self.canvas.tag_lower("background")

    def add_item(self, text, font=("default", 12, "bold"), color="yellow"):
        if len(font) == 2 and type(font) == tuple and type(font[1]) == tkfont.Font:
            font = font[0]
        if isinstance(font, str):
            font = literal_eval(font)
        item = self.canvas.create_text(0, 0, anchor=tk.NW, text=text, font=font, fill="black", tag="item")
        rectangle = self.canvas.create_rectangle(self.canvas.bbox(item), fill=color)
        self.canvas.tag_lower(rectangle, item)
        self.items[item] = (rectangle, item)
        self.items[text] = (rectangle, item)
        return item, rectangle, text, font, color

    def add_item_callback(self, *args, **kwargs):
        item, rectangle, text, font, color = self.add_item(*args, **kwargs)
        if callable(self._additem_callback):
            self._additem_callback(item, self.canvas.coords(rectangle), text, font, color)
        if self.client and self.client.logged_in:
            self.client.add_item(
                *(self.master.list.selected_strategy, self.master.list.selected_phase, text, font, color)
            )

    def new_item(self):
        window = AddItem(callback=self.add_item_callback)
        if hasattr(self.master, "list"):
            # Else master is MapToplevel and this is done elsewhere
            self.master.list.tree.column("#0", width=150)
        window.wait_window()

    def del_item(self):
        item = self.current
        rectangle = self.items[item][0]
        text = self.canvas.itemcget(item, "text")
        if callable(self._delitem_callback):
            self._delitem_callback(item, rectangle, text)
        if self.client and self.client.logged_in and self.master.list.selected_phase:
            self.client.del_item(self.master.list.selected_strategy, self.master.list.selected_phase, text)
        self.canvas.delete(item, rectangle)

    def update_map(self, phase):
        if not isinstance(phase, Phase):
            raise ValueError("map is not a Map instance")
        self.canvas.delete("all")
        type, map = phase.map
        self.set_background(type, map)
        for item, value in phase:
            item, rectangle, _, _, _ = self.add_item(text=value["name"], color=value["color"], font=value["font"])
            self.canvas.coords(item, int(value["x"] / 768 * self._canvaswidth),
                               int(value["y"] / 768 * self._canvasheight))
            self.canvas.coords(rectangle, self.canvas.bbox(item))
        return

    def edit_item(self):
        pass

    def set_readonly(self, readonly=False):
        self.readonly = readonly
        if not self.readonly:
            self.canvas.tag_bind("item", "<ButtonPress-1>", self.left_press)
            self.canvas.tag_bind("item", "<ButtonRelease-1>", self.left_release)
            self.canvas.tag_bind("item", "<B1-Motion>", self.left_motion)
            self.canvas.tag_bind("item", "<ButtonPress-3>", self.right_press)
            self.canvas.bind("<ButtonPress-3>", self.frame_right_press)
        else:
            self.canvas.tag_unbind("item", "<ButtonPress-1>")
            self.canvas.tag_unbind("item", "<ButtonRelease-1>")
            self.canvas.tag_unbind("item", "<B1-Motion>")
            self.canvas.tag_unbind("item", "<ButtonPress-3>")
            self.canvas.unbind("<ButtonPress-3>")


class AddItem(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self.callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add Item")
        self.attributes("-topmost", True)
        self.header_label = ttk.Label(self, text="Add a new item", font=("default", 12), justify=tk.LEFT)
        self.text_header = ttk.Label(self, text="Item text", font=("default", 11), justify=tk.LEFT)
        self.text = tk.StringVar()
        self.text_entry = ttk.Entry(self, textvariable=self.text)
        self.background_color = tk.StringVar()
        self.background_color.set("#ffffff")
        self.background_color_header = ttk.Label(self, text="Item background", font=("default", 11), justify=tk.LEFT)
        self.background_color_entry = tk.Entry(self, textvariable=self.background_color)
        self.background_color_button = ttk.Button(self, text="Choose color", command=self.update_color)
        self.font_header = ttk.Label(self, text="Item font", font=("default", 11), justify=tk.LEFT)
        self.font_select_frame = FontSelectFrame(self)
        self.add_button = ttk.Button(self, text="Add item", command=self.add_item)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.grid_widgets()

    def grid_widgets(self):
        # self.header_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.text_header.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.text_entry.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.background_color_header.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.background_color_entry.grid(row=6, column=0, sticky="nswe", padx=5, pady=5)
        self.background_color_button.grid(row=6, column=1, padx=5, pady=5)
        self.font_header.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.font_select_frame.grid(row=8, column=0, columnspan=3, sticky="nswe", padx=5, pady=5)
        self.add_button.grid(row=9, column=1, sticky="nswe", padx=5, pady=5)
        self.cancel_button.grid(row=9, column=0, sticky="nswe", padx=5, pady=5)

    def add_item(self):
        if callable(self.callback):
            if not self.font_select_frame._family:
                print("No font family selected.")
            font = self.font_select_frame.font if self.font_select_frame.font is not None else ("default", 12)
            if font == ("default", 12):
                print("Default font selected")
            self.callback(self.text.get(), font, color=self.background_color.get())
        self.destroy()

    def update_color(self):
        tuple, hex = askcolor()
        if not tuple or not hex:
            return
        self.background_color.set(hex)
        self.update_entry(tuple)

    def update_entry(self, color_tuple):
        red, green, blue = color_tuple
        self.background_color_entry.config(background=self.background_color.get(),
                                           foreground='#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186
                                           else "#ffffff")
