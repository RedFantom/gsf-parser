"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import queue
from os import path
# Own modules
from .clienthandler import ClientHandler
from utils.directories import get_temp_directory


class StrategyClientHandler(ClientHandler):
    """
    Object that handles the communication with a Client through an *unencrypted* socket
    """
    # TODO: Support encryption for Servers that have certificates
    def __init__(self, sock, address, server_queue):
        """
        :param sock: socket object from server_socket.accept
        :param address: IP-address of the Client (only used for logging purposes)
        :param server_queue: Queue object in which commands are placed
        """
        log_file = path.join(get_temp_directory(), "strategy_clienthandler_{}.log".format(address[0]))
        ClientHandler.__init__(self, sock, address, server_queue, log_file, debug=False)
        self.name = None
        self.role = None
        # The client_queue is for the network to put commands in
        self.client_queue = queue.Queue()
        # The message_queue is used for communication with the Client
        self.message_queue = queue.Queue()

    def update(self):
        """
        A function to be regularly called by the Server in its loop to perform the basic functionality of the
        ClientHandler. Checks the message_queue and the client_queue, and uses the server_queue.
        """
        if not self.client_queue.empty():
            # The ClientHandler received a command from the network
            # The data is directly sent to the Client of the ClientHandler, as it must either be login/logout for the
            # master Client, or it is a Map operation
            self.write_log("ClientHandler {0} client_queue is not empty".format(self.name))
            server_command = self.client_queue.get()
            self.write_log("ClientHandler received server_command {0}".format(server_command))

            # Code to kick and ban is executed before sending any other commands to execute ASAP
            # The code to prevent reconnect is built into the Server
            if server_command == "kick" or server_command == "ban":
                if not self.send(server_command):
                    return
                self.close()
                return

            # Code to change the master role is handled in the ClientHandler too to change the master role
            if server_command == "master":
                self.role = "master"
                # The message is sent as normal in the next if-statement
                self.write_log("The ClientHandler was made a master ClientHandler")
            # If the sending of the command fails, end this update()
            # It may have been a one-time error where the pipe was broke, in which case there is no damage by not
            # continuing this cycle. However, the socket may be closed, in which case the close() function is already
            # called and continuing the cycle would result in errors.
            if not self.send(server_command):
                return
        # Call receive() to update the contents of the message_queue
        self.receive()
        # Process *one* message from the message_queue
        if not self.message_queue.empty():
            message = self.message_queue.get()
        else:
            # No messge was received, and thus the cycle ends
            return
        # The message is decoded from bytes into a str
        self.write_log("ClientHandler for {0} received data: {1}".format(self.name, message))
        # The command is processed in a separate function
        self.process_message(message)

    def process_message(self, message):
        """
        Function to process the command received from the Client. See line comments for more details.
        :param message: raw bytes message received
        :return: None
        """
        # First process the raw message
        messaged = message.decode()
        elements = messaged.split("_")
        command = elements[0]

        # Start checking for a command match
        if command == "login":
            # The Client requests a login

            # Check if the data received is valid
            if elements[1] != "master" and elements[1] != "client":
                # The data is not valid, so a disconnect is started
                self.close()
                return
            # The data is valid, and thus the login is accepted and put in the network queue
            self.role = elements[1]
            self.name = elements[2]
            self.write_log("ClientHandler for {0} sent b'login'".format(self.name))
            # Notify the Server of the login
            if self.role == "master":
                self.server_queue.put(("master_login", self))
            else:
                self.server_queue.put(("client_login", self))

        elif command == "strategy":
            # The Client wants to send a Strategy (serialized into a string)

            self.write_log("ClientHandler received a strategy")
            # Elements == ["strategy", serialized_strategy]
            assert len(elements) == 2
            if self.role != "master":
                # Pushing Strategies is something only the master Client can do
                raise RuntimeError("Attempted to share a strategy while not master")
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "move":
            # The Client wants to move an item on the Map

            # Elements == ["move", strategy_name, phase_name, item_name, new_x, new_y]
            assert len(elements) == 6
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "add":
            # The Client wants to add an item to the Map

            # Elements == ["add", strategy_name, phase_name, item_text, item_font_tuple, item_color_hex]
            assert len(elements) == 6
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "del":
            # The Client wants to delete an item from the Map

            # Elements == ["del", strategy_name, phase_name, item_text]
            assert len(elements) == 4
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "readonly":
            # The master Client wants to allow or disallow a client to use the Map

            # Elements == ["readonly", name, allowed_bool]
            assert len(elements) == 3
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "kick":
            # The master client wants to kick a Client

            # Elements == ["kick", name]
            assert len(elements) == 2
            self.server_queue.put((message, self))

        elif command == "allowshare":
            # The master client allows or disallows a Client from sharing Strategies

            # Elements == ["allowshare", name, allow_bool]
            assert len(elements) == 3
            self.server_queue.put((message, self))

        elif command == "allowedit":
            # The master client allows or disallows a Client from editing Strategies

            # Elements == ["allowshare", name, allow_bool]
            assert len(elements) == 3
            self.server_queue.put((message, self))

        elif command == "ban":
            # The master client wants to ban a Client from reconnecting

            # Elements == ["ban", name]
            assert len(elements) == 2
            self.server_queue.put((message, self))

        elif command == "logout":
            # The Client wants to logout

            # Elements == ["logout"]
            assert len(elements) == 1
            self.close()

        elif command == "master":
            # The master client wants to pass his master privileges to someone else

            # Elements == ["master", name]
            assert len(elements) == 2
            # Only the master is allowed to assign a new master
            if not self.role == "master":
                self.write_log("Attempted to change master while not the master ClientHandler!")
                self.close()
                return
            _, name = elements
            self.server_queue.put((command, name, self))

        elif command == "description":
            # One of the Clients with sharing rights wants to update a description

            # Elements == ["description", strategy_name, phase_name, new_description] OR
            # Elements == ["description", strategy_name, new_description]
            self.server_queue.put((message, self))

        else:
            self.write_log("ClientHandler received unknown command: {0}".format(message))
        return

    def close(self):
        """
        For whatever reason close the socket and notify the network of the logout
        """
        self.write_log("ClientHandler closing")
        self.socket.close()
        self.server_queue.put(("logout", self))











