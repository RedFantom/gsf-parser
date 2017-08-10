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
from time import sleep


class ClientHandler(object):
    def __init__(self, sock, address, server_queue):
        self.socket = sock
        self.address = address
        self.name = None
        self.role = None
        self.server_queue = server_queue
        self.client_queue = queue.Queue()
        self.message_queue = queue.Queue()

    def update(self):
        if not self.client_queue.empty():
            print("ClientHandler {0} client_queue is not empty".format(self.name))
            server_command = self.client_queue.get(block=False)
            print("ClientHandler received server_command ", server_command)
            self.send(server_command)
        self.receive()
        if not self.message_queue.empty():
            message = self.message_queue.get()
        else:
            return
        try:
            messaged = message.decode()
            elements = messaged.split("_")
        except UnicodeDecodeError:
            elements = [message[:10].decode(), message[10:]]
        print("ClientHandler for {0} received data: ".format(self.name), message)
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
            self.server_queue.put((message, self))
        elif command == "move":
            assert len(elements) == 6
            # command, strategy, phase, text, x, y
            self.server_queue.put((message, self))
        elif command == "add":
            assert len(elements) == 6
            # command, strategy, phase, text, font, color
            self.server_queue.put((message, self))
        elif command == "del":
            assert len(elements) == 4
            # command, strategy, phase, text
            self.server_queue.put((message, self))
        elif command == "logout":
            assert len(elements) == 1
            self.server_queue.put(("logout", self))
        else:
            print("ClientHandler received unkown command: ", message)
        return

    def send(self, command):
        print("ClientHandler sending ", command)
        if isinstance(command, bytes):
            string = command.decode()
            string += "+"
        elif isinstance(command, tuple):
            raise ValueError("Received tuple as command: {0}", command)
        elif isinstance(command, str):
            string = command + "+"
        else:
            raise ValueError("Received invalid type as command: {0}, {1}".format(type(command), command))
        self.socket.send(string.encode())

    def close(self):
        print("ClientHandler closing")
        self.socket.close()
        self.server_queue.put(("logout", self))

    def write_log(self, line):
        with open(path.join(get_temp_directory(), "client_handler_{0}.log".format(self.address)), "a") as fo:
            fo.write("[{0}] {1}".format(datetime.now().strftime("%H:%M:%S"), line))

    def receive(self):
        self.socket.setblocking(0)
        total = b""
        while True:
            try:
                message = self.socket.recv(16)
                print("ClientHandler received message: ", message)
                if message == b"":
                    self.close()
                    return
            except socket.error:
                break
            elements = message.split(b"+")
            total += elements[0]
            if len(elements) >= 2:
                self.message_queue.put(total)
                for item in elements[1:-1]:
                    self.message_queue.put(item)
                total = elements[-1]
        return












