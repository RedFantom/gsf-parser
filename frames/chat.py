"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom
"""
# Standard Library
from datetime import datetime
from multiprocessing import Pipe
from typing import List, Tuple
# UI Libraries
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
# Project Modules
from parsing.chat import ChatParser
from widgets.chat import ChatWindow


class ChatFrame(ttk.Frame):
    """
    Frame containing ChatWindow and parsing control buttons

    Controls a ChatParser instance. Requires the selection of a correct
    character in order to perform operations. Reads the messages and
    inserts them into the ChatWindow.
    """

    def __init__(self, master, window):
        """Initialize with master widget"""
        self._highlight = False
        self._parser: ChatParser = None
        self._pipe = None
        self._after_id = None

        ttk.Frame.__init__(self, master)
        self.window = window

        self._scroll = ttk.Scrollbar(self)
        self._chat = ChatWindow(self, width=785, height=350, scrollbar=self._scroll)
        self._chars: dict = window.characters_frame.characters.copy()

        self.server, self.character = tk.StringVar(), tk.StringVar()
        servers = ("Choose Server",) + tuple(self.window.characters_frame.servers.values())
        self.server_dropdown = ttk.OptionMenu(self, self.server, *servers, command=self.update_characters)
        self.character_dropdown = ttk.OptionMenu(self, self.character, *("Choose Character",))
        self.start_button = ttk.Button(self, command=self.start_parsing, text="Start", width=20)

        self.grid_widgets()

    def grid_widgets(self):
        """Configure the widgets in the grid geometry manager"""
        self._chat.grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="nswe")
        self._scroll.grid(row=0, column=3, padx=(0, 5), pady=5, sticky="nswe")

        self.server_dropdown.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="nswe")
        self.character_dropdown.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")
        self.start_button.grid(row=1, column=2, padx=(0, 5), pady=(0, 5), sticky="nswe")

    def highlight(self):
        """Create or remove a red higlight on the missing data attrs"""
        style = ttk.Style()
        if self._highlight:
            color = style.lookup(".", "foreground", default="black")
        else:
            color = "red"
        self._highlight = not self._highlight
        style.configure("Highlight.TMenubutton", foreground=color)
        for w in (self.server_dropdown, self.character_dropdown):
            w.configure(style="Highlight.TMenubutton")

    def check_start(self):
        """Determine whether parsing can be started"""
        if self.selected_character is None:
            self.highlight()
            self.after(2000, self.highlight)
            return False
        return True

    def start_parsing(self):
        """Start the parsing if it can be started"""
        if self.check_start() is False:
            return
        self._pipe, conn = Pipe()
        try:
            server, character = self.selected_character
            self._parser = ChatParser(character, server, conn)
            self._parser.start()
        except RuntimeError:
            messagebox.showerror("Error", "An error occurred while starting the ChatParser.")
            raise
        self.start_button.config(state=tk.DISABLED, text="Working")
        self._after_id = self.after(1000, self.check_status)

    def check_status(self):
        """Periodically called function to update ChatWindow"""
        self._after_id = None
        while self._pipe.poll():
            messages = self._pipe.recv()
            if isinstance(messages, str):
                # self.start_button.config(state=tk.NORMAL)
                self.start_button.config(text=messages)
                # self.start_button.config(state=tk.DISABLED)
                continue
            self.insert_messages(messages)
        if not self._parser.is_alive():
            self.stop_parsing()
            return
        self._after_id = self.after(1000, self.check_status)

    def insert_messages(self, messages: List[Tuple[str, str, str, str]]):
        """Insert a list of messages into the ChatWindow"""
        for message in messages:
            time, channel, author, text = message
            if not isinstance(time, datetime):
                time = datetime.now()
            self._chat.create_message(time, author, text, "lightblue")
        self._chat.redraw_messages()

    def stop_parsing(self):
        """Stop the active parser"""
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._parser.join()
        self.start_button.config(state=tk.NORMAL, text="Start")
        self._parser = None

    def update_characters(self, *args):
        """Update the character_dropdown"""
        if len(args) == 0:
            return
        server = args[0]
        if "Choose" in server:
            return
        self.character_dropdown["menu"].delete(0, tk.END)
        characters = ["Choose Character"]
        if server not in self.window.characters_frame.servers.values():
            return
        for data in self.window.characters_frame.characters:
            character_server = self.window.characters_frame.servers[data[0]]
            if character_server != server:
                continue
            characters.append(data[1])
        for character in sorted(characters):
            self.character_dropdown["menu"].add_command(
                label=character, command=lambda value=character: self.character.set(value))

    @property
    def selected_character(self) -> Tuple[str, str]:
        """Return the selected character"""
        if "Choose" in self.server.get() or "Choose" in self.character.get():
            return None
        reverse_servers = {value: key for key, value in self.window.characters_frame.servers.items()}
        server = reverse_servers[self.server.get()]
        return server, self.character.get()
