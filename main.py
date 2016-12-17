# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import gui
import sys
import tkMessageBox
import settings

set_obj = settings.settings()
set_obj.read_set()

if __name__ == "__main__":
    if sys.platform == "win32":
        main_window = gui.main_window()
    else:
        tkMessageBox.showerror("Fatal error", "Unix is not supported")

def new_window():
    main_window = gui.main_window()