# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
import os
import _pickle as pickle
from tkinter import messagebox
from tools.utilities import get_temp_directory
from strategies.strategies import Strategy
from threading import Thread
from queue import Queue


class Client(Thread):
    def __init__(self, address, port, name, role, list, logincallback, insertcallback):
        Thread.__init__(self)
        self.exit_queue = Queue()
        self.logged_in = False
        self.name = name
        self.role = role
        self.list = list
        self.exit = False
        self.login_callback = logincallback
        self.insert_callback = insertcallback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(4)
        try:
            self.socket.connect((address, port))
        except socket.timeout:
            messagebox.showerror("Error", "The connection to the target server timed out.")
            self.login_failed()
            return
        except ConnectionRefusedError:
            messagebox.showerror("Error", "The server refused the connection. Perhaps the server does not have "
                                          "correct firewall or port forwarding settings.")
            self.login_failed()
            return
        self.login()

    def send(self, string):
        self.socket.send(string.encode())

    def login(self):
        self.send("login_{0}_{1}".format(self.role.lower(), self.name))
        try:
            message = self.socket.recv(16)
        except socket.timeout:
            messagebox.showerror("Error", "The connection to the target server timed out.")
            self.login_failed()
            return
        try:
            message = message.decode()
        except AttributeError as e:
            print(e)
            self.login_failed()
        if message == "login":
            self.logged_in = True
            self.login_callback(True)
        else:
            self.login_failed()

    def send_strategy(self, strategy):
        if self.role != "master":
            raise RuntimeError("Attempted to send a strategy to the server while role is not master")
        if not isinstance(strategy, Strategy):
            raise ValueError("Attempted to send object that is not an instance of Strategy: {0}".format(type(strategy)))
        file_name = Client.get_temp_file()
        with open(file_name, "wb") as fo:
            pickle.dump(strategy, fo)
        with open(file_name, "rb") as fi:
            string = fi.readall()
        self.send("strategy_{0}".format(string))
        try:
            message = self.socket.recv(16)
        except socket.timeout:
            return False
        if str(message) == "saved":
            return True
        return False

    def update(self, repeat=True):
        try:
            message = self.socket.recv(8192)
        except socket.timeout:
            return
        print("Received message from server: ", message)
        self.insert_callback(message)
        if not repeat or self.exit:
            print("Client.update not repeating.")
            return

    def run(self):
        while True:
            if not self.exit_queue.empty():
                if self.exit_queue.get():
                    break
            self.update()

    def login_failed(self):
        self.login_callback(False)
        self.socket.close()

    def close(self):
        self.exit_queue.put(True)
        self.socket.send(b"logout")
        self.socket.close()
        self.logged_in = False

    def add_item(self, *args):
        print("Add item called with: ", args)

    def move_item(self, *args):
        print("Move item called with: ", args)

    def del_item(self, *args):
        print("Del item called with: ", args)

    @staticmethod
    def get_temp_file():
        return os.path.join(get_temp_directory(), "client_strategy.tmp")


