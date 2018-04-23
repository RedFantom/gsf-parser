"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
import _pickle as pickle
# UI Libraries
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox
from ttkwidgets import CheckboxTreeview
# Project Modules
from network.sharing.client import SharingClient
from variables import settings
from parsing.parser import Parser
from utils.directories import get_temp_directory
from network.sharing.data import *


def get_connected_client():
    """
    Setup a SharingClient and return the functional instance, or None
    if it failed. Also provides error handling if the SharingClient
    fails to connect to the network.
    """
    client = SharingClient()
    try:
        client.connect()
    except ConnectionRefusedError:
        messagebox.showerror("Error", "The remote network refused the connection.")
        return None
    except Exception as e:
        messagebox.showerror("Error", "An unidentified error occurred while connecting to the remote network:\n\n"
                                      "{}".format(repr(e)))
        return None
    client.start()
    return client


class SharingFrame(ttk.Frame):
    """
    A Frame to contain widgets to allow uploading of CombatLogs to the
    network and viewing leaderboards that keep track of individual
    player performance on different fronts. A connection to the network
    is required, and as the GSF Server is not done yet, this Frame is
    still empty.
    """

    def __init__(self, root_frame, window):
        """
        :param root_frame: The MainWindow.notebook
        :param window: The MainWindow instance
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = window
        self.cancel_sync = False
        self.sharing_db = None
        # Initialize database
        self.sharing_db_path = os.path.join(get_temp_directory(), "share.db")
        self.open_database()
        # Initialize SharingClient
        self.client = SharingClient()
        # Initialize CheckboxTreeview
        self.file_tree_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.file_tree = CheckboxTreeview(
            self, height=14, columns=("name", "legacy", "pcount", "psync", "ecount", "esync"),
            yscrollcommand=self.file_tree_scroll.set, show=("headings", "tree"))
        self.setup_treeview()
        self.update_tree()
        # Setup the progress bar and Synchronize button
        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar["maximum"] = 1
        self.synchronize_button = ttk.Button(self, text="Synchronize", command=self.synchronize, width=5)
        # Create a binding to F5
        self.bind("<F5>", self.update_tree)

    def grid_widgets(self):
        """Put widgets into the grid geometry manager"""
        self.file_tree.grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky="nswe")
        self.file_tree_scroll.grid(row=1, column=5, padx=(0, 5), pady=5, sticky="ns")
        self.progress_bar.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        self.synchronize_button.grid(row=2, column=4, columnspan=2, padx=(0, 5), pady=5, sticky="nswe")

    def setup_treeview(self):
        """Setup the Treeview with column names and headings"""
        self.file_tree_scroll.config(command=self.file_tree.yview)

        self.file_tree.column("#0", width=180, stretch=False, anchor=tk.E)
        self.file_tree.heading("#0", text="CombatLog")
        self.file_tree.column("name", width=110, anchor=tk.W)
        self.file_tree.heading("name", text="Player name")
        self.file_tree.column("legacy", width=110, stretch=False, anchor=tk.W)
        self.file_tree.heading("legacy", text="Legacy name")
        self.file_tree.column("pcount", width=70, stretch=False, anchor=tk.E)
        self.file_tree.heading("pcount", text="ID Count\nPlayer")
        self.file_tree.column("psync", width=100, stretch=False, anchor=tk.E)
        self.file_tree.heading("psync", text="Synchronized\nPlayer")
        self.file_tree.column("ecount", width=70, stretch=False, anchor=tk.E)
        self.file_tree.heading("ecount", text="ID Count\nEnemy")
        self.file_tree.column("esync", width=100, stretch=False, anchor=tk.E)
        self.file_tree.heading("esync", text="Synchronized\nEnemy")

        self.file_tree.tag_configure("complete", background="lawn green")
        self.file_tree.tag_configure("checked", background="light goldenrod")
        self.file_tree.tag_configure("incomplete", background="#ffb5b5")
        self.file_tree.tag_configure("invalid", background="gray60")

    def synchronize(self):
        """
        Callback to synchronize_button Button widget.

        Sets up a connection and starts sharing the ID-name combinations
        with the server. Also downloads ID-name combinations with the
        server and saves them to the ID-name databases.
        """
        print("[SharingFrame] Starting synchronization")
        # Connect to the network
        client = get_connected_client()
        if client is None:
            return
        character_data = self.window.characters_frame.characters
        character_names = character_data.get_player_servers()
        skipped = []
        completed = []
        self.synchronize_button.config(text="Cancel", command=self.cancel_synchronize)
        # Loop over files selected for sharing
        file_list = self.file_tree.get_checked()
        self.progress_bar["maximum"] = len(file_list)
        for file_name in file_list:
            self.progress_bar["value"] += 1
            if self.cancel_sync is True or not client.is_alive():
                break
            print("[SharingFrame] Synchronizing file '{}'".format(file_name))
            lines = Parser.read_file(file_name)
            id_list = Parser.get_player_id_list(lines)
            enemy_ids = Parser.get_enemy_id_list(lines, id_list)
            synchronized = self.get_amount_synchronized(file_name, id_list, enemy_ids)
            if synchronized == ("Complete", "Complete"):
                print("[SharingFrame] Already synchronized:", file_name)
                continue
            player_name = Parser.get_player_name(lines)
            # Skip files with ambiguous network
            if player_name not in character_names:
                skipped.append(file_name)
                print("[SharingFrame] Skipping file:", file_name)
                messagebox.showinfo(
                    "Info", "Cannot share {}. Character name not one of own characters.".format(file_name))
                continue
            server = character_names[player_name]
            # Actually start synchronizing
            print("[ShareFrame] Sending player ID list")
            result = self.send_player_id_list(id_list, character_data, server, player_name, file_name, client)
            if result is False:
                messagebox.showerror("Error", "Failed to send ID numbers.")
                break
            self.retrieve_enemy_id_list(enemy_ids, server, file_name, client)
            completed.append(file_name)
        client.close()
        print("[SharingFrame] Synchronization completed.")
        self.cancel_sync = False
        self.synchronize_button.config(state=tk.NORMAL, text="Synchronize", command=self.synchronize)
        self.update_tree()
        self.progress_bar["value"] = 0

    def send_player_id_list(self, id_list: list, character_data: dict, server: str,
                            player_name: str, file_name: str, client: SharingClient):
        """
        Send the player-name ID combinations found in the CombatLogs
        of the current user using a connected SharingClient.
        :param id_list: List of ID numbers for the user
        :param character_data: CharacterDatabase containing the
            character details
        :param server: Three-letter server code
        :param player_name: Name of the player who owns these ID numbers
        :param file_name: Name of the file containing these IDs
        :param client: Connected SharingClient instance
        """
        for index, player_id in enumerate(id_list):
            print("[SharingFrame] Sharing ID '{}' for name '{}'".format(player_id, player_name))
            legacy_name = character_data[(server, player_name)]["Legacy"]
            faction = character_data[(server, player_name)]["Faction"]
            print("[SharingFrame] Sending data: {}, {}, {}".format(player_id, legacy_name, server))
            result = client.send_name_id(server, factions_dict[faction], legacy_name, player_name, player_id)
            if result is False:
                print("[SharingFrame] Sending ID failed.")
                return False
            self.sharing_db[file_name]["player_sync"] = index + 1
            print("[SharingFrame] Successfully shared ID. Total count:", self.sharing_db[file_name]["player_sync"])
            self.save_database()
            self.update()
        return True

    def retrieve_enemy_id_list(self, enemy_id_list: list, server: str, file_name: str, client: SharingClient):
        """
        Attempt to download enemy names for ID numbers of the enemies
        for a given file and server.
        :param enemy_id_list: list of ID numbers
        :param server: three-letter server name code
        :param file_name: Name of the file to download IDs for
        :param client: Connected and set-up SharingClient instance
        """
        for enemy_id in enemy_id_list:
            result = client.get_name_id(server, enemy_id)
            if result is None or result == "none":
                continue
            self.sharing_db[file_name]["enemies"][enemy_id] = result
            self.sharing_db[file_name]["enemy_sync"] += 1
            self.save_database()
            self.update()
        return True

    @staticmethod
    def show_confirmation_dialog(skipped: list, completed: list):
        """
        Show a confirmation dialog listing the skipped and completed
        files during synchronization.
        :param skipped: List of skipped file names
        :param completed: List of completed file names
        """
        # Build information string
        string = "The following files were skipped because the network of the character could not be determined:\n"
        for skipped_file in skipped:
            string += skipped_file + "\n"
        string += "The following files were successfully synchronized:\n"
        for completed_file in completed:
            string += completed_file + "\n"
        messagebox.showinfo("Info", string)

    def cancel_synchronize(self):
        """
        Callback for button to stop the synchronization process. Does
        not actually stop the process, only sets a flag that gets
        checked by the synchronization function.
        """
        self.cancel_sync = True
        self.synchronize_button.config(state=tk.DISABLED)

    def update_tree(self, *args):
        """
        Updates the contents of the Treeview with files. Parses the
        files in the process to determine the following:
        - Whether the file is a valid GSF CombatLog
        - A string for the file
        - The player name
        - The player ID numbers
        - The enemy ID numbers
        """
        self.file_tree.delete(*self.file_tree.get_children(""))
        # This function provides a dictionary with player names as keys and servers as values
        character_names = self.window.characters_frame.characters.get_player_servers()
        for item in os.listdir(settings["parsing"]["path"]):
            # Skip non-GSF CombatLogs
            if not Parser.get_gsf_in_file(item):
                continue
            # Parse file name
            file_string = Parser.parse_filename(item)
            if file_string is None:
                # Renamed CombatLogs are not valid for use
                continue
            # Read the file
            lines = Parser.read_file(item)
            # Parse the file
            player_name = Parser.get_player_name(lines)
            legacy_name = "" if player_name not in character_names else character_names[player_name]
            player_ids = Parser.get_player_id_list(lines)
            enemy_ids = Parser.get_enemy_id_list(lines, player_ids)
            # Check how much of the IDs in this file were already synchronized
            player_sync, enemy_sync = self.get_amount_synchronized(item, player_ids, enemy_ids)
            # Generate a tag to give a background color
            tags = ("complete",) if player_sync == "Complete" and enemy_sync == "Complete" else ("incomplete",)
            tags = tags if legacy_name != "" else ("invalid",)
            # Insert the file into the Treeview
            self.file_tree.insert(
                "", tk.END, text=file_string, iid=item, tags=(tags,),
                values=(player_name, legacy_name, len(player_ids), player_sync, len(enemy_ids), enemy_sync))
        return

    def __exit__(self):
        self.save_database()

    def save_database(self):
        with open(self.sharing_db_path, "wb") as fo:
            pickle.dump(self.sharing_db, fo)

    def open_database(self):
        # Open the sharing database
        if not os.path.exists(self.sharing_db_path):
            self.sharing_db = dict()
            return
        with open(self.sharing_db_path, "rb") as fi:
            self.sharing_db = pickle.load(fi)

    def get_amount_synchronized(self, file_name, player_ids, enemy_ids):
        """
        Return the amount of ID numbers that was synchronized for this
        file, or "Complete" if all were synchronized.
        """
        # First open the file to determine the amount of IDs
        if file_name not in self.sharing_db:
            print("[SharingFrame] Adding to Sharing DB:", file_name)
            self.sharing_db[file_name] = {"player_sync": 0, "enemy_sync": 0, "enemies": {}}
        player_sync = self.sharing_db[file_name]["player_sync"]
        enemy_sync = self.sharing_db[file_name]["enemy_sync"]
        print("[SharingFrame] {}: player_sync: {}, enemy_sync: {}".format(file_name, player_sync, enemy_sync))
        result = ("Complete" if player_sync == len(player_ids) else player_sync,
                  "Complete" if enemy_sync == len(enemy_ids) else enemy_sync)
        return result
