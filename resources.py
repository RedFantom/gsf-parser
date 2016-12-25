# This file contains utility code NOT written by RedFantom or Daethyra, though it may have been edited to suit a particular purpose better
# This code was written by others. For the credits, see the block-comment in each class. This file is excluded from the copyright of RedFantom
# and Daethyra, but the code in this file IS redistributed under the license found in LICENSE.
import ttk
import Tkinter as tk
import platform

# Vertically scrollable frame with built-in scrollbar
# Widgets should be placed in instance.interior!
class vertical_scroll_frame(ttk.Frame):
    """
    This code is based on:
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    Tkinter Wiki
    Author: Not listed
    License: Not listed

    Edited by RedFantom for ttk and normal import
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, width = 780, height = 395)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)
        def mousewheel(event):
            print "[DEBUG] Being scrolled"
            canvas.yview_scroll(-1*(event.delta / 100), "units")
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