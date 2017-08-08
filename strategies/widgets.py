# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import messagebox
from strategies.tools import *
from strategies.strategies import *
from strategies.toplevels import AddStrategy, AddItem, AddPhase
import os
from PIL import Image, ImageTk


class Map(ttk.Frame):
    def __init__(self, *args, **kwargs):
        # Setup Frame
        self.current = None
        self.items = {}
        width = kwargs.pop("canvaswidth", 385)
        height = kwargs.pop("canvasheight", 385)
        self._additem_callback = kwargs.pop("additem_callback", None)
        self._moveitem_callback = kwargs.pop("moveitem_callback", None)
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
        rectangle = self.items[item]
        self.config(cursor="exchange")
        self.canvas.itemconfigure(item, fill="blue")
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        x = self._max_x if x > self._max_x else x
        y = self._max_y if y > self._max_y else y
        x = 0 if x < 0 else x
        y = 0 if y < 0 else y
        self.canvas.coords(item, x, y)
        self.canvas.coords(rectangle, self.canvas.bbox(item))
        self._moveitem_callback(self.canvas.itemcget(item, "text"), x, y)

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
        print("Arguments received:\nText: {0}\nFont: {1}\nColor: {2}".format(text, font, color))
        if len(font) == 2 and type(font) == tuple and type(font[1]) == tkfont.Font:
            font = font[0]
        item = self.canvas.create_text(0, 0, anchor=tk.NW, text=text, font=font, fill="black", tag="item")
        rectangle = self.canvas.create_rectangle(self.canvas.bbox(item), fill=color)
        self.canvas.tag_lower(rectangle, item)
        self.items[item] = rectangle
        return item, rectangle, text, font, color

    def add_item_callback(self, *args, **kwargs):
        item, rectangle, text, font, color = self.add_item(*args, **kwargs)
        if callable(self._additem_callback):
            self._additem_callback(item, self.canvas.coords(rectangle), text, font, color)

    def new_item(self):
        window = AddItem(callback=self.add_item_callback)
        self.master.list.tree.column("#0", width=150)
        window.wait_window()

    def del_item(self):
        item = self.current
        rectangle = self.items[item]
        self.canvas.delete(item, rectangle)

    def update_map(self, phase):
        if not isinstance(phase, Phase):
            raise ValueError("map is not a Map instance")
        self.canvas.delete("all")
        type, map = phase.map
        self.set_background(type, map)
        for item, value in phase:
            item, rectangle, _, _, _ = self.add_item(text=value["name"], color=value["color"], font=value["font"])
            self.canvas.coords(item, value["x"], value["y"])
            self.canvas.coords(rectangle, self.canvas.bbox(item))
        return

    def edit_item(self):
        pass


