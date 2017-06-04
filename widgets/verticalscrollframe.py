# This file contains utility code NOT written by RedFantom or Daethyra, though it may have been edited to suit a
# particular purpose better. This code was written by others. For the credits, see the block-comment in each class.
# This file is excluded from the copyright of RedFantom, Daethyra and Sprigellania, but the code in this file
# IS redistributed under the license found in LICENSE, so you only have to accept one License when using the
# software.
import tkinter.ttk as ttk

import tkinter as tk

import platform


# Vertically scrollable frame with built-in scrollbar
# Widgets should be placed in instance.interior!
class VerticalScrollFrame(ttk.Frame):
    """
    This code is based on:
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    mtTkinter Wiki
    Author: Not listed
    License: Not listed

    Edited by RedFantom for ttk and normal import, and size
    """

    def __init__(self, parent, canvaswidth=780, canvasheight=395, **kw):
        ttk.Frame.__init__(self, parent, **kw)
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=2)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, width=canvaswidth,
                           height=canvasheight)
        canvas.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        vscrollbar.config(command=canvas.yview)

        def mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 100)), "units")

        canvas.bind("<MouseWheel>", mousewheel)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        def _configure_interior(event):
            if interior.winfo_reqwidth() == canvaswidth and interior.winfo_reqheight() == canvasheight:
                return
            canvas.config(scrollregion=canvas.bbox("all"))
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)
        ScrollingArea(parent).add_scrolling(canvas, yscrollbar=vscrollbar)


# Cross-platform scrollable area class
class ScrollingArea(object):
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
            root.bind_all('<4>', self.on_mouse_wheel, add='+')
            root.bind_all('<5>', self.on_mouse_wheel, add='+')
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self.on_mouse_wheel, add='+')

    def on_mouse_wheel(self, event):
        if self.activeArea:
            self.activeArea.on_mouse_wheel(event)

    def mouse_wheel_bind(self, widget):
        self.activeArea = widget

    def mouse_wheel_unbind(self):
        self.activeArea = None

    def build_function_on_mouse_wheel(self, widget, orient, factor=1):
        view_command = getattr(widget, orient + 'view')
        if self.OS == 'Linux':
            def on_mouse_wheel(event):
                if event.num == 4:
                    view_command("scroll", (-1) * factor, "units")
                elif event.num == 5:
                    view_command("scroll", factor, "units")
        elif self.OS == 'Windows':
            def on_mouse_wheel(event):
                view_command("scroll", (-1) * int((event.delta / 120) * factor), "units")
        elif self.OS == 'Darwin':
            def on_mouse_wheel(event):
                view_command("scroll", event.delta, "units")
        else:
            raise ValueError("Using a not recognized OS")
        return on_mouse_wheel

    def add_scrolling(self, scrolling_area, xscrollbar=None, yscrollbar=None):
        if yscrollbar:
            scrolling_area.configure(xscrollcommand=yscrollbar.set)
            yscrollbar['command'] = scrolling_area.yview
        if xscrollbar:
            scrolling_area.configure(yscrollcommand=xscrollbar.set)
            xscrollbar['command'] = scrolling_area.xview
        scrolling_area.bind('<Enter>', lambda event: self.mouse_wheel_bind(scrolling_area))
        scrolling_area.bind('<Leave>', lambda event: self.mouse_wheel_unbind())
        if xscrollbar and not hasattr(xscrollbar, 'onMouseWheel'):
            xscrollbar.on_mouse_wheel = self.build_function_on_mouse_wheel(scrolling_area, 'x', self.factor)
        if yscrollbar and not hasattr(yscrollbar, 'onMouseWheel'):
            yscrollbar.on_mouse_wheel = self.build_function_on_mouse_wheel(scrolling_area, 'y', self.factor)
        main_scrollbar = yscrollbar or xscrollbar
        if main_scrollbar:
            scrolling_area.on_mouse_wheel = main_scrollbar.on_mouse_wheel
        for scrollbar in (xscrollbar, yscrollbar):
            if scrollbar:
                scrollbar.bind('<Enter>', lambda event, scrollbar=scrollbar: self.mouse_wheel_bind(scrollbar))
                scrollbar.bind('<Leave>', lambda event: self.mouse_wheel_unbind())
