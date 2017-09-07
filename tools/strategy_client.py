# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
from tkinter import messagebox
from threading import Thread
from queue import Queue
from ast import literal_eval
# Own modules
from parsing.strategies import Strategy, Item, Phase


class Client(Thread):
    """
    Client to connect to a server.strategy_server.Server to get a ClientHandler and support real-time editing and
    sharing of Strategies in the StrategiesFrame.
    """
    def __init__(self, address, port, name, role, list, logincallback, insertcallback, disconnectcallback):
        """
        :param address: address of the server
        :param port: port of the server
        :param name: username for the login
        :param role: role for the login ("master" or "client")
        :param list: StrategiesList object from the StrategiesFrame (for updating its database)
        :param logincallback: Callback to call when login succeeds
        :param insertcallback: Callback to call when a command is received
        :param disconnectcallback: Callback to call when disconnect occurs
        """
        Thread.__init__(self)
        # Queue to send True to if exit is requested
        self.exit_queue = Queue()
        self.logged_in = False
        self.name = name
        # Role may be Master or Client instead of master or client
        self.role = role.lower()
        self.list = list
        self.exit = False
        self.login_callback = logincallback
        self.insert_callback = insertcallback
        self.disconnect_callback = disconnectcallback
        # Create a TCP socket with timeout 4 seconds and IPv4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(4)
        # message_queue for the receive system similar to server.strategy_clienthandler.ClientHandler.receive
        self.message_queue = Queue()
        # Attempt to connect
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
        # If connected, then login
        self.login()

    def send(self, string):
        """
        Send a command to the ClientHandler and end with a b"+"
        """
        self.socket.send((string + "+").encode())

    def login(self):
        """
        Send a login request to the ClientHandler and wait for acknowledgement, unless a timeout occurs, then call
        disconnect procedures.
        """
        self.send("login_{0}_{1}".format(self.role.lower(), self.name))
        try:
            message = self.socket.recv(16)
        except socket.timeout:
            messagebox.showerror("Error", "The connection to the target server timed out.")
            self.login_failed()
            return
        message = message.decode()
        if "login" in message:
            self.logged_in = True
            self.login_callback(True)
        elif "invalidname" in message:
            messagebox.showerror("Error", "You chose an invalid username. Perhaps it is already in use?")
            self.login_failed()
        else:
            print("Login failed because message is {}".format(message))
            self.login_failed()

    def send_strategy(self, strategy):
        """
        Send a Strategy object to the ClientHandler for sharing
        """
        if not self.role == "master":
            return
        if not isinstance(strategy, Strategy):
            raise ValueError("Attempted to send object that is not an instance of Strategy: {0}".format(type(strategy)))
        # Serialize the Strategy object and then send
        self.send(self.build_strategy_string(strategy))

    @staticmethod
    def build_strategy_string(strategy):
        """
        Function to serialize a Strategy object into a string
        """
        string = "strategy_" + strategy.name + "~" + strategy.description + "~" + str(strategy.map) + "~"
        for phase_name, phase in strategy:
            string += phase.name + "¤" + phase.description + "¤" + str(phase.map) + "¤"
            for item_name, item in phase:
                string += "³" + str(item.data)
            string += "¤"
        return string

    @staticmethod
    def read_strategy_string(string):
        """
        Function to rebuild Strategy object from string
        """
        strategy_elements = string.split("~")
        strategy_name = strategy_elements[0]
        strategy_description = strategy_elements[1]
        strategy_map = literal_eval(strategy_elements[2])
        phase_elements = strategy_elements[3:]
        strategy = Strategy(strategy_name, strategy_map)
        strategy.description = strategy_description
        for phase_string in phase_elements:
            phase_string_elements = phase_string.split("¤")
            phase_name = phase_string_elements[0]
            phase_description = phase_string_elements[1]
            phase_map = literal_eval(phase_string_elements[2])
            phase = Phase(phase_name, phase_map)
            phase.description = phase_description
            item_string = phase_string_elements[3]
            item_elements = item_string.split("³")
            for item_string_elements in item_elements:
                if item_string_elements == "":
                    continue
                item_dictionary = literal_eval(item_string_elements)
                phase[item_dictionary["name"]] = Item(
                    item_dictionary["name"],
                    item_dictionary["x"],
                    item_dictionary["y"],
                    item_dictionary["color"],
                    item_dictionary["font"]
                )
            strategy[phase_name] = phase
        return strategy

    def update(self):
        """
        Function called by the Thread loop to perform basic functionality
        """
        # If called when not logged_in, do not do anything
        if not self.logged_in:
            return
        # Check for new messages
        self.receive()
        if self.message_queue.empty():
            return
        # Get a message
        message = self.message_queue.get()
        print("Client received data: ", message)
        # Decode the message
        dmessage = message.decode()
        elements = dmessage.split("_")
        # Call function to process the message
        self.process_command(elements)

    def process_command(self, elements):
        """
        Process a command received from the ClientHandler. Only performs updates to the database, visual updates to the
        Map are performed elsewhere.
        """
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
            strategy = self.read_strategy_string(elements[1])
            self.list.db[strategy.name] = strategy
            self.list.update_tree()
        elif command == "client":
            print(elements)
            self.insert_callback("client_login", elements[2])
        elif command == "readonly":
            self.insert_callback("readonly", elements)
        elif command == "ban":
            self.close()
            self.insert_callback("banned", None)
        elif command == "kick":
            self.close()
            self.insert_callback("kicked", None)
        elif command == "master" and elements[1] != "login":
            name = elements[1]
            self.insert_callback("master", name)
        elif command == "master" and elements[1] == "login":
            self.insert_callback("master_login", elements[2])
        elif command == "allowshare":
            self.insert_callback("allowshare", elements)
        elif command == "invalidname":
            messagebox.showerror("Error", "You chose an invalid username.")
            self.disconnect_callback()
            self.close()
        else:
            print("Unimplemented command '{}' with arguments '{}'".format(command, elements))
        return

    def run(self):
        """
        Loop of the Thread to call self.update() and self.process_command() by extent.
        """
        while True:
            if not self.exit_queue.empty():
                if self.exit_queue.get():
                    break
            if not self.logged_in:
                break
            self.update()

    def login_failed(self):
        """
        Callback for when logging into the server fails, for whatever reason.
        """
        self.login_callback(False)
        self.socket.close()

    def close(self):
        """
        Function to close the Client and all its functionality to restore the situation before the Client was opened.
        """
        # The Thread may have already been stopped, but its good to make sure
        self.exit_queue.put(True)
        try:
            # Attempt to send a logout
            self.socket.send(b"logout")
        except OSError:
            # The error occurs when there's something wrong with the socket, in which case the socket was closed
            # on the server-side, in which case the event should be properly handled elsewhere (self.send designated for
            # just that).
            pass
        self.socket.close()
        self.logged_in = False
        self.disconnect_callback()

    """
    Functions to process the commands received from the server and update the database accordingly, if possible.
    Also, these functions call insert_callback for visual processing of the commands.
    """

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

    def description_server(self, strategy, phase, text):
        # TODO: Implement client side description updating
        pass

    def new_master_server(self, new_master_name):
        self.insert_callback("master", [new_master_name])

    """
    Functions to send commands to the server upon events happening on the Map.
    """

    def add_item(self, strategy, phase, text, font, color):
        print("Sending add item command")
        self.send("add_{0}_{1}_{2}_{3}_{4}".format(strategy, phase, text, font, color))

    def move_item(self, strategy, phase, text, x, y):
        self.send("move_{0}_{1}_{2}_{3}_{4}".format(strategy, phase, text, x, y))

    def del_item(self, strategy, phase, text):
        print("Sending del command")
        self.send("del_{0}_{1}_{2}".format(strategy, phase, text))

    """
    Functions to handle master control events
    """

    def new_master(self, new_master_name):
        self.send("master_{0}".format(new_master_name))
        self.insert_callback("readonly", ["readonly", "True"])
        self.insert_callback("allowshare", ["allowshare", "False"])
        self.role = "client"

    def kick_player(self, player_name):
        if not self.role == "master":
            raise ValueError("Attempted to kick a player while not master!")
        self.send("kick_{0}".format(player_name))
        self.insert_callback("logout", ["logout", player_name])

    def ban_player(self, player_name):
        if not self.role == "master":
            raise ValueError("Attempted to ban a player while not master!")
        self.send("ban_{0}".format(player_name))
        self.insert_callback("logout", ["logout", player_name])

    def allow_share_player(self, player_name, new_state):
        if not self.role == "master":
            raise ValueError("Attempted to change allow_share state while not master.")
        self.send("allowshare_{}_{}".format(player_name, new_state))

    def allow_edit_player(self, player_name, new_state):
        if not self.role == "master":
            raise ValueError("Attempted to change the allow_edit state while not master.")
        self.send("allowedit_{}_{}".format(player_name, new_state))

    def readonly_player(self, player_name, new_state):
        if not self.role == "master":
            raise ValueError("Attempted to change readonly state while not master.")
        self.send("readonly_{}_{}".format(player_name, new_state))

    def check_strategy_phase(self, strategy, phase):
        """
        Function to check if a particular strategy and phase are available in the database and give the user feedback
        if not. Returns True if the code which called the function is clear to move ahead with a database update.
        """
        return strategy in self.list.db and phase in self.list.db[strategy]

    def receive(self):
        """
        Function to receive and separate messages received from the ClientHandler
        """
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