class StrategyList(ttk.Frame):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop("callback", None)
        self._settings_callback = kwargs.pop("settings_callback", None)
        ttk.Frame.__init__(self, *args, **kwargs)
        self.db = StrategyDatabase()
        self.phase = None
        self._flipped = False
        self._phase_menu = tk.Menu(self, tearoff=0)
        self._phase_menu.add_command(label="Rename", command=self.edit_phase)
        self._phase_menu.add_command(label="Delete", command=self.del_phase)
        self._strategy_menu = tk.Menu(self, tearoff=0)
        self._strategy_menu.add_command(label="Add phase", command=self.add_phase)
        self.tree = ttk.Treeview(self, height=11)
        self.scrollbar = ttk.Scrollbar(self, command=self.tree.yview, orient=tk.VERTICAL)
        self.tree.config(yscrollcommand=self.scrollbar.set)
        self.tree.bind("<Button-3>", self._right_click)
        self.tree.bind("<Double-1>", self._select)
        self.tree.heading("#0", text="Strategies")
        self.tree.column("#0", width=150)
        self.new_button = ttk.Button(self, text="New strategy", command=self.new_strategy)
        self.del_button = ttk.Button(self, text="Delete strategy", command=self.del_strategy)
        self.edit_button = ttk.Button(self, text="Edit strategy", command=self.edit_strategy, state=tk.DISABLED)
        self.grid_widgets()

    def grid_widgets(self):
        self.tree.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)
        self.new_button.grid(row=1, column=0, columnspan=2, sticky="nswe", pady=5, padx=5)
        self.del_button.grid(row=3, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.edit_button.grid(row=4, column=0, columnspan=2, sticky="nswe", pady=(0, 5), padx=5)
        self.update_tree()

    def add_item_to_phase(self, item, box, text, font, color):
        item_obj = Item(text, box[0], box[1], color, font)
        try:
            self.db[self.selected_strategy][self.selected_phase][text] = item_obj
        except KeyError:
            self.db[self.selected_strategy][self.phase][text] = item_obj
        self.db.save_database()

    def move_item_phase(self, text, x, y):
        self.db[self.selected_strategy][self.selected_phase][text]["x"] = x
        self.db[self.selected_strategy][self.selected_phase][text]["y"] = y
        self.db.save_database()

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        iterator = self.db
        for strategy, content in iterator:
            print("Found a strategy: ", strategy)
            self.tree.insert("", tk.END, iid=strategy, text=strategy)
            for phase in content:
                self.tree.insert(strategy, tk.END, iid=(content.name, "..", phase[0]), text=phase[0])

    def _right_click(self, event):
        selection = self.tree.selection()
        if len(selection) is 0:
            print("No item in the tree is selected")
            return
        value = selection[0]
        elements = value.split("..")
        if len(elements) is 1:
            self._strategy_menu.post(event.x_root, event.y_root)
        elif len(elements) is 2:
            self._phase_menu.post(event.x_root, event.y_root)
        else:
            raise ValueError("Invalid elements value found: ", elements)

    def _left_click(self, event):
        print("Left click")

    def sort_strategies(self):
        self._flipped = not self._flipped
        self.update_tree()

    def new_strategy(self):
        window = AddStrategy(db=self.db)
        window.wait_window()
        self.update_tree()

    def del_strategy(self):
        selection = self.tree.selection()
        print("Selection: ", selection)
        if len(selection) is 0:
            return
        selection = selection[0]
        print("Selection[0]: ", selection)
        if selection not in self.db.keys():
            print("Strategy not found in database: {0}".format(self.db.keys()))
            return
        del self.db[selection]
        self.update_tree()

    def add_phase(self):
        window = AddPhase(callback=self._new_phase)
        window.wait_window()

    def del_phase(self):
        del self.db[self.selected_strategy][self.selected_phase]
        self.db.save_database()
        self.update_tree()

    def edit_phase(self):
        pass

    def _new_phase(self, title):
        self.db[self.selection][title] = Phase(title, self.db[self.selected_strategy].map)
        self.update_tree()
        self.db.save_database()

    def edit_strategy(self):
        pass

    def _select(self, event):
        if self.selected_phase:
            self._phase_selected()
            if callable(self._callback):
                self._callback(self.selected_phase)
            self._phase = self.selected_phase
            self.master.description.delete("1.0", tk.END)
            self.master.description.insert("1.0", self.db[self.selected_strategy][self.selected_phase].description)
        else:
            self.master.description.delete("1.0", tk.END)
            self.master.description.insert("1.0", self.db[self.selected_strategy].description)
            self._strategy_selected()

    def _strategy_selected(self):
        self.new_button.config(text="New strategy", command=self.new_strategy)
        self.del_button.config(text="Delete strategy", command=self.del_strategy)
        self.edit_button.config(text="Add phase", command=self.add_phase, state=tk.NORMAL)

    def _phase_selected(self):
        # self.new_button.config(text="New strategy", state=tk.DISABLED)
        self.del_button.config(text="Delete phase", command=self.del_phase)
        self.edit_button.config(text="Edit phase", command=self.edit_phase, state=tk.DISABLED)

    @property
    def selection(self):
        selection = self.tree.selection()
        if len(selection) is 0:
            return None
        print("Returning selection: ", selection[0])
        return selection[0]

    @property
    def selected_strategy(self):
        selection = self.selection
        if not selection:
            return None
        elements = selection.split("..")
        print("Got elements: ", elements)
        strategy = elements[0]
        strategy = strategy.strip()
        return strategy.replace("{", "").replace("}", "")

    @property
    def selected_phase(self):
        selection = self.selection
        if not selection:
            return None
        elements = selection.split("..")
        if len(elements) is not 2:
            return None
        phase = elements[1]
        if phase.startswith(" "):
            phase = phase[1:]
        if phase.endswith(" "):
            phase = phase[:1]
        print("Returning phase: ", phase)
        return phase.replace("{", "").replace("}", "")
