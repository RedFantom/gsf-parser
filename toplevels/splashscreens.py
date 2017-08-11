# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.filedialog
import os
from PIL import Image, ImageTk
# Own modules
import variables
from tools import utilities


class SplashScreen(tk.Toplevel):
    def __init__(self, window, amount, title="GSF Parser"):
        tk.Toplevel.__init__(self, window)
        self.window = window
        self.grab_set()
        self.title(title)
        self.label = ttk.Label(self, text="Working...")
        self.label.pack()

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()
        self.progress_bar["maximum"] = amount
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self, number):
        self.progress_bar["value"] = number
        self.update()
        self.window.update()


class BootSplash(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Starting...")
        self.logo = ImageTk.PhotoImage(
            Image.open(os.path.join(utilities.get_assets_directory(),
                                    "logos", "logo_" + variables.settings_obj["gui"]["logo_color"] + ".png")))
        self.panel = ttk.Label(self, image=self.logo)
        self.panel.pack()
        self.window = window
        self.label_var = tk.StringVar()
        self.label_var.set("Connecting to specified server...")
        self.label = ttk.Label(self, textvariable=self.label_var)
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=462, mode="determinate")
        self.progress_bar.pack()
        screen_res = utilities.get_screen_resolution()
        req_size = (self.winfo_reqwidth(), self.winfo_reqheight())
        self.wm_geometry("+{0}+{1}".format(int((screen_res[0] - req_size[0]) / 2),
                                           int((screen_res[1] - req_size[1]) / 2)))
        self.update()
        try:
            directory = os.listdir(window.default_path)
        except OSError:
            tkinter.messagebox.showerror("Error",
                                         "The CombatLogs folder found in the settings file is not valid. Please "
                                         "choose another folder.")
            folder = tkinter.filedialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            variables.settings_obj.read_set()
            os.chdir(variables.settings_obj["parsing"]["cl_path"])
            directory = os.listdir(os.getcwd())
        files = []
        for file in directory:
            if file.endswith(".txt"):
                files.append(file)
        variables.files_done = 0
        self.amount_files = len(files)
        """
        if self.amount_files >= 50:
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombadwLogs folder. "+\
            "You may want to archive some of your %s CombatLogs in order to speed up the parsing program and the "+\
            "startup times." % self.amount_files)
        """
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()
        self.done = False

    def update_progress(self):
        if variables.files_done != self.amount_files:
            self.label_var.set("Parsing the files...")
            self.progress_bar["value"] = variables.files_done
            self.update()
        else:
            return


class ConnectionSplash(tk.Toplevel):
    def __init__(self, window=variables.main_window):
        tk.Toplevel.__init__(self, window)
        self.window = window
        self.FLAG = False
        self.title("GSF Parser: Connecting...")
        self.label = ttk.Label(self, text="Connecting to specified server...")
        self.label.pack()
        self.conn_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate")
        self.conn_bar.pack()
        self.window.after(500, self.connect)

    def connect(self):
        if not self.FLAG:
            self.update()
            self.window.after(500, self.connect)
        else:
            return
