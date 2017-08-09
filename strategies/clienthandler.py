# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
from tools.utilities import get_temp_directory
from datetime import datetime
from os import path
import queue


class ClientHandler(object):
    def __init__(self, sock, address, server_queue):
        self.socket = sock
        self.address = address
        self.name = None
        self.role = None
        self.server_queue = server_queue
        self.client_queue = queue.Queue()

    def update(self):
        try:
            message = self.socket.recv(8192)
        except socket.timeout:
            return
        except ConnectionAbortedError:
            self.close()
        try:
            message = message.decode()
        except AttributeError as e:
            print(e)
            return
        elements = message.split("_")
        command = elements[0]
        if command == "login":
            if elements[1] != "master" and elements[1] != "client":
                raise ValueError("Not a valid role received, got {0} instead of expected `master` or `client`".
                                 format(elements[1]))
            self.role = elements[1]
            self.name = elements[2]
            print("Client handler sent b'login'")
            self.socket.send(b"login")
            if self.role == "master":
                self.server_queue.put(("master_login", self))
            else:
                self.server_queue.put(("client_login", self))
        elif command == "strategy":
            assert len(elements) >= 2
            # command, pickle
            if self.role != "master":
                raise RuntimeError("Attempted to share a strategy while not master")
            self.server_queue.put(message)
        elif command == "move":
            assert len(elements) == 4
            # command, strategy, phase, text
            self.server_queue.put(message)
        elif command == "add":
            assert len(elements) == 6
            # command, strategy, phase, text, font, color
            self.server_queue.put(message)
        elif command == "del":
            assert len(elements) == 4
            # command, strategy, phase, text
            self.server_queue.put(message)
        else:
            raise ValueError("Unkown command received: {0}".format(command))
        if not self.client_queue.empty():
            server_command = self.client_queue.get(block=False)
            self.send(server_command)

    def send(self, command):
        if not isinstance(command, str):
            raise ValueError()
        self.socket.send(command.encode())

    def close(self):
        self.socket.close()
        self.server_queue.put(("logout", self))

    def write_log(self, line):
        with open(path.join(get_temp_directory(), "client_handler_{0}.log".format(self.address)), "a") as fo:
            fo.write("[{0}] {1}".format(datetime.now().strftime("%H:%M:%S"), line))









