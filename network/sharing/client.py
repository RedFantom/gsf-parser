"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from tkinter import messagebox
from datetime import datetime
from queue import Queue
# Project Modules
from network.client import Client
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
        """Send a name/ID combination to the network"""
        print("[SharingClient] Sending store name command.")
        self.send("storename_{}_{}_{}_{}_{}".format(server, faction, mainname, altname, id))
        print("[SharingClient] Awaiting result.")
        message = self.get_message()
        if isinstance(message, bytes):
            message = message.decode()
        if message == "saved":
            print("[SharingClient] Saved successfully.")
            return True
        elif message == "unkown":
            print("[SharingClient] Store failed.")
            return None
        print("[SharingClient] Unknown response:", message)
        return False

    def get_name_id(self, server, id):
        """Get a main name from the network"""
        self.send("getname_{}_{}".format(server, id))
        message = self.get_message()
        if message is False:
            return False
        if message == "unknown":
            return None
        return message

    def get_message(self, timeout=4):
        """
        :return: A str message from the network
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
            ban_message = "Your IP address was banned from this network."
            if len(elements) > 1:
                _, message = elements
                ban_message += " The following message was received: {}".format(message) + "."
            messagebox.showerror("Ban", ban_message)
            return False
        return message_decoded

