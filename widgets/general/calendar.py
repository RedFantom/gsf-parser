"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom

Loosely based on the Calendar Widget created by the Python Team. That
widget is available in the ttkwidgets package. It is licensed under the
GPL compatible Python License. This widget is available only under the
GNU GPLv3.
"""
# Standard Library
import calendar
from colorsys import rgb_to_hsv, hsv_to_rgb
from datetime import datetime
import locale
from typing import Any, Dict, List, Tuple
# UI Libraries
import tkinter as tk
from tkinter import ttk
# Project Modules
from utils import open_icon


def hex_to_rgb(string: str) -> Tuple[int, int, int]:
    """Convert a hex color to an RGB color tuple"""
    string = string.strip("#")
    r, g, b = tuple(string[i:i+2] for i in range(0, len(string), 2) if string != "")
    r, g, b = map(lambda v: int(v, base=16), (r, g, b))
    return r, g, b


class DateKeyDict(dict):
    """Special dictionary with only datetimes as keys ignoring dates"""

    def __getitem__(self, key: datetime) -> Any:
        """Match the key to one of the keys in the dictionary"""
        return dict.__getitem__(self, self._match_key(key))

    def __setitem__(self, key: datetime, value: Any) -> None:
        """Set a value in the dictionary ignoring time of datetime"""
        dict.__setitem__(self, self._match_key(key), value)

    def _match_key(self, item: datetime) -> datetime:
        """Match the key without the time of the datetime"""
        for key in self.keys():
            if key.date() == item.date():
                return key
        return item  # Create new key

    def __contains__(self, item: datetime) -> bool:
        """Determine whether this dictionary contains the key"""
        for key in self.keys():
            if key.date() == item.date():
                return True
        return False

    def update(self, other: Dict[datetime, int]) -> Dict[datetime, int]:
        """Update safely with the values from another dictionary"""
        for key, value in other.items():
            self[key] = value
        return self


class Calendar(ttk.Frame):
    """
    Calendar Widget supporting higlighted dates

    The highlights act as a heatmap. For each date, a number of events
    can be set. The dates with the maximum number of events get the
    maximum highlight color, other events get a less bright colour.
    """

    OPTIONS = [
        "width",
        "height",
        "firstweekday",
        "year",
        "month",
        "selectbg",
        "selectfg",
        "higlight",
    ]

    DAYS = {
        calendar.SUNDAY: "Su",
        calendar.MONDAY: "Mo",
        calendar.TUESDAY: "Tu",
        calendar.WEDNESDAY: "We",
        calendar.THURSDAY: "Th",
        calendar.FRIDAY: "Fr",
        calendar.SATURDAY: "Sa"
    }

    ORDER = [
        calendar.MONDAY,
        calendar.TUESDAY,
        calendar.WEDNESDAY,
        calendar.THURSDAY,
        calendar.FRIDAY,
        calendar.SATURDAY,
        calendar.SUNDAY,
    ]

    def __init__(self, master=None, **kwargs):
        """
        :param master: Master widget
        :param kwargs: Special widget options

        width, height: Width and height in pixels applied to the Canvas
            and Frame widgets
        year, month: Year and month to initialize the widget with
        selectbg, selectfg: Colours to apply to the selected item in
            the calendar widget
        highlight: Highlight colour to apply in the heatmap
        callback: Callback to call upon date selection
        """
        self._width, self._height = kwargs.pop("width", 200), kwargs.pop("height", 200)
        now: datetime = datetime.now()
        self._year, self._month = kwargs.pop("year", now.year), kwargs.pop("month", now.month)
        self._selectbg = kwargs.pop("selectbg", "#1c3a6b")
        self._selectfg = kwargs.pop("selectfg", "#ffffff")
        self._highlight = kwargs.pop("highlight", "#ff0000")
        self._callback = kwargs.pop("callback", None)

        self.master: tk.BaseWidget = master
        self._date: datetime = datetime(self._year, self._month, 1)
        self._selection: datetime = None
        self._frame: ttk.Frame = None

        ttk.Frame.__init__(self, master, **kwargs)

        self._calendar = calendar.TextCalendar()

        self._image_next, self._image_prev = map(
            lambda i: open_icon(i, folder="gui"), ("right.png", "left.png"))
        ttk.Style(self).configure("Cal.Toolbutton", anchor=tk.CENTER)
        self._button_next = ttk.Button(
            self, command=self.next_month, image=self._image_next, style="Cal.Toolbutton")
        self._button_prev = ttk.Button(
            self, command=self.prev_month, image=self._image_prev, style="Cal.Toolbutton")

        self._select = tk.BooleanVar(self, value=False)
        ttk.Style(self).configure("Header.Toolbutton", anchor=tk.CENTER)
        self._header = ttk.Checkbutton(
            self, width=15, style="Header.Toolbutton",
            command=self._create_month_selector, variable=self._select)
        self._canvas = tk.Canvas(self, width=200, height=200, background="white")
        self._canvas.bind("<Button-1>", self._on_click)

        self._values: Dict[datetime, int] = DateKeyDict()
        self._markers: Dict[datetime, str] = DateKeyDict()
        self._columns: List[int] = list()
        self._rows: List[int] = list()
        self._numbers: Dict[int, str] = dict()
        self._boxes: Dict[int, str] = dict()

        self.redraw_calendar()
        self.grid_widgets()

    def grid_widgets(self):
        """Configure the widgets in the grid geometry manager"""
        self._button_prev.grid(column=0, row=0, sticky="nswe", padx=5, pady=5)
        self._button_next.grid(column=2, row=0, sticky="nswe", padx=5, pady=5)
        self._header.grid(column=1, row=0, sticky="nswe", pady=5)
        self._canvas.grid(column=0, row=1, columnspan=3, sticky="nswe", padx=5, pady=(0, 5))

    def next_month(self):
        """Move the Calendar widget to the next month"""
        month = self._date.month + 1
        year = self._date.year
        if month is 13:
            month = 1
            year += 1
        self._date = datetime(year=year, month=month, day=1)
        self.redraw_calendar()

    def prev_month(self):
        """Move the Calendar widget to the previous month"""
        month = self._date.month - 1
        year = self._date.year
        if month is 0:
            month = 12
            year -= 1
        self._date = datetime(year=year, month=month, day=1)
        self.redraw_calendar()

    def redraw_calendar(self):
        """Redraw the Calendar Canvas widget"""
        self._canvas.delete(tk.ALL)
        self._columns.clear()
        self._rows.clear()
        self._numbers.clear()
        self._draw_header()
        self._draw_days()

    def _draw_header(self):
        """Draw the day headers"""
        x, y = 7, 0
        for day in self.ORDER:
            self._columns.append(x)
            id = self._canvas.create_text(
                x, 2, text=self.DAYS[day], fill=self._selectfg, anchor=tk.NW, font=("default", 10))
            _, _, x, y = self._canvas.bbox(id)
            x += 7
        self._rows.append(y + 2)
        self._canvas.create_rectangle((0, 0, x, y), fill=self._selectbg, tags=("header",))
        self._canvas.tag_lower("header")
        self._canvas.configure(width=x)
        self._columns.append(x)

    def _draw_days(self):
        """Draw the days in the Canvas"""
        year, month = self._date.year, self._date.month
        self._header.configure(text=self._calendar.formatmonthname(year, month, 0, True).capitalize())
        for i, week in enumerate(self.calendar):
            y = self._rows[i] + 2
            for j, number in enumerate(week):
                x = self._columns[j+1] - 7
                text = str(number) if number is not 0 else ""
                id = self._canvas.create_text(x, y, text=text, anchor=tk.NE, font=("TkDefaultFont", 10))
                self._numbers[number] = id
                _, _, _, y2 = self._canvas.bbox(id)
                self._draw_heatmap_element(id, number, j)
            self._rows.append(y2)
        self._canvas.configure(height=y2 + 2)
        self._canvas.tag_lower("bg")

    def _draw_heatmap_element(self, id: str, number: int, j: int):
        """Draw the heatmap box around a day text"""
        if number is 0:
            return
        x1, y1, x2, y2 = self._canvas.bbox(id)
        date = datetime(year=self._date.year, month=self._date.month, day=number)
        if date not in self._markers:
            value = self._values[date] if date in self._values else 0
            color = self.scale_color_saturation(
                self._highlight, value, max(tuple(self._values.values()) + (1,)))
        else:
            color = self._markers[date]
        id = self._canvas.create_rectangle(
            (self._columns[j] - 3, y1 - 1, x2 + 4, y2 + 1), width=0, fill=color, tags=("bg",))
        self._boxes[number] = id

    def update_heatmap(self, values: Dict[datetime, int]=None, **kwargs):
        """Update the values of each day"""
        if values is not None:
            kwargs.update(values)
        self._values.update(kwargs)
        self.redraw_calendar()

    def update_markers(self, markers: Dict[datetime, str]=None, **kwargs):
        """Update the marker colors that override the heatmap"""
        if markers is not None:
            kwargs.update(markers)
        self._markers.update(kwargs)
        self.redraw_calendar()

    def clear_values(self):
        """Clear all values for the days"""
        self.clear_values()
        self.redraw_calendar()

    def _on_click(self, event: tk.Event):
        """Callback for <Button-1> event: Configure self._selection"""
        x, y = event.x, event.y
        col, row = self.get_table_coords(x, y)
        number = self.calendar[row - 1][col - 1] if row is not None and col is not None else 0
        if number is 0:
            self._selection = None
            return
        year, month = self._date.year, self._date.month
        self._selection = datetime(year=year, month=month, day=number)
        if self.selection is not None and callable(self._callback):
            self._callback(self._selection)
        self.redraw_calendar()
        text, box = self._numbers[number], self._boxes[number]
        self._canvas.itemconfigure(box, fill=self._selectbg)
        self._canvas.itemconfigure(text, fill=self._selectfg)

    def get_table_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Return the row, column for a given xy coordinate"""
        return self.get_table_column(x), self.get_table_row(y)

    def get_table_column(self, x: int) -> int:
        """Return the column index for an x coordinate"""
        for j in range(1, len(self._columns)):
            if self._columns[j - 1] <= x < self._columns[j]:
                return j
        return None

    def get_table_row(self, y: int) -> int:
        """Return the row index for a y coordinate"""
        for i in range(1, len(self._rows)):
            if self._rows[i - 1] <= y < self._rows[i]:
                return i
        return None

    @staticmethod
    def scale_color_saturation(target: str, value: int, maximum: int) -> str:
        """Return a scaled RGB color"""
        r, g, b = hex_to_rgb(target)
        h, s, v = rgb_to_hsv(r, g, b)
        s = max(s * value / maximum, s / 10) if value != 0 else 0
        c: Tuple[int, int, int] = map(int, hsv_to_rgb(h, s, 255))
        return "#{:02x}{:02x}{:02x}".format(*c)

    @property
    def selection(self) -> datetime:
        """Return the selected date in the calendar"""
        return self._selection

    @property
    def calendar(self) -> List[List[int]]:
        """Return a calendar instance"""
        year, month = self._date.year, self._date.month
        calendar: List[List[int]] = self._calendar.monthdayscalendar(year, month)
        if len(calendar) is 5:
            calendar.append([0] * 7)
        return calendar

    def _create_month_selector(self):
        """Show a small window to select the month and year"""
        self._frame = ttk.Frame(self._canvas)
        year, month = tk.IntVar(value=self._date.year), tk.IntVar(value=self._date.month)

        year_menu = ttk.OptionMenu(self._frame, year)
        month_menu = ttk.OptionMenu(self._frame, month)
        year_menu.grid(row=0, column=0)
        month_menu.grid(row=0, column=1)

        for y in range(2013, self._date.year + 1):
            year_menu["menu"].add_command(label=y, command=SetVar(year, y))

        for m in range(1, 13):
            ms = self._calendar.formatmonthname(None, m, 0, False)
            month_menu["menu"].add_command(label=ms, command=SetVar(month, m))

        def update_month():
            self.set_month(year.get(), month.get())
            self._destroy_month_selector()

        ttk.Button(self._frame, text="OK", command=update_month, width=3).grid(row=0, column=2)
        self._header.config(command=self._destroy_month_selector)

        self._frame.update_idletasks()
        x = (self._width - self._frame.winfo_reqwidth()) // 2
        self._frame.place(x=x, y=2, anchor=tk.NW)

        self._select.set(True)

    def _destroy_month_selector(self):
        """Destroy the small month selection window"""
        if self._frame is not None:
            self._frame.destroy()
            self._frame = None
        self._header.config(command=self._create_month_selector)
        self._select.set(False)

    def set_month(self, year: int, month: int):
        """Set the displayed month to the given value"""
        self._date = datetime(year=year, month=month, day=1)
        self.redraw_calendar()


class SetVar(object):
    """Set a predefined value in a variable upon call"""

    def __init__(self, variable: tk.Variable, value: Any):
        """
        :param variable: Variable to set the value for
        :param value: Value to apply to the Variable
        """
        self.variable = variable
        self.value = value

    def __call__(self):
        """Apply the value to the variable"""
        self.variable.set(self.value)


if __name__ == '__main__':
    from ttkthemes import ThemedTk
    w = ThemedTk(theme="arc")
    c = Calendar(w)
    now = datetime.now()
    year, month = now.year, now.month
    c.update_heatmap({datetime(year=year, month=month, day=i): i % 4 for i in range(1, 28)})
    c.grid()
    w.mainloop()
