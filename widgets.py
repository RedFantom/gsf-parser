# This file contains utility code NOT written by RedFantom or Daethyra, though it may have been edited to suit a
# particular purpose better. This code was written by others. For the credits, see the block-comment in each class.
# This file is excluded from the copyright of RedFantom, Daethyra and Sprigellania, but the code in this file
# IS redistributed under the license found in LICENSE, so you only have to accept one License when using the
# software.
import ttk

try:
    import mtTkinter as tk
except ImportError:
    import Tkinter as tk
import platform
import calendar
import tkFont
import re
from PIL import Image, ImageTk
import os


# Vertically scrollable frame with built-in scrollbar
# Widgets should be placed in instance.interior!
class vertical_scroll_frame(ttk.Frame):
    """
    This code is based on:
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    mtTkinter Wiki
    Author: Not listed
    License: Not listed

    Edited by RedFantom for ttk and normal import, and size
    """

    def __init__(self, parent, canvaswidth=780, canvasheight=395, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, width=canvaswidth,
                           height=canvasheight)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        def mousewheel(event):
            print "[DEBUG] Being scrolled"
            canvas.yview_scroll(-1 * (event.delta / 100), "units")

        canvas.bind("<MouseWheel>", mousewheel)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)
        scrolling_area(parent).add_scrolling(canvas, yscrollbar=vscrollbar)


# Cross-platform scrollable area class
class scrolling_area(object):
    """
    Credits to: Miguel martinez Lopez
    Link: http://code.activestate.com/recipes/578894-mousewheel-binding-to-scrolling-area-tkinter-multi/
    License: MIT License

    Edited by RedFantom:
    - Removed whitespaces
    - Added platform error
    """
    OS = platform.system()

    def __init__(self, root, factor=2):
        self.activeArea = None
        if type(factor) == int:
            self.factor = factor
        else:
            raise Exception("Factor must be an integer.")
        if self.OS == "Linux":
            root.bind_all('<4>', self.onMouseWheel, add='+')
            root.bind_all('<5>', self.onMouseWheel, add='+')
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self.onMouseWheel, add='+')

    def onMouseWheel(self, event):
        if self.activeArea:
            self.activeArea.onMouseWheel(event)

    def mouseWheel_bind(self, widget):
        self.activeArea = widget

    def mouseWheel_unbind(self):
        self.activeArea = None

    def build_function_onMouseWheel(self, widget, orient, factor=1):
        view_command = getattr(widget, orient + 'view')
        if self.OS == 'Linux':
            def onMouseWheel(event):
                if event.num == 4:
                    view_command("scroll", (-1) * factor, "units")
                elif event.num == 5:
                    view_command("scroll", factor, "units")
        elif self.OS == 'Windows':
            def onMouseWheel(event):
                view_command("scroll", (-1) * int((event.delta / 120) * factor), "units")
        elif self.OS == 'Darwin':
            def onMouseWheel(event):
                view_command("scroll", event.delta, "units")
        else:
            raise ValueError("Using a not recognized OS")
        return onMouseWheel

    def add_scrolling(self, scrollingArea, xscrollbar=None, yscrollbar=None):
        if yscrollbar:
            scrollingArea.configure(xscrollcommand=yscrollbar.set)
            yscrollbar['command'] = scrollingArea.yview
        if xscrollbar:
            scrollingArea.configure(yscrollcommand=xscrollbar.set)
            xscrollbar['command'] = scrollingArea.xview
        scrollingArea.bind('<Enter>', lambda event: self.mouseWheel_bind(scrollingArea))
        scrollingArea.bind('<Leave>', lambda event: self.mouseWheel_unbind())
        if xscrollbar and not hasattr(xscrollbar, 'onMouseWheel'):
            xscrollbar.onMouseWheel = self.build_function_onMouseWheel(scrollingArea, 'x', self.factor)
        if yscrollbar and not hasattr(yscrollbar, 'onMouseWheel'):
            yscrollbar.onMouseWheel = self.build_function_onMouseWheel(scrollingArea, 'y', self.factor)
        main_scrollbar = yscrollbar or xscrollbar
        if main_scrollbar:
            scrollingArea.onMouseWheel = main_scrollbar.onMouseWheel
        for scrollbar in (xscrollbar, yscrollbar):
            if scrollbar:
                scrollbar.bind('<Enter>', lambda event, scrollbar=scrollbar: self.mouseWheel_bind(scrollbar))
                scrollbar.bind('<Leave>', lambda event: self.mouseWheel_unbind())


