# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Written by Daethyra, edited by RedFantom

"""
Real-time log files watcher supporting log rotation.
Works with Python >= 2.6 and >= 3.2, on both POSIX and Windows.

Credits to:
Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT
GitHub: https://github.com/giampaolo
"""

import os
import errno
import time
import stat
import datetime
import variables
import threading
import tkMessageBox


# ===================================================================
# --- Stalker Wrapper
# ===================================================================
class LogStalker(threading.Thread):
    """Looks for changes in all watched files in a directory.
    This is useful for watching log file changes in real-time

    Example:

    >>> def callback(filename, lines):
    ...     print(filename, lines)
    ...
    >>> lw = LogStalker("/var/log/", callback)
    >>> lw.loop()  # blocking
    >>> while 1:  # non-blocking
    ...    lw.loop(blocking=False)
    ...    time.sleep(0.1)
    ...
    >>>
    """

    def __init__(self, callback, folder=variables.path, extensions=["txt"], tail_lines=0, sizehint=1048576):
        """

        :param folder: (str), folder to watch
        :param callback: (callable), function which is called every time one of the file being
            watched is updated, is called with 'filename' and 'lines' arguments
        :param extensions: (list), only watch files with these extension
        :param tail_lines: (int), read last N lines from files being watched before starting
        :param sizehint: (int), passed to file.readlines(), represents an approximation of the
            maximum number of bytes to read from a file on every iteration (as opposed to load the
            entire file in memory until EOF is reached). Default to 1MB
        """
        # self.folder = os.path.realpath(folder)
        threading.Thread.__init__(self)
        self.FLAG = True
        self.folder = folder.replace("\n", "")
        self.extensions = extensions
        self._files_map = {}
        self._callback = callback
        self._sizehint = sizehint

        # assert os.path.isdir(self.folder), self.folder
        assert callable(callback), repr(callback)

        self.update_files()

        for id, file in self._files_map.items():
            file.seek(os.path.getsize(file.name))  # EOF
            if tail_lines:
                try:
                    lines = self.tail(file.name, tail_lines)
                except IOError as err:
                    if err.errno != errno.ENOENT:
                        raise
                else:
                    if lines:
                        self._callback(file.name, lines)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def run(self, interval=0.1, blocking=True):
        """Start a busy loop checking for file changes every'interval' seconds.
        If 'blocking' is False make one loop and then return.
        """
        while self.FLAG:
            if not variables.FLAG:
                print "[DEBUG] Closing because of vars.FLAG"
                self.close()
                return
            self.update_files()
            for fid, file in list(self._files_map.items()):
                self.readlines(file)

            if not blocking:
                return
            if not variables.FLAG:
                self.close()
                return
            time.sleep(interval)

    def log(self, line):
        print(datetime.datetime.now().strftime("%H:%M:%S"), ":", line)

    def listdir(self):
        """List directory and filter files by extension.
        You may want to override this to add extra logic or globbing support.
        """
        ls = os.listdir(self.folder)
        if self.extensions:
            return [x for x in ls if os.path.splitext(x)[1][1:] in self.extensions]
        else:
            return ls

    @classmethod
    def open(cls, file):
        """
        Wrapper around open().
        By default files are opened in binary mode and readlines()
        will return bytes on both Python 2 and 3.
        This means callback() will deal wirh a list of bytes.
        Can be overridden in order to deal with unicode strings
        instead, like this:

          import codecs, locale
          return codecs.open(file, 'r', encoding=locale.getpreferredencoding(),
                             errors='ignore')
        """
        return open(file, 'rb')

    @classmethod
    def tail(cls, fname, window):
        """Read last N lines from file fname."""
        if window <= 0:
            raise ValueError('invalid window value %r' % window)
        with cls.open(fname) as f:
            BUFSIZ = 1024
            encoded = getattr(f, 'encoding', False)
            CR = '\n' if encoded else b'\n'
            data = '' if encoded else b''
            f.seek(0, os.SEEK_END)
            fsize = f.tell()
            block = -1
            exit = False
            while not exit:
                step = (block * BUFSIZ)
                if abs(step) >= fsize:
                    f.seek(0)
                    newdata = f.read(BUFSIZ - (abs(step) - fsize))
                    exit = True
                else:
                    f.seek(step, os.SEEK_END)
                    newdata = f.read(BUFSIZ)
                data = newdata + data
                if data.count(CR) >= window:
                    break
                else:
                    block -= 1
            return data.splitlines()[-window:]

    def update_files(self):
        ls = []
        for name in self.listdir():
            absname = os.path.realpath(os.path.join(self.folder, name))
            try:
                st = os.stat(absname)
            except EnvironmentError as err:
                if err.errno != errno.ENOENT:
                    raise
            else:
                if not stat.S_ISREG(st.st_mode):
                    continue
                fid = self.get_file_id(st)
                ls.append((fid, absname))

        # check existent files
        for fid, file in list(self._files_map.items()):
            try:
                st = os.stat(file.name)
            except EnvironmentError as err:
                if err.errno == errno.ENOENT:
                    self.unwatch(file, fid)
                else:
                    raise
            else:
                if fid != self.get_file_id(st):
                    # same name but different file (rotation); relaod it.
                    self.unwatch(file, fid)
                    self.watch(file.name)
        # add new ones
        for fid, fname in ls:
            if fid not in self._files_map:
                self.watch(fname)

    def readlines(self, file):
        """
        Read file lines since last access until EOF is reached and
        incove callback.
        """
        while True:
            lines = file.readlines(self._sizehint)
            if not lines:
                break
            self._callback(lines)

    def watch(self, fname):
        try:
            file = self.open(fname)
            fid = self.get_file_id(os.stat(fname))
        except IOError:
            tkMessageBox.showerror("Error",
                                   "The real-time parsing process encountered a known bug. Please restart the GSF Parser.")
            variables.main_window.destroy()
        except EnvironmentError as err:
            if err.errno != errno.ENOENT:
                raise
        else:
            self.log("watching logfile %s" % fname)
            self._files_map[fid] = file
            if len(self._files_map) > 500:
                self.log("You have %d log files. You should think about makeing some cleaning." % len(self._files_map))

    def unwatch(self, file, fid):
        # File no longer exists. If it has been renamed try to read it
        # for the last time in case we're dealing with a rotating log
        # file.
        self.log("un-watching logfine %s" % file.name)
        del self._files_map[fid]
        with file:
            lines = self.readlines(file)
            if lines:
                self._callback(file.name, lines)

    @staticmethod
    def get_file_id(st):
        if os.name == 'posix':
            return "%xg%x" % (st.st_dev, st.st_ino)
        else:
            return "%f" % st.st_ctime

    def close(self):
        for id, file in self._files_map.items():
            file.close()
        self._files_map.clear()
