# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
# General imports
import os
from datetime import datetime
import shelve
# UI imports
import tkinter.ttk as ttk
import tkinter as tk
from ttkwidgets import CheckboxTreeview
# Own modules
from server.sharing_client import SharingClient
import variables
from parsing import parse, fileops
from tools.utilities import get_temp_directory
from toplevels.splashscreens import SplashScreen
from widgets.readonly_entry import ReadonlyEntry
from widgets import VerticalScrollFrame


class SharingFrame(ttk.Frame):
    """
    A Frame to contain widgets to allow uploading of CombatLogs to the server
    and viewing leaderboards that keep track of individual player performance
    on different fronts. A connection to the server is required, and as the
    GSF Server is not done yet, this Frame is still empty.
    """

    def __init__(self, root_frame):
        """
        :param root_frame: The MainWindow.notebook
        """
        ttk.Frame.__init__(self, root_frame)
        # Open the sharing database
        sharing_db_path = os.path.join(get_temp_directory(), "share.db")
        self.sharing_db = shelve.open(sharing_db_path)
        # Initialize SharingClient
        address = variables.settings_obj["sharing"]["server_address"]
        port = variables.settings_obj["sharing"]["server_port"]
        server = (address, port)
        self.client = SharingClient(*server)
        # Initialize CheckboxTreeview
        self.file_tree_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.file_tree = CheckboxTreeview(self, height=14, columns=("name", "count", "sync"), show=("headings", "tree"),
                                          yscrollcommand=self.file_tree_scroll.set)
        self.file_tree_scroll.config(command=self.file_tree.yview)
        self.file_tree.column("#0", width=150, stretch=False, anchor=tk.E)
        self.file_tree.heading("#0", text="CombatLog")
        self.file_tree.column("name", width=100)
        self.file_tree.heading("name", text="Player name")
        self.file_tree.column("count", width=80, stretch=False, anchor=tk.E)
        self.file_tree.heading("count", text="ID Count")
        self.file_tree.column("sync", width=90, stretch=False, anchor=tk.E)
        self.file_tree.heading("sync", text="Synchronized")
        self.update_tree()
        # Setup the progress bar and Synchronize button
        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar["maximum"] = 1
        self.synchronize_button = ttk.Button(self, text="Synchronize", command=self.synchronize)
        # Setup the manual frame
        self.manual_frame = ManualFrame(self)
        self.manual_frame.grid_widgets()
        # Create a binding to F5
        self.bind("<F5>", self.update_tree)

    def synchronize(self):
        """
        Function for the sync_button to call when pressed. Connects to the server.
        """
        pass

    def grid_widgets(self):
        """
        The usual for putting the widgets into their correct positions
        """
        self.file_tree.grid(row=1, column=1, padx=5, pady=5, sticky="nswe")
        self.file_tree_scroll.grid(row=1, column=2, padx=(0, 5), pady=5, sticky="ns")
        self.manual_frame.grid(row=1, column=3, padx=(0, 5), pady=5, sticky="nswe", columnspan=2)
        self.progress_bar.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="nswe")
        self.synchronize_button.grid(row=2, column=4, padx=(0, 5), pady=5, sticky="nswe")

    def update_tree(self, *args):
        """
        Fills the tree with filenames
        """
        valid_gsf_combatlogs = sorted(fileops.get_valid_gsf_combatlogs())
        for item in valid_gsf_combatlogs:
            file_string = fileops.get_file_string(item)
            if file_string is None:
                # Creating a nice file string failed, probably a custom filename
                continue
            # Get the right values from the CombatLog to show in the tree
            path = os.path.join(variables.settings_obj["parsing"]["cl_path"], item)
            with open(path, "r") as fi:
                lines = fi.readlines()
            player_name = parse.determinePlayerName(lines)
            player_ids = parse.determinePlayer(lines)
            synchronized = self.get_amount_synchronized(item, player_ids)
            self.file_tree.insert("", tk.END, text=file_string, iid=item,
                                  values=(player_name, len(player_ids), synchronized))

    def __exit__(self):
        self.save_database()

    """
    The following functions are for database operations.
    """

    def save_database(self):
        self.sharing_db.close()

    def get_amount_synchronized(self, file_name, player_ids):
        """
        Return the amount of ID numbers that was synchronized for this file, or "Complete" if all were synchronized.
        """
        # First open the file to determine the amount of IDs
        if file_name not in self.sharing_db:
            self.sharing_db[file_name] = 0
        if len(player_ids) == self.sharing_db[file_name]:
            return "Complete"
        return self.sharing_db[file_name]


class ManualFrame(VerticalScrollFrame):
    """
    Frame that contains widgets to allow manual data retrieval from a SharingServer
    """

    def __init__(self, master):
        VerticalScrollFrame.__init__(self, master, canvasheight=350, canvaswidth=290)
        self.header_label = ttk.Label(self.interior, text="Manual Data Retrieval", font=("Calibri", 12),
                                      justify=tk.LEFT)
        self.description_label = ttk.Label(
            self.interior,
            text="You can use these widgets to get some data from the server manually. Simply enter the "
                 "reference data in the Entry box, press <Return> and wait for the data to appear in the "
                 "Entry box on the right.",
            font=("Calibri", 10), justify=tk.LEFT, wraplength=285
        )

    def grid_widgets(self):
        """
        The usual function to put all widgets in their correct place
        """
        self.header_label.grid(row=1, column=1, columnspan=3, sticky="nswe", padx=5, pady=(0, 5))
        self.description_label.grid(row=2, column=1, columnspan=3, sticky="nswe", padx=5, pady=(0, 5))

    def get_mainname_for_altname(self):
        pass

    def get_killer_mainname_for_id(self):
        pass

    def get_mainname_for_bomb_id(self):
        pass