class Calendar(ttk.Frame):
    """
    ttk Widget that enables a calender within a frame, allowing the user to select dates.
    Credits to: The Python team
    Source: The Python/ttk samples
    License: The Python GPL-compatible license
    """

    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, **kw):
        """
        WIDGET-SPECIFIC OPTIONS
            locale, firstweekday, year, month, selectbackground,
            selectforeground
        """
        # remove custom options from kw before initializating ttk.Frame
        fwday = kw.pop('firstweekday', calendar.MONDAY)
        year = kw.pop('year', self.datetime.now().year)
        month = kw.pop('month', self.datetime.now().month)
        locale = kw.pop('locale', None)
        sel_bg = kw.pop('selectbackground', '#ecffc4')
        sel_fg = kw.pop('selectforeground', '#05640e')

        self._date = self.datetime(year, month, 1)
        self._selection = None  # no date selected

        ttk.Frame.__init__(self, master, **kw)

        self._cal = self.get_calendar(locale, fwday)

        # self.__setup_styles()       # creates custom styles
        self.__place_widgets()  # pack/grid used widgets
        self.__config_calendar()  # adjust calendar columns and setup tags
        # configure a canvas, and proper bindings, for selecting dates
        self.__setup_selection(sel_bg, sel_fg)

        # store items ids, used for insertion later
        self._items = [self._calendar.insert('', 'end', values='')
                       for _ in range(6)]
        # insert dates in the currently empty calendar
        self._build_calendar()

        # set the minimal size for the widget
        self._calendar.bind('<Map>', self.__minsize)

    def __setitem__(self, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            ttk.Frame.__setitem__(self, item, value)

    def __getitem__(self, item):
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    '''
    def __setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))
    '''

    def __place_widgets(self):
        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn_img = Image.open(os.path.dirname(__file__) + "\\assets\\gui\\left.png")
        rbtn_img = Image.open(os.path.dirname(__file__) + "\\assets\\gui\\right.png")
        lbtn_tkimg = ImageTk.PhotoImage(lbtn_img)
        rbtn_tkimg = ImageTk.PhotoImage(rbtn_img)
        lbtn = ttk.Button(hframe, command=self._prev_month, image=lbtn_tkimg)
        rbtn = ttk.Button(hframe, command=self._next_month, image=rbtn_tkimg)
        self._header = ttk.Label(hframe, width=15, anchor='center')
        # the calendar
        self._calendar = ttk.Treeview(hframe, show='', selectmode='none', height=7)

        # pack the widgets
        hframe.pack(side='top', pady=4, anchor='center')
        lbtn.grid()
        self._header.grid(column=1, row=0, padx=12)
        rbtn.grid(column=2, row=0)
        self._calendar.pack(expand=1, fill='both', side='bottom')

    def __config_calendar(self):
        cols = self._cal.formatweekheader(3).split()
        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background='grey90')
        self._calendar.insert('', 'end', values=cols, tag='header')
        # adjust its columns width
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                                  anchor='e')

    def __setup_selection(self, sel_bg, sel_fg):
        self._font = tkFont.Font()
        self._canvas = canvas = tk.Canvas(self._calendar,
                                          background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')

        canvas.bind('<ButtonPress-1>', lambda evt: canvas.place_forget())
        self._calendar.bind('<Configure>', lambda evt: canvas.place_forget())
        self._calendar.bind('<ButtonPress-1>', self._pressed)

    def __minsize(self, evt):
        width, height = self._calendar.master.geometry().split('x')
        height = height[:height.index('+')]
        self._calendar.master.minsize(width, height)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month

        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        self._header['text'] = header.title()

        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_selection(self, text, bbox):
        """Configure canvas for a new selection."""
        x, y, width, height = bbox

        textw = self._font.measure(text)

        canvas = self._canvas
        canvas.configure(width=width, height=height)
        canvas.coords(canvas.text, width - textw, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)

    # Callbacks

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or not item in self._items:
            # clicked in the weekdays row or just outside the columns
            return

        item_values = widget.item(item)['values']
        if not len(item_values):  # row is empty for this month
            return

        text = item_values[int(column[1]) - 1]
        if not text:  # date is empty
            return

        bbox = widget.bbox(item, column)
        if not bbox:  # calendar not visible yet
            return

        # update and then show selection
        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_selection(text, bbox)

    def _prev_month(self):
        """Updated calendar to show the previous month."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()  # reconstuct calendar

    def _next_month(self):
        """Update calendar to show the next month."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()  # reconstruct calendar

    @staticmethod
    def get_calendar(locale, fwday):
        """
        Function required by the Calender widget class
        :param locale:
        :param fwday:
        :return:
        """
        # instantiate proper calendar class
        if locale is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale)

    @property
    def selection(self):
        """Return a datetime representing the current selected date."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        return self.datetime(year, month, int(self._selection[0]))


class ToggledFrame(ttk.Frame):
    """
    A frame with a toggle button to show or hide the contents. Edited by RedFantom for image support instead of a '+'
    or '-'.
    Author: Onlyjus
    License: None
    Source: http://stackoverflow.com/questions/13141259/expandable-and-contracting-frame-in-tkinter
    """

    def __init__(self, parent, text="", *args, **options):
        ttk.Frame.__init__(self, parent, *args, **options)
        self.show = tk.IntVar()
        self.show.set(0)
        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)
        closed_img = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\assets\\gui\\closed.png")
        self.closed = ImageTk.PhotoImage(closed_img)
        open_img = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\assets\\gui\\open.png")
        self.open = ImageTk.PhotoImage(open_img)
        ttk.Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)
        self.toggle_button = ttk.Checkbutton(self.title_frame, width=4, image=self.closed,
                                             command=self.toggle, variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="left")
        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(image=self.open)
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(image=self.closed)


class HoverInfo(tk.Menu):
    """"
    A simple class that provides an info box when hovering over a Tkinter widget
    Author: Jakirk Patrick
    License: None
    Source: https://jakirkpatrick.wordpress.com/2012/02/01/making-a-hovering-box-in-tkinter/

    Edited by RedFantom: Removed comparisons to None
    """

    def __init__(self, parent, text, command=None):
        self._com = command
        tk.Menu.__init__(self, parent, tearoff=0)
        if not isinstance(text, str):
            raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
        toktext = re.split('\n', text)
        for t in toktext:
            self.add_command(label=t)
        self._displayed = False
        self.master.bind("<Enter>", self.Display)
        self.master.bind("<Leave>", self.Remove)

    def __del__(self):
        self.master.unbind("<Enter>")
        self.master.unbind("<Leave>")

    def Display(self, event):
        if not self._displayed:
            self._displayed = True
            self.post(event.x_root, event.y_root)
        if not self._com:
            self.master.unbind_all("<Return>")
            self.master.bind_all("<Return>", self.Click)

    def Remove(self, event):
        if self._displayed:
            self._displayed = False
            self.unpost()
        if not self._com:
            self.unbind_all("<Return>")

    def Click(self, event):
        self._com()
