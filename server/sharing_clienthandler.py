# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from queue import Queue
import socket
# Own modules
from .clienthandler import ClientHandler
from .database import DatabaseHandler
from .queries import *


class SharingClientHandler(ClientHandler):
    """
    ClientHandler to handle exactly one Sharing Client and provide services to that single Client.
    """

    excluded = ["select", "where", "insert", "create", "table"]

    def __init__(self, address, socket, database, server_queue):
        """
        :param socket: socket.socket object
        :param database: DatabaseHandler object
        :param server_queue: Queue object to send messages to the Server
        """
        if not isinstance(database, DatabaseHandler):
            raise ValueError("database is not a DatabaseHandler object")
        log_file = "sharing_clienthandler_{}.log".format(address[0])
        ClientHandler.__init__(self, socket, address, server_queue, log_file, debug=False)
        self.database = database
        self.message_queue = Queue()
        self.database_queue = Queue()
        self.client_queue = Queue()  # A Queue to receive commands from the server
        self.waiting_for_database = False
        self.state = 1
        self.internal_queue = Queue()
        # Callable object to reset state
        self.reset_state = lambda: self.next_state(reset=True)

    def update(self):
        """
        Function to be called on the ClientHandler by the Server, to update tasks. This means that each Client can
        execute one instruction on the Server per cycle. The ClientHandler should skip the cycle if it's waiting
        for data from the database but has not yet received this data.
        """
        if self.waiting_for_database:
            # If the Client is waiting for the database, then the cycle is passed through the process_database function
            # And no more instructions are executed for the Client in this function
            self.receive_from_database()
            return
        if not self.client_queue.empty():
            command = self.client_queue.get()
            self.process_server_command(command)
        self.receive()
        if self.message_queue.empty():
            # No message was found in the queue
            return
        command = self.message_queue.get()
        self.process_command(command)

    def process_command(self, command):
        """
        Function to process command given by the Client
        """
        if not isinstance(command, bytes):
            self.close_error("process_command does not support other data types than bytes")
            return
        command_string = command.decode()
        elements = command_string.split("_")
        if len(elements) == 0:
            # Empty command received
            return
        instruction = elements[0]
        # Go through all the possible instructions
        if instruction == "storename":
            # "storename", server, faction, mainname, altname, id_number
            if len(elements) != 6:
                self.close_error("wrong number of command arguments received")
                return
            _, server, faction, mainname, altname, id_number = elements
            self.store_name(server, faction, mainname, altname, id_number)
        elif instruction == "getname":
            # "getname", server, faction, id_number
            if len(elements) != 4:
                self.close_error("wrong number of command arguments received")
                return
            _, server, faction, id_number = elements
            self.get_name(server, faction, id_number)
        else:
            self.close_error("ClientHandler received unsupported command: {}".format(command))
        return

    def store_name(self, *args):
        """
        Function to store name in database
        """
        server, faction, mainname, altname, id_number = args
        primealt = 1 if mainname == altname else 0
        if self.state == 1:
            # Phase 1: Insert the character into the Alt table
            query = insert_main_character % (altname, mainname, server, faction, primealt)
            self.database.put_command_in_queue(self.database_queue, query, query=False)
            self.waiting_for_database = True
            self.internal_queue.put(lambda: self.store_name(*args))
            self.next_state()
            # Function will be recalled by receive_from_database
            return
        elif self.state == 2:
            # Phase 2: Insert the character and id into the Id table
            query = insert_id_name % (id_number, server, altname)
            self.database.put_command_in_queue(self.database_queue, query, query=False)
            self.internal_queue.put((self.store_name, args))
            self.waiting_for_database = False
            self.send("saved")
            self.reset_state()
            return
        else:
            self.write_log("store_name called while no supported state was detected")
            self.close_error()
            return

    def get_name(self, *args):
        """
        Function to get an *altname* from the database based on the ID number
        """
        if self.state == 1:
            # Generate a query and put it in the queue
            server, faction, id_number = args
            query = get_altname_by_id % id_number, server
            self.database.put_command_in_queue(self.database_queue, query, query=True)
            self.waiting_for_database = True
            self.next_state()
            return
        elif self.state == 2:
            # Return the data to the user
            # Results is supposed to be a list with a single name [altname]
            server, faction, id_number, results = args
            if not isinstance(results, list) or not len(results) == 1:
                self.close_error("Unexpected results received from database: {}".format(results))
                return
            self.waiting_for_database = False
            self.send("result_{}".format(results[0]))
            self.reset_state()
        else:
            self.close_error("get_name called while no supported state was detected")
            return

    def receive_from_database(self):
        """
        Get data back from the database
        """
        if self.database_queue.empty():
            return
        results = self.database_queue.get()
        if isinstance(results, tuple):
            # Tuple, so either successful command or errored query
            success, command, query = results
            if success is True:
                if self.internal_queue.empty():
                    self.close_error("Internal queue of ClientHandler empty while a function was expected")
                    return
                # Expecting a callable object in the internal_queue
                func, args = self.internal_queue.get()
                func(*args)
            else:
                # Command was not executed successfully
                self.close_error()
        else:
            # Not a tuple, so a successful query
            data = (results, )
            if self.internal_queue.empty():
                self.close_error("Internal queue of ClientHandler empty while a function was expected")
                return
            func, args = self.internal_queue.get()
            args = args + data
            func(*args)
        return

    def process_server_command(self, command):
        """
        Function to process command given by the Server
        """
        pass

    def close_error(self, line=None):
        """
        Function to close the ClientHandler because an error occurred
        """
        if line is not None:
            self.write_log(line)
        self.send("error")
        self.close()

    def ban(self, line):
        """
        Function to ban a client for a certain reason
        """
        self.send("ban_{}".format(line))
        self.server_queue.put(("ban", self))
        self.write_log("Client with IP {} banned for: {}".format(self.address[0], line))
        self.close()

    def close(self):
        """
        Function to close
        """
        self.server_queue.put(("exit", self))
        self.send("exit")
        self.socket.close()

    def next_state(self, reset=False):
        """
        Function to indicate a move to the next state
        """
        if reset is False:
            self.state += 1
        else:
            self.state = 1

    def receive(self):
        """
        Receives data from the Client in a particular format and then puts the separated messages into the
        message_queue, additionally checks if the data received is allowed.
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
                for item in self.excluded:
                    if item in total.lower():
                        self.ban("Disallowed SQL keyword: {}".format(item))
                        return
                self.message_queue.put(total)
                for item in elements[1:-1]:
                    self.message_queue.put(item)
                total = elements[-1]
        return
