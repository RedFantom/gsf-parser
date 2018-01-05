# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
# General imports
import os
import sys
import shelve
# UI imports
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox
from ttkwidgets import CheckboxTreeview
from ttkwidgets.autocomplete import AutocompleteCombobox
# Own modules
from server.sharing_client import SharingClient
from variables import settings
from parsing import fileops
from parsing.parser import Parser
from tools.utilities import get_temp_directory
from widgets import VerticalScrollFrame
from server.sharing_data import *


def get_connected_client():
    client = SharingClient()
    try:
        client.connect()
    except ConnectionRefusedError:
        messagebox.showerror("Error", "The remote server refused the connection.")
        return None
    except Exception as e:
        messagebox.showerror("Error", "An unidentified error occurred while connecting to the remote server:\n\n"
                                      "{}".format(repr(e)))
        return None
    client.start()
    return client


class SharingFrame(ttk.Frame):
    """
    A Frame to contain widgets to allow uploading of CombatLogs to the server
    and viewing leaderboards that keep track of individual player performance
    on different fronts. A connection to the server is required, and as the
    GSF Server is not done yet, this Frame is still empty.
    """

    def __init__(self, root_frame, window):
        """
        :param root_frame: The MainWindow.notebook
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = window
        self.cancel_sync = False
        # Open the sharing database
        sharing_db_path = os.path.join(get_temp_directory(), "share.db")
        self.sharing_db = shelve.open(sharing_db_path)
        # Initialize SharingClient
        self.client = SharingClient()
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
        # Connect to the server
        client = get_connected_client()
        if client is None:
            return
        character_data = self.window.characters_frame.characters
        character_names = self.get_player_names(character_data)
        skipped = []
        completed = []
        self.synchronize_button.config(text="Cancel", command=self.cancel_synchronize)
        # Loop over files selected for sharing
        for file_name in self.file_tree.get_checked():
            if self.cancel_sync is True:
                break
            print("[SharingFrame] Synchronizing file '{}'".format(file_name))
            lines = self.read_file(file_name)
            id_list = Parser.get_player_id_list(lines)
            synchronized = self.get_amount_synchronized(file_name, id_list)
            if synchronized == "Complete":
                continue
            player_name = Parser.get_player_name(lines)
            # Skip files with ambiguous server
            if player_name not in character_names:
                skipped.append(file_name)
                continue
            server = character_names[player_name]
            self.sharing_db[file_name] = 0
            # Actually start synchronizing
            self.send_player_id_list(id_list, character_data, server, player_name, file_name, client)
            completed.append(file_name)
        client.close()
        self.cancel_sync = False
        self.synchronize_button.config(state=tk.NORMAL, text="Synchronize", command=self.synchronize)

    @staticmethod
    def get_player_names(character_data):
        character_names = {}
        names = []
        for name, server in character_data.keys():
            if name in names:
                if name in character_names:
                    del character_names[name]
                continue
            character_names[name] = server
            names.append(name)
        return names

    def send_player_id_list(self, id_list, character_data, server, player_name, file_name, client):
        for player_id in id_list:
            print("[SharingFrame] Sharing ID '{}' for name '{}'".format(player_id, player_name))
            legacy_name = character_data[(server, player_name)]["Legacy"]
            faction = character_data[(server, player_name)]["Faction"]
            print("[SharingFrame] Sending data: {}, {}, {}".format(player_id, legacy_name, server))
            client.send_name_id(server, factions_dict[faction], legacy_name, player_name, player_id)
            self.sharing_db[file_name] += 1

    @staticmethod
    def show_confirmation_dialog(skipped, completed):
        # Build information string
        string = "The following files were skipped because the server of the character could not be determined:\n"
        for skipped_file in skipped:
            string += skipped_file + "\n"
        string += "The following files were successfully synchronized:\n"
        for completed_file in completed:
            string += completed_file + "\n"
        messagebox.showinfo("Info", string)

    def cancel_synchronize(self):
        self.cancel_sync = True
        self.synchronize_button.config(state=tk.DISABLED)

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
            file_string = Parser.parse_filename(item)
            if file_string is None:
                # Creating a nice file string failed, probably a custom filename
                continue
            # Get the right values from the CombatLog to show in the tree
            lines = self.read_file(item)
            player_name = Parser.get_player_name(lines)
            player_ids = Parser.get_player_id_list(lines)
            synchronized = self.get_amount_synchronized(item, player_ids)
            self.file_tree.insert("", tk.END, text=file_string, iid=item,
                                  values=(player_name, len(player_ids), synchronized))

    @staticmethod
    def read_file(file_name):
        path = os.path.join(settings["parsing"]["path"], file_name)
        with open(path, "rb") as fi:
            lines = []
            for line in fi:
                try:
                    lines.append(line.decode())
                except UnicodeDecodeError:
                    continue
        return lines

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


class ManualFrame(ttk.Frame):
    """
    Frame that contains widgets to allow manual data retrieval from a SharingServer
    """

    def __init__(self, master):
        # VerticalScrollFrame.__init__(self, master, canvasheight=350, canvaswidth=290)
        ttk.Frame.__init__(self, master)
        self.interior = self
        self.header_label = ttk.Label(self.interior, text="Manual Data Retrieval", font=("Calibri", 12),
                                      justify=tk.LEFT)
        self.description_label = ttk.Label(
            self.interior,
            text="You can use these widgets to get some data from the server manually. Simply enter the "
                 "reference data in the Entry box, press <Return> and wait for the data to appear in the "
                 "Entry box on the right.",
            font=("Calibri", 10), justify=tk.LEFT, wraplength=285
        )
        # Get name
        self.get_name_frame = GetNameFrame(self.interior)
        self.unbind("<MouseWheel>")

    def grid_widgets(self):
        """
        The usual function to put all widgets in their correct place
        """
        self.header_label.grid(row=1, column=1, columnspan=3, sticky="nswe", padx=5, pady=(0, 5))
        self.description_label.grid(row=2, column=1, columnspan=3, sticky="nswe", padx=5, pady=(0, 5))
        self.get_name_frame.grid(row=3, column=1, columnspan=3, sticky="nswe", padx=5, pady=(0, 5))


class GetNameFrame(ttk.Frame):
    """
    Frame that contains the widgets to manually retrieve a name
    """

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.header_label = ttk.Label(
            self, text="Name for ID number", font=("Calibri", 11), width=40 if sys.platform != "linux" else 34)
        self.server = tk.StringVar()
        self.after_task = None
        self.server_dropdown = AutocompleteCombobox(self, textvariable=self.server, completevalues=servers_list)
        self.faction = tk.StringVar()
        self.faction_dropdown = AutocompleteCombobox(self, textvariable=self.faction, completevalues=factions_list)
        self.id = tk.StringVar()
        self.id_entry = ttk.Entry(self, textvariable=self.id, width=20 if sys.platform != "linux" else 15)
        self.id_entry.bind("<Return>", self.get_name)
        self.result_entry = ttk.Entry(self, width=20 if sys.platform != "linux" else 15)
        self.result_entry.insert(tk.END, "Result...")
        self.result_entry.config(state="readonly")
        self.grid_widgets()

    def get_name(self, *args):
        client = get_connected_client()
        if client is None:
            return
        server = self.server.get()
        faction = self.faction.get()
        if server not in servers_list or faction not in factions_list:
            messagebox.showinfo("Info", "Entered data is not valid. Please check your server and faction values.")
            return
        result = client.get_name_id(servers_dict[server], factions_dict[faction], self.id_entry.get())
        client.close()
        # Insert into the result box
        self.result_entry.config(state=tk.NORMAL)
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(tk.END, result)
        self.result_entry.config(state="readonly")

    def grid_widgets(self):
        self.header_label.grid(row=1, column=1, sticky="w", pady=5)
        self.server_dropdown.grid(row=2, column=1, sticky="nswe", pady=(0, 5))
        self.faction_dropdown.grid(row=3, column=1, sticky="nswe", pady=(0, 5))
        self.id_entry.grid(row=4, column=1, sticky="nswe", pady=(0, 5))
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(tk.END, "ID Number...")
        self.result_entry.grid(row=5, column=1, sticky="nswe", columnspan=4, pady=(0, 5))
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(tk.END, "Result")
