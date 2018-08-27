"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom
"""
# Standard Library
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
# UI Libraries
import tkinter as tk
from tkinter import ttk
# Project Modules
import humanize


BoxCoords = Tuple[int, int, int, int]
Coords = Tuple[int, int]


class ChatWindow(tk.Canvas):
    """
    Chat window based on tk.Canvas

    Window that can display chat messages with a timestamp with nice
    rounded backgrounds.
    """

    _CUSTOM = [
        "width"
    ]

    def __init__(self, master: (tk.Widget, tk.Frame, tk.Tk), **kwargs):
        """
        :param master: Master widget
        :param kwargs: Additional keyword arguments passed to Canvas
        """
        self._padx = kwargs.pop("padx", 5)
        self._pady = kwargs.pop("pady", 5)
        self._date_markers = kwargs.pop("date_markers", True)
        self._timeout = kwargs.pop("timeout", 10000)
        kwargs.setdefault("width", 300)
        self._width = kwargs.get("width")
        scrollbar: ttk.Scrollbar = kwargs.pop("scrollbar", None)

        tk.Canvas.__init__(self, master, **kwargs)
        self._config_scroll(scrollbar)

        self._messages: Dict[str, Dict[str, Any]] = dict()
        self._order: List[str] = list()
        self._id = 1
        self._after_id = self.after(self._timeout, self.update_messages)

        self.bind("<MouseWheel>", self.yview_scroll)

    def _config_scroll(self, scrollbar: ttk.Scrollbar):
        """Configure a scrollbar to be used"""
        if scrollbar is not None:
            print("[ChatWindow] Configuring scrollbar: {}".format(scrollbar))
            scrollbar.configure(command=self.yview)
            self.configure(yscrollcommand=scrollbar.set)

    def update_messages(self):
        """Update the timestamps of all drawn messages"""
        for key, message in self._messages.items():
            time_id = message["ids"][1]
            text = self.format_time(message["time"])
            self.itemconfig(time_id, text=text)
        self._after_id = self.after(self._timeout, self.update_messages)

    def _draw_message(self, time: datetime, author: str, text: str, color: str) -> Tuple[str, str, str, str]:
        """
        Draw a single message on the Canvas in the correct position

        The message is drawn as a nicely rounded rectangle with a fill
        color. The text is drawn inside the rectangle. Dates are also
        marked with additional round, light grey markers.
        """
        time = self.format_time(time)
        y1: int = self.vertical_position
        x1, x2 = self._padx, self._width - self._padx

        author_coords: Coords = (x1 + self._padx, y1 + self._pady)
        author_id = self.create_text(
            author_coords, text=author, anchor=tk.NW, font=("default", 12, "bold"))
        x1a, y1a, x2a, y2a = self.bbox(author_id)

        time_coords: Coords = (x2a + 4, y2a - 2)
        time_id = self.create_text(
            time_coords, text=time, anchor=tk.SW, font=("default", 9, "italic"))

        width = self._width - 4 * self._padx
        text_id = self.create_text(
            (x1a, y2a + 4), text=text, anchor=tk.NW, justify=tk.LEFT, width=width)
        x1t, y1t, x2t, y2t = self.bbox(text_id)

        box: BoxCoords = (x1, y1, x2, y2t + self._pady)
        rectangle_id = self.create_rounded_rectangle(box, 15, fill=color, tags=("rectangle",))

        self.tag_lower("rectangle")

        return author_id, time_id, text_id, rectangle_id

    def create_message(self, time: datetime, author: str, text: str, color: str, redraw: bool=True) -> str:
        """Create a message in the widget and draw it"""
        message_id: str = str(self._id)
        self._id += 1
        self._messages[message_id] = {
            "time": time,
            "author": author,
            "text": text,
            "color": color,
            "ids": self._draw_message(time, author, text, color)
        }
        x1, y1, x2, y2 = self.bbox(self._messages[message_id]["ids"][3])
        self._messages[message_id]["box"] = \
            (x1 - self._padx, y1 - self._pady, x2 + self._padx, y2 + self._pady)

        if time < self._messages[self.most_recent]["time"] and redraw:
            self.redraw_messages()
        self.update_scroll_region()

        return message_id

    def redraw_messages(self):
        """Redraw all the messages in the widget"""
        for key in sorted(self._messages.keys(), key=lambda k: self._messages[k]["time"]):
            message: Dict[str, Any] = self._messages[key]
            self._messages[key]["ids"] = self._draw_message(
                message["time"], message["author"], message["text"], message["color"])

    def update_scroll_region(self):
        """Update the scrollregion of self with the bounding box of all"""
        x1, y1, x2, y2 = self.bbox(tk.ALL)
        box: Tuple = (x1 - self._padx, y1 - self._pady, x2 + self._padx, y2 + self._pady)
        self.configure(scrollregion=box)

    def create_rounded_rectangle(self, box: Tuple[int, int, int, int], radius: int, **kwargs) -> str:
        """Draw a rounded rectangle in a specified location"""
        (x1, y1, x2, y2), r = box, radius
        points = [
            x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2,
            y2 - r, x2, y2, x2 - r, y2, x2 - r, y2, x1 + r,
            y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r,
            x1, y1 + r, x1, y1 + r, x1, y1
        ]
        kwargs.setdefault("smooth", True)
        return self.create_polygon(points, **kwargs)

    @property
    def most_recent(self) -> (None, str):
        """Return the time of the most recent message"""
        if len(self._messages) == 0:
            return None
        key = lambda k: self._messages[k]["time"].timestamp()
        return list(reversed(sorted(self._messages.keys(), key=key)))[-1]

    @property
    def vertical_position(self) -> int:
        """Return the vertical position to place a new message at"""
        if len(self._messages) == 0:
            return self._pady
        return self._messages[self.most_recent]["box"][3]

    @property
    def messages(self):
        """Return a read-only copy of the messages in the widget"""
        return self._messages.copy()

    def configure(self, cnf: (dict, str)=None, **kwargs):
        """Configure widget options"""
        if cnf is not None:
            if isinstance(cnf, dict):
                kwargs.update(cnf)
            elif isinstance(cnf, str):
                return self.cget(cnf)
        for key, value in kwargs.items():
            if key == "scrollbar":
                self._config_scroll(value)
                continue
            attr = "_{}".format(key)
            if hasattr(self, attr):
                setattr(self, attr, value)
                if key not in self._CUSTOM:
                    continue
            tk.Canvas.configure(self, **{key: value})

    def config(self, cnf: (dict, str) = None, **kwargs):
        """Configure alias for tk.Widget"""
        return self.configure(cnf, **kwargs)

    def cget(self, key: str):
        """Return the value for a given option"""
        attr = "_{}".format(key)
        if hasattr(self, attr):
            return getattr(self, attr)
        return tk.Canvas.cget(self, key)

    @staticmethod
    def format_time(d: datetime) -> str:
        """Format time relatively if necessary"""
        diff: timedelta = datetime.now() - d
        if diff.days >= 7:
            return d.strftime("%-d %B, %Y")
        elif 0 < diff.days < 7:
            return humanize.naturalday(d).capitalize()
        elif diff.seconds > 60:
            return humanize.naturaltime(d).capitalize()
        else:
            return "A few seconds ago"


if __name__ == '__main__':
    from ttkthemes import ThemedTk
    w = ThemedTk(theme="clearlooks", gif_override=True)
    c = ChatWindow(w)
    for i in range(120):
        author = "Author {}".format(i % 2)
        colour = "tomato" if i % 2 else "lightyellow"
        args = datetime.now() - timedelta(minutes=i), author, "Message {}: {}".format(i, i * "abcde"), colour
        c.create_message(*args, redraw=False)
    c.redraw_messages()
    s = ttk.Scrollbar(w)
    c.configure(scrollbar=s)
    c.grid(row=0, column=0, sticky="nswe")
    s.grid(row=0, column=1, sticky="nswe")

    w.mainloop()
