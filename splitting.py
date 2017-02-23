# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

import parse
import os
import datetime
import tkFileDialog
import tkMessageBox
import Tkinter as tk
import ttk


# Function that returns True if a file contains any GSF events
def check_gsf(file_name):
    """
    This function is copied from `statistics.py` of the GSF Parser
    Written by RedFantom, licensed under GNU GPLv3
    :param file_name:
    :return:
    """
    with open(file_name, "r") as file_obj:
        for line in file_obj:
            if "@" not in line:
                file_obj.close()
                return True
            else:
                continue
    if not file_obj.closed:
        raise
    return False


def split():
    source_folder = tkFileDialog.askdirectory(title="Source folder")
    try:
        os.chdir(source_folder)
    except OSError:
        tkMessageBox.showerror("Error", "Folder not valid!")
        raise SystemExit(1)
    target_folder = tkFileDialog.askdirectory(title="Target folder")
    try:
        os.chdir(target_folder)
    except OSError:
        tkMessageBox.showerror("Error", "Folder not valid!")
        raise SystemExit(1)
    os.chdir(source_folder)
    progress_bar['maximum'] = len(os.listdir(os.getcwd()))
    progress_bar['value'] = 0
    for cl in os.listdir(os.getcwd()):
        # This could be merged into one logic statement,
        # But we don't want to run a non .txt file through check_gsf
        progress_bar['value'] += 1
        main_window.update()
        if not cl.endswith(".txt"):
            continue
        if not check_gsf(cl):
            continue
        with open(cl, "r") as fo:
            lines = fo.readlines()
        player_list = parse.determinePlayer(lines)
        file_cube = parse.splitter(lines, player_list)[0]
        try:
            dt = datetime.datetime.strptime(cl[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%d-%m_%H.%M.%S")
        except ValueError:
            print "File name is not a valid CombatLog string, but contains GSF matches. Running with it."
            dt = cl
        match_count = 0
        for match in file_cube:
            print "Writing a new match."
            with open(target_folder + "\\" + dt + "   Match " + str(match_count) + ".txt", "w", 0) as mo:
                for spawn in match:
                    for event in spawn:
                        mo.write(event)
            match_count += 1
    tkMessageBox.showinfo("Done", "All done separating your matches.")


main_window = tk.Tk()
main_window.wm_title("GSF Splitter")
progress_bar = ttk.Progressbar(main_window, orient=tk.HORIZONTAL, length=300, mode="determinate")
button = ttk.Button(main_window, text="Start", command=split)
button.pack()
progress_bar.pack()
main_window.mainloop()



