# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
from queue import Queue
from os import path
from datetime import datetime


class ClientHandler(object):
    """
    Simple class that supports the handling of a Client
    """

    def __init__(self, sock, address, server_queue, log_file, debug=True):
        """
        :param socket: socket.socket object
        :param address: (ip, id) tuple
        :param server_queue: Queue
        """
        # Perform type checking
        if not isinstance(sock, socket.socket):
            raise ValueError("sock argument is not a socket.socket")
        if not isinstance(address, tuple) or not len(address) == 2 or not isinstance(address[0], str):
            raise ValueError("invalid address tuple passed as argument: {}".format(address))
        if not isinstance(server_queue, Queue):
            raise ValueError("server_queue argument is not a queue.Queue")
        if not isinstance(log_file, str) or not path.exists(path.dirname(log_file)):
            raise ValueError("invalid log_file name passed as argument: {}".format(log_file))
        self.socket = sock
        self.address = address
        self.server_queue = server_queue
        self.message_queue = Queue()
        self.debug = debug
        self.log_file = log_file

    def update(self):
        """
        Function to be called regularly
        """
        self.receive()

    def close(self):
        """
        Closes the socket
        """
        self.socket.close()

    def receive(self):
        """
        Receives data from the Client in a particular format and then puts the separated messages into the message_queue
        """
        self.socket.setblocking(0)
        total = b""
        while True:
            try:
                message = self.socket.recv(16)
                if message == b"":
                    self.close()
                    break
                self.write_log("ClientHandler received message: {0}".format(message))
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

    def send(self, command):
        """
        Send data to the Client on the other side of the socket. This function processed the data first, as it must be
        sent in a certain format. The data must be sent as a bytes object, ending with a '+' to indicate the end of
        a message to the Client as the socket does *not* separate messages.
        :param command: data to send
        :return: True if successful, False if not
        :raises: ValueError if not one (1) b'_' is found in the command to send (both more and less raise an error)
        """
        self.write_log("ClientHandler sending {0}".format(command))
        if isinstance(command, bytes):
            to_send = command + b"+"
        elif isinstance(command, str):
            string = command + "+"
            to_send = string.encode()
        else:
            raise ValueError("Received invalid type as command: {0}, {1}".format(type(command), command))
        try:
            self.socket.send(to_send)
        except ConnectionError:
            self.close()
            return False
        return True

    def write_log(self, line):
        """
        Write a line to the log file, but also check if the log file is not too bit and truncate if required

        Copied from server.strategy_server.write_log(line) but with different file_name
        """
        if not self.debug:
            return
        line = line.strip() + "\n"
        if not path.exists(self.log_file):
            with open(self.log_file, "w") as fo:
                fo.write("")
        # First read the current contents of the file
        with open(self.log_file, "r") as fi:
            lines = fi.readlines()
        # Add the line that should be written to the file
        lines.append("[{0}] {1}".format(datetime.now().strftime("%H:%M:%S"), line))
        # Limit the file size to a 1000 lines, and truncate to 800 lines if limit is reached
        if len(lines) > 1000:
            lines = lines[len(lines) - 200:]
        # Write the new contents of the file
        with open(self.log_file, "w") as fo:
            fo.writelines(lines)
        return
