# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from os.path import dirname, join, basename
import sys
try:
    tcl_lib = join(sys._MEIPASS, "lib")
    tcl_new_lib = join(dirname(dirname(tcl_lib)), basename(tcl_lib))
    import shutil
    shutil.copytree(src=tcl_lib, dst=tcl_new_lib)
except AttributeError:
    pass
import gui


def new_window():
    main_window = gui.MainWindow()
    main_window.mainloop()


if __name__ == "__main__":
    new_window()
