# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from tkinter import messagebox
from datetime import datetime
import socket
from queue import Queue
# Own modules
from .client import Client
from variables import settings


class SharingClient(Client):
    """
    A Client class to interact with a SharingClientHandler, with capabilities of sharing ID/name combinations,
    bomb/owner id combinations, kills, and more. Does not provide any realtime functionality.
    """
    def __init__(self):
        self.hold_queue = Queue()
        host = settings["parsing"]["address"]
        port = settings["parsing"]["port"]
        Client.__init__(self, host, port)

    def send_name_id(self, server, faction, mainname, altname, id):
        """
        Send a name/ID combination to the server
        """
        print("[SharingClient] Sending store name command.")
        self.send("storename_{}_{}_{}_{}_{}".format(server, faction, mainname, altname, id))
        print("[SharingClient] Awaiting result.")
        message = self.get_message()
        if message == "saved":
            print("[SharingClient] Saved successfully.")
            return True
        elif message == "unkown":
            print("[SharingClient] Store failed.")
            return None
        return False

    def get_name_id(self, server, faction, id):
        """
        Get a mainname from the server
        """
        self.send("getname_{}_{}_{}".format(server, faction, id))
        message = self.get_message()
        if message is False:
            return False
        if message == "unknown":
            return None
        return message

    def get_message(self, timeout=4):
        """
        :return: A str message from the server
        """
        start = datetime.now()
        while self.message_queue.empty():
            if (datetime.now() - start).total_seconds() > timeout:
                return False
            self.receive()
        message = self.message_queue.get()
        message_decoded = message.decode() if isinstance(message, bytes) else message
        if message == "exit":
            return False
        # Possible ban commands: "ban" or "ban_message"
        elements = message_decoded.split("_")
        if elements[0] == "ban":
            ban_message = "Your IP address was banned from this server."
            if len(elements) > 1:
                _, message = elements
                ban_message += " The following message was received: {}".format(message) + "."
            messagebox.showerror("Ban", ban_message)
            return False
        return message_decoded

