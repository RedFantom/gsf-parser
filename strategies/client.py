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
from strategies.strategies import Strategy, Item
from threading import Thread
from queue import Queue


class Client(Thread):
    def __init__(self, address, port, name, role, list, logincallback, insertcallback, disconnectcallback):
        Thread.__init__(self)
        self.exit_queue = Queue()
        self.logged_in = False
        self.name = name
        self.role = role
        self.list = list
        self.exit = False
        self.login_callback = logincallback
        self.insert_callback = insertcallback
        self.disconnect_callback = disconnectcallback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(4)
        self.message_queue = Queue()
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
        self.socket.send((string + "+").encode())

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
        string = pickle.dumps(strategy)
        self.socket.send(b"strategy_" + string + b"+")
        try:
            message = self.socket.recv(16)
        except socket.timeout:
            return False
        if str(message) == "saved":
            return True
        return False

    def update(self):
        if not self.logged_in:
            return
        self.receive()
        if self.message_queue.empty():
            return
        message = self.message_queue.get()
        print("Client received data: ", message)
        try:
            dmessage = message.decode()
            elements = dmessage.split("_")
        except UnicodeDecodeError:
            elements = ["strategy", message[10:]]
        self.process_command(elements)

    def process_command(self, elements):
        command = elements[0]
        if command == "add":
            assert len(elements) == 6
            _, strategy, phase, text, font, color = elements
            self.add_item_server(strategy, phase, text, font, color)
        elif command == "move":
            assert len(elements) == 6
            _, strategy, phase, text, x, y = elements
            self.move_item_server(strategy, phase, text, x, y)
        elif command == "del":
            assert len(elements) == 4
            _, strategy, phase, text = elements
            self.del_item_server(strategy, phase, text)
        elif command == "strategy":
            assert len(elements) >= 2
            string = elements[1]
            strategy = pickle.loads(string.encode())
            if not isinstance(strategy, Strategy):
                raise ValueError("Invalid! {0}".format(type(strategy)))
            self.list.db[strategy.name] = strategy
            self.list.update_tree()

    def run(self):
        while True:
            if not self.exit_queue.empty():
                if self.exit_queue.get():
                    break
            if not self.logged_in:
                break
            self.update()

    def login_failed(self):
        self.login_callback(False)
        self.socket.close()

    def close(self):
        self.exit_queue.put(True)
        try:
            self.socket.send(b"logout")
        except OSError:
            pass
        self.socket.close()
        self.logged_in = False
        self.disconnect_callback()

    def add_item_server(self, strategy, phase, text, font, color):
        print("Add item called with: ", strategy, phase, text, font, color)
        if not self.check_strategy_phase(strategy, phase):
            return
        self.list.db[strategy][phase][text] = Item(text, 0, 0, color, font)
        self.insert_callback("add_item", (strategy, phase, text, font, color))

    def move_item_server(self, strategy, phase, text, x, y):
        print("Move item called with: ", strategy, phase, text, x, y)
        if not self.check_strategy_phase(strategy, phase):
            return
        self.insert_callback("move_item", (strategy, phase, text, x, y))

    def del_item_server(self, strategy, phase, text):
        print("Del item called with: ", strategy, phase, text)
        if not self.check_strategy_phase(strategy, phase):
            return
        del self.list.db[strategy][phase][text]
        self.insert_callback("del_item", (strategy, phase, text))

    def add_item(self, strategy, phase, text, font, color):
        print("Sending add item command")
        self.send("add_{0}_{1}_{2}_{3}_{4}".format(strategy, phase, text, font, color))

    def move_item(self, strategy, phase, text, x, y):
        print("Sending move item command")
        self.send("move_{0}_{1}_{2}_{3}_{4}".format(strategy, phase, text, x, y))

    def del_item(self, strategy, phase, text):
        print("Sending del command")
        self.send("del_{0}_{1}_{2}".format(strategy, phase, text))

    @staticmethod
    def get_temp_file():
        return os.path.join(get_temp_directory(), "client_strategy.tmp")

    def check_strategy_phase(self, strategy, phase):
        if strategy not in self.list.db:
            messagebox.showinfo("Info", "Operation on a Strategy received that was not in the database. Please wait "
                                        "for the database update.")
            return False
        if phase not in self.list.db[strategy]:
            messagebox.showerror("Info", "Operation on a Phase received that was not in the database. Please wait for "
                                         "the database update.")
            return False
        return True

    def receive(self):
        if not self.logged_in:
            return
        self.socket.setblocking(0)
        total = b""
        while True:
            try:
                message = self.socket.recv(16)
                if message == b"":
                    self.close()
                    break
                print("ClientHandler received message: ", message)
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
