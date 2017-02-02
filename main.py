# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import os
import sys
import firstrun
import gui
import tkMessageBox
import settings

def new_window():
    main_window = gui.main_window()

if __name__ == "__main__":
    if sys.platform == "win32":
        # oob = firstrun.Oob_window()
        # oob.mainloop()
        import variables
        if variables.set_obj.version != "v2.2.1":
            print "[DEBUG] OOB not completed successfully, exiting..."
        main_window = gui.main_window()
    else:
        tkMessageBox.showerror("Fatal error", "Unix is not supported")
