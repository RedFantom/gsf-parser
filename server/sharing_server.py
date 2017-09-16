# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
import os
import threading
from queue import Queue
from datetime import datetime
from select import select
# Own modules
from tools.admin import is_user_admin
from tools.utilities import get_temp_directory
from .database import DatabaseHandler


class SharingServer(threading.Thread):
    """
    Server for long awaited features. Complete rewritten, without any legacy code, using a new method of accepting
    clients (specifically mirroring the StrategyServer) and with new, easier protocol messages.
    """
    def __init__(self, address=("127.0.0.1", 83), max_clients=16):
        self._address = address
        self._max_clients = max_clients
        threading.Thread.__init__(self)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._database = DatabaseHandler()

    def setup_socket(self):
        """
        Setup the socket to bind and then listen for clients
        :raises: RuntimeError if executed as non-admin
        """
        if not is_user_admin():
            raise RuntimeError("SharingServer can only bind to the address if executed with admin rights")
        self._socket.bind(self._address)
        self._socket.listen(self._max_clients)

