# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
import threading
from queue import Queue


class Client(threading.Thread):
    """
    Parent class for all GSF Parser Client classes. Provides base functionality, including sending and receiving
    messages in a more stream-lines way than can be achieved with plain sockets.
    """
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.exit_queue = Queue()
        self.message_queue = Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = host
        self.port = port

    def connect(self):
        """
        Function to connect to the specified server. Can be overridden to additionally perform error handling or perhaps
        some sort of login functionality.
        """
        timeout = self.socket.gettimeout()
        self.socket.settimeout(4)
        self.socket.connect((self.address, self.port))
        self.socket.settimeout(timeout)

    def run(self):
        """
        Loop of the Thread to call self.update() and self.process_command() by extent.
        """
        while True:
            if not self.exit_queue.empty():
                break
            self.update()
        self.send("exit")
        self.socket.close()

    def update(self):
        """
        Function to be implemented by a child class to perform the functionality it's made for
        """
        self.receive()

    def close(self):
        """
        Function that can be overriden by a child class to perform additional functionality, such as sending a
        logout message.
        """
        self.exit_queue.put(True)

    def send(self, string):
        """
        Send a command to a ClientHandler and end with a b"+"
        """
        if not isinstance(string, str):
            string = string.decode()
        return self.socket.send((string + "+").encode())

    def receive(self):
        """
        Function to receive and separate messages received from the ClientHandler
        """
        print("Starting receive")
        self.socket.setblocking(False)
        total = b""
        wait = False
        while True:
            try:
                message = self.socket.recv(32)
                total += message
                print(total)
                wait = message[-1] != 43
                if message == b"":
                    break
            except socket.error:
                if wait is True:
                    continue
                else:
                    break
        print("[Client] received message: ", total, wait)
        elements = total.split(b"+")
        for elem in elements:
            try:
                if elem.decode() == "":
                    continue
            except UnicodeDecodeError:
                pass
            self.message_queue.put(elem)
        return
