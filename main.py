"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from tkinter import messagebox, filedialog
from os.path import dirname, join, basename, exists
import sys
import shutil
import platform


def create_window():
    """
    Attempt to create a new MainWindow and provide error handling and
    user interaction for when an error occurs which causes the
    window creation to fail.
    """
    import gui
    try:
        main_window = gui.MainWindow()
    except Exception as e:
        if exists("development"):
            raise
        save = messagebox.askyesno(
            "Error", "The GSF Parser window failed to correctly initialize. Please report this "
                     "error along with the debug output below.\n\n{}\n\nWould you like to "
                     "save the debug output to a file?".format(repr(e), e))
        if save is True:
            filename = filedialog.asksaveasfilename()
            if filename is None:
                raise ValueError("Invalid filename provided")
            with open(filename, "w") as fo:
                fo.write(repr(e))
        raise
    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        exit(0)


def setup_tkinter():
    """Fixes bug in PyInstaller, see issue #17"""
    if "Windows-7" not in platform.platform():
        return
    try:
        tcl_lib = join(sys._MEIPASS, "lib")
        tcl_new_lib = join(dirname(dirname(tcl_lib)), basename(tcl_lib))
        shutil.copytree(src=tcl_lib, dst=tcl_new_lib)
    except (AttributeError, FileNotFoundError, FileExistsError):
        pass
    return


if __name__ == '__main__':
    setup_tkinter()
    create_window()
