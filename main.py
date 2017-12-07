﻿# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

from os.path import dirname, join, basename, exists
from os import rmdir
import sys
import shutil
import platform
from tkinter import messagebox, filedialog
from tools.utilities import get_temp_directory


def new_window():
    import gui
    try:
        main_window = gui.MainWindow()
    except Exception as e:
        if exists("development"):
            raise
        save = messagebox.askyesno("Error", "The GSF Parser window failed to correctly initialize. Please report this "
                                            "error along with the debug output below.\n\n{}: {}\n\nWould you like to "
                                            "save the debug output to a file?".format(type(e), e))
        if save is True:
            filename = filedialog.asksaveasfilename()
            if filename is None:
                raise ValueError("Invalid filename provided")
            with open(filename, "w") as fo:
                fo.write(e)
        clear = messagebox.askyesno(
            "Question",
            "The GSF Parser can automatically delete all your temporary data. This may solve your issue if it is "
            "caused by incompatibility of an old data file with the expected data in a new one.\n\n"
            "WARNING: This process WILL delete your characters, builds and real-time parsing data if you had any.\n\n"
            "Do you want to attempt the automatic fix?"
        )
        if clear is True:
            try:
                rmdir(get_temp_directory())
            except OSError:
                messagebox.showerror("Error", "Could not automatically delete the temporary files.")
        raise
    main_window.mainloop()


def setup_tkinter():
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
    new_window()
