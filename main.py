# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
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
        # oob = firstrun.oob_window()
        # oob.mainloop()
        import variables

        if variables.settings_obj.version != "v2.2.1":
            print "[DEBUG] OOB not completed successfully, exiting..."
        main_window = gui.main_window()
        main_window.mainloop()
    else:
        tkMessageBox.showerror("Fatal error", "Unix is not supported")
