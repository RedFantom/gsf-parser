# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from tkinter import messagebox
# Own modules
from .client import Client
from variables import settings


class SharingClient(Client):
    """
    A Client class to interact with a SharingClientHandler, with capabilities of sharing ID/name combinations,
    bomb/owner id combinations, kills, and more. Does not provide any realtime functionality.
    """
    def __init__(self):
        host = settings["parsing"]["address"]
        port = settings["parsing"]["port"]
        Client.__init__(self, host, port)

    def send_name_id(self, server, faction, mainname, altname, id):
        """
        Send a name/ID combination to the server
        """
        self.send("storename_{}_{}_{}_{}_{}".format(server, faction, mainname, altname, id))
        message = self.get_message()
        if message == "saved":
            return True
        elif message == "unkown":
            return None
        return False

    def get_name_id(self, server, faction, id):
        """
        Get a mainname from the server
        """
        self.send("getname_{}_{}_{}".format(server, faction, id))

    def get_message(self):
        """
        :return: A str message from the server
        """
        while self.message_queue.empty():
            self.receive()
        message = self.message_queue.get()
        message_decoded = message.decode()
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

