"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from sys import platform
import psutil
import subprocess
import re


def get_window_location(process="swtor.exe"):
    """
    Return box coordinates to the SWTOR window by using the appropriate
    Window manager library for the given platform.
    :param process: Name of the process
    :return: (x, y, x + width, y + height)
    """
    return Window(name=process).get_rectangle()


class Window(object):
    """
    Class to provide a universal interface to the window manager
    interface libraries of Windows and Linux to allow retrieving of
    window rectangles.
    """

    ERRORS = [
        "no such file",
        "not installed",
        "error",
    ]

    WIN32 = "win32"
    LINUX = "linux"

    def __init__(self, name: str = None, pid: int = None, pids: list=None):
        """
        :param name: Full process name
        :param pid: Process ID number
        :param pids: List of Process ID numbers
        Either of these *must* be provided.
        """
        if name is not None:
            pids = self.get_pid_for_name(name)
        if pid is not None:
            pids = [pid, ]
        if pids is None:
            raise ValueError("Invalid arguments received")
        self._pids = pids
        self._w_handles = self.get_window_handles(self._pids)

    def get_rectangle(self, index=0):
        """Return the rectangle coordinates"""
        handle = self.handles[index]
        print("[Window] Window handle:", handle)
        if platform == Window.WIN32:
            coords = self.get_rectangle_win32(handle)
        elif platform == Window.LINUX:
            coords = self.get_rectangle_linux(handle)
        else:
            raise NotImplementedError()
        print("[Window] Coordinates of window:", coords)
        return coords

    @staticmethod
    def get_rectangle_win32(handle: (int, str)):
        """Return the rectangle coordinates for a given window handle"""
        import win32gui as gui
        return list(map(int, gui.GetWindowRect(handle)))

    @staticmethod
    def get_rectangle_linux(handle: (int, str)):
        """Return the rectangle coordinates for a given window handle"""
        out, err = Window.execute("xdotool", "getwindowgeometry", handle)
        position = re.search(r"Position: (\d*,\d*)", out)
        size = re.search(r"Geometry: (.*)", out)
        if position is None or size is None:
            return None
        x, y = map(int, position.group(1).split(","))
        w, h = map(int, position.group(1).split(","))
        return [x, y, x+w, y+h]

    @staticmethod
    def get_window_handles(pids: list):
        """Return the window handles for a given process ID"""
        if platform == Window.WIN32:
            return Window.get_window_handles_win32(pids)
        elif platform == Window.LINUX:
            return Window.get_window_handles_linux(pids)
        raise NotImplementedError()

    @staticmethod
    def get_window_handles_linux(pids: list):
        """Return the window handles for a given process ID"""
        out, err = Window.execute("xprop", "-root")
        match = re.search(r"_NET_CLIENT_LIST_STACKING\(WINDOW\): window id # (.*)", out)
        if match is None:
            return None
        windows = match.group(1).split(", ")
        handles = list()
        for win in windows:
            out, err = Window.execute("xdotool", "getwindowpid", win)
            process_id = int(out) if out != "" else 0
            if process_id in pids:
                print("[Window] SWTOR PID:", process_id)
                handles.append(win)
        return handles

    @staticmethod
    def get_window_handles_win32(pids: list):
        """Return the window handles for a given process ID"""
        import win32gui as gui
        import win32process as process

        handles = list()

        def callback(window_handle, _):
            if not (gui.IsWindowVisible(window_handle) and gui.IsWindowEnabled(window_handle)):
                return
            _, found_pid = process.GetWindowThreadProcessId(window_handle)
            if found_pid in pids:
                handles.append(window_handle)

        gui.EnumWindows(callback, None)
        return handles

    @staticmethod
    def get_pid_for_name(name: str):
        """Return the PID number for a given process name"""
        pids = list()
        for process in psutil.process_iter():
            if process.name() == name:
                pids.append(process.pid)
        if len(pids) == 0:
            return None
        return pids

    @staticmethod
    def execute(*args):
        """Execute a command and return output as str"""
        proc = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        out, err = proc.stdout.read().decode(), proc.stderr.read().decode()
        for buff in (out, err):
            if Window.check_errors(buff):
                raise RuntimeError("Failed to execute command: {}".format(list(args)))
        return out, err

    @staticmethod
    def check_errors(buffer: str):
        """Check for errors in executing the command"""
        buffer = buffer.lower()
        for error in Window.ERRORS:
            if error in buffer:
                return True
        return False

    @property
    def pids(self):
        return self._pids

    @property
    def handles(self):
        return self._w_handles
