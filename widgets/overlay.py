# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
"""
The contents of this file are based on this excellent StackOverflow answer:
https://stackoverflow.com/questions/21840133/how-to-display-text-on-the-screen-without-a-window-using-python
"""
import win32api as api
import win32con as con
import win32gui as gui
import win32ui as ui
from tkinter import StringVar, Tk
from variables import main_window


class Overlay(object):
    """
    A class that can display text on the screen without ragged edges and with higher performance
    than Tkinter Toplevels can. Also supports clicking through the Text.
    """

    default_font = {
        "family": "Calibri",
        "bold": True,
        "italic": False,
        "size": 12
    }

    def __init__(self, position, text_variable, wait_time=20, font=default_font,
                 master=None, color=(0, 255, 255), opacity=255):
        """
        :param font:
        :param position: Position of the window (x, y)
        :param text_variable: tk.StringVar
        :param wait_time: time in ms for after call
        :param color: color tuple for the text
        """
        # Argument attributes
        self._position = position
        self._text_var = text_variable
        if not isinstance(self._text_var, StringVar):
            raise ValueError("The Overlay class only accepts StringVar objects")
        self._wait_time = wait_time
        self._font_family = font["family"]
        self._font_size = font["size"]
        self._bold = font["bold"]
        self._italic = font["italic"]
        self._master = main_window if not master else master
        self._color = color
        if not isinstance(self._color, tuple) or not len(self._color) == 3:
            raise ValueError("Invalid color tuple passed to Overlay.__init__")
        if not isinstance(self._master, Tk):
            raise ValueError("The Overlay class only accepts Tk objects as master")
        self._opacity = opacity
        # pywin32 interface attributes
        self._h_instance = None
        self._class_name = "GSF Parser Overlay"
        self._window_class = None
        self._window_class_atom = None
        self._ex_style = None
        self._style = None
        self._h_window = None
        self._window = None
        self._after_code = None
        # Start the initialization of the Win32API Text window
        self.initialize_pywin32()
        # Setup the window style
        self.initialize_style()

    def initialize_pywin32(self):
        """
        Initializes a window without borders and transparent background in order to provide an overlay
        throught the win32API (should be higher performance than the Tkinter ones and also provides the option
        to remove ANTIALIASING of the text which results in white around the edges of the text)
        """
        self._h_instance = api.GetModuleHandle()
        self._window_class = gui.WNDCLASS()
        self._window_class.style = con.CS_HREDRAW | con.CS_VREDRAW
        self._window_class.lpfnWndProc = self.draw
        self._window_class.hInstance = self._h_instance
        self._window_class.hCursor = gui.LoadCursor(None, con.IDC_ARROW)
        self._window_class.hbrBackground = gui.GetStockObject(con.WHITE_BRUSH)
        self._window_class.lpszClassName = self._class_name
        self._window_class_atom = gui.RegisterClass(self._window_class)

    def initialize_style(self):
        """
        Initialize the pywin32 styles
        """
        self._ex_style = con.WS_EX_COMPOSITED | con.WS_EX_LAYERED | con.WS_EX_NOACTIVATE | \
                         con.WS_EX_TOPMOST | con.WS_EX_TRANSPARENT
        self._style = con.WS_DISABLED | con.WS_POPUP | con.WS_VISIBLE

    def initialize_window(self):
        """
        Initialize the actual window
        """
        # Initialize the window object
        self._window = gui.CreateWindowEx(
            self._ex_style,  # External style
            self._window_class_atom,  # Window class
            "GSF Parser Overlay",  # Window title
            self._style,  # Window style
            self._position[0],  # X coordinate
            self._position[1],  # y coordinate
            api.GetSystemMetrics(con.SM_CXSCREEN),  # Width
            api.GetSystemMetrics(con.SM_CYSCREEN),  # Height
            None,  # Parent window
            None,  # Menu
            self._h_instance,
            None  # lpParam
        )
        # Set white as a transparent color
        gui.SetLayeredWindowAttributes(self._window, 0x00ffffff, 255, con.LWA_COLORKEY | con.LWA_ALPHA)
        # Call an UpdateWindow
        gui.UpdateWindow(self._window)
        # Change the position of the window
        gui.SetWindowPos(
            self._window,  # Window object
            con.HWND_TOPMOST,  # Topmost window handle
            self._position[0],  # x coordinate
            self._position[1],  # y coorinate
            0,  # width (resizes automatically)
            0,  # height (resizes automatically)
            # The does not:
            # - Activate
            # - Move
            # - Resize
            # But it *is* shown
            con.SWP_NOACTIVATE | con.SWP_NOMOVE | con.SWP_NOSIZE | con.SWP_SHOWWINDOW
        )
        # Make sure the window is actually shown
        gui.ShowWindow(self._window, con.SW_SHOW)
        # gui.PumpMessages()
        self.update()

    def draw(self, window, message, w_parameter, l_parameter):
        """
        Callback for the drawing in the window
        """
        if message == con.WM_PAINT:
            hdc, paint_struct = gui.BeginPaint(window)
            dpi_scale = ui.GetDeviceCaps(hdc, con.LOGPIXELSX) / 60.0
            log_font = gui.LOGFONT()
            log_font.lfFaceName = self._font_family
            log_font.lfHeight = int(round(dpi_scale * self._font_size))
            # Remove the antialiasing of the font
            log_font.lfQuality = con.NONANTIALIASED_QUALITY
            log_font.lfWeight = 700 if self._bold is True else 400
            log_font.lfItalic = self._italic
            hard_font = gui.CreateFontIndirect(log_font)
            gui.SelectObject(hdc, hard_font)
            gui.SetTextColor(hdc, eval("0x00{0:02x}{1:02x}{2:02x}".format(
                self._color[0], self._color[1], self._color[2])
            ))
            rectangle = gui.GetClientRect(window)
            gui.DrawText(
                hdc,
                self._text_var.get(),
                -1,
                rectangle,
                con.DT_NOCLIP | con.DT_CENTER | con.DT_WORDBREAK | con.DT_VCENTER
            )
            gui.EndPaint(window, paint_struct)
            return 0

        elif message == con.WM_DESTROY:
            gui.PostQuitMessage(0)
            return 0

        else:
            return gui.DefWindowProc(window, message, w_parameter, l_parameter)

    def update(self):
        gui.UpdateWindow(self._window)
        if self._master:
            self._after_code = self._master.after(self._wait_time, self.update)
        gui.SetLayeredWindowAttributes(self._window, 0x00ffffff, self._opacity, con.LWA_COLORKEY | con.LWA_ALPHA)
        gui.RedrawWindow(self._window, None, None, con.RDW_INVALIDATE | con.RDW_ERASE)
        gui.PumpWaitingMessages()

    def destroy(self):
        """
        Function to send a WM_DESTROY to the window
        """
        if self._after_code is not None:
            self._master.after_cancel(self._after_code)
        gui.SendMessage(self._window, con.WM_CLOSE, None, None)

    def cget(self, key):
        """
        Returns the option for a key
        """
        if key == "position":
            return self._position
        elif key == "wait_time":
            return self._wait_time
        elif key == "text_var":
            return self._text_var
        elif key == "font_family":
            return self._font_family
        elif key == "font_size":
            return self._font_size
        elif key == "master":
            return self._master
        else:
            return None

    def config(self, **kwargs):
        """
        Change the options of the window. Some options cannot be changed.
        """
        self._position = kwargs.pop("position", self._position)
        self._wait_time = kwargs.pop("wait_time", self._wait_time)
        self._font_family = kwargs.pop("font_family", self._font_family)
        self._font_size = kwargs.pop("font_size", self._font_size)
        self._opacity = kwargs.pop("opacity", self._opacity)
        if "master" in kwargs:
            raise RuntimeError("Master widget cannot be changed after window is initialized")
        if "text_var" in kwargs:
            raise RuntimeError("Text variable cannot be changed after window is initialized")
        return True

    def configure(self, **kwargs):
        return self.config(**kwargs)

    def __getitem__(self, item):
        return self.cget(item)

    def __setitem__(self, key, value):
        return self.config(**{key: value})

    @property
    def rectangle(self):
        return gui.GetClientRect(self._window)

    @property
    def position(self):
        rectangle = self.rectangle
        x = rectangle[0]
        y = rectangle[1]
        w = rectangle[2] - x
        h = rectangle[3] - y
        return x, y, w, h

    def __exit__(self):
        self.destroy()


if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    string = StringVar(master=root)
    string.set("Something great")
    overlay = Overlay((-900, 100), string, master=root)

    def change_text():
        string.set("Something else\nEntirely")
        overlay.config(opacity=100)

    overlay.initialize_window()
    root.after(5000, change_text)
    root.after(10000, lambda: overlay.destroy())
    root.mainloop()
