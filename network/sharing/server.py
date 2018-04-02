"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import socket
import threading
from queue import Queue
from datetime import datetime
from select import select
# Project Modules
from utils.admin import *
from network.sharing.clienthandler import SharingClientHandler
from network.database import DatabaseHandler


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
        self.exit_queue = Queue()
        self.server_queue = Queue()
        self.banned = []
        self.client_handlers = []

    @property
    def database(self):
        return self._database

    def setup_socket(self):
        """
        Setup the socket to bind and then listen for clients
        :raises: RuntimeError if executed as non-admin
        """
        if not check_privileges() and self._address[1] <= 1000:
            escalate_privileges()
        self._socket.bind(self._address)
        drop_privileges()
        print("[SharingServer] bound to address:", self._address)

    def run(self):
        """
        Loop to provide all the Server functionality. Ends if a True
        value is found in the exit_queue Queue attribute. Allows for
        maximum of eighth people to be logged in at the same time. The
        Server logs to its own log file, which is located in the
        temporary directory of the GSF Parser.
        """
        self.setup_socket()
        self._socket.listen(self._max_clients)
        print("[SharingServer] Server listening for clients now.")
        self.database.start()
        print("[SharingServer] Database connection initialized.")
        result = False
        while True:
            # Check if the Server should exit its loop
            if not self.exit_queue.empty() and self.exit_queue.get():
                print("SharingServer stopping activities...")
                SharingServer.write_log("Sharing network is exiting loop")
                break
            # The select.select function is used so the Server can immediately continue with its operations if there are
            # no new clients. This could also be done with a try/except socket.error block, but this would introduce
            # a rather high performance penalty, so the select function is used.
            if self._socket in select([self._socket], [], [], 0)[0]:
                SharingServer.write_log("network ready to accept")
                print("[SharingServer] Accepting new client.")
                connection, address = self._socket.accept()
                # Check if the IP is banned
                if address[0] not in self.banned:
                    # The ClientHandler is created and then added to the list of active ClientHandlers
                    self.client_handlers.append(
                        SharingClientHandler(address, connection, self.database, self.server_queue))
                    print("[SharingServer] Client accepted: {}.".format(address[0]))
                else:
                    # If the IP is banned, then a message is sent
                    connection.send(b"ban")
                    connection.close()
                    print("Client banned.")
            # Check if the Server should exit its loop for the second time in this loop
            if not self.exit_queue.empty() and self.exit_queue.get() is True:
                break
            # Call the update() function on each of the active ClientHandlers to update their state
            # This is a rather long part of the loop. If there are performance issues, the update() function should
            # be checked for problems first, unless the problem in loop code is apparent.
            for client_handler in self.client_handlers:
                if client_handler.active is False:
                    print("[SharingServer] Inactive ClientHandler:", repr(client_handler))
                    continue
                if result is True:
                    print("[SharingServer] Updating")
                result = client_handler.update()
                if result is True:
                    print("[SharingServer] Client handler completed task.")
            # The server_queue contains commands from ClientHandlers, and these should *all* be handled before
            # continuing.
            while not self.server_queue.empty():
                self.do_action_for_server_queue()
            # This is the end of a cycle
        # The loop is broken because an exit was requested. All ClientHandlers are requested to close their
        # their functionality (and sockets)
        SharingServer.write_log("Server closing ClientHandlers")
        print("[SharingServer] closing ClientHandlers.")
        for client_handler in self.client_handlers:
            client_handler.close()
            SharingServer.write_log("Server closed ClientHandler {0}".format(client_handler.name))
        SharingServer.write_log("Sharing network is returning from run()")
        # Last but not least close the listening socket to release the bind on the address
        self._socket.close()
        print("[SharingServer] closed.")

    def do_action_for_server_queue(self):
        """
        Function to execute when one of the ClientHandlers needs
        something done
        """
        print("[SharingServer] Performing action for network Queue.")
        command, handler = self.server_queue.get()
        if command == "exit":
            print("[SharingServer] [{}] Removing ClientHandler".format(
                datetime.now().strftime("%H:%M:%S.%f")), handler.address)
            self.client_handlers.remove(handler)
        elif command == "ban":
            self.banned.append(handler.address[0])
        else:
            SharingServer.write_log("SharingServer received unkown command: {}".format(command))

    @staticmethod
    def write_log(line):
        """
        Write a line to the log file, but also check if the log file is
        not too bit and truncate if required
        """
        line = line.strip() + "\n"
        file_name = "sharing_server.log"
        if not os.path.exists(file_name):
            with open(file_name, "w") as fo:
                fo.write("")
        # First read the current contents of the file
        with open(file_name, "r") as fi:
            lines = fi.readlines()
        # Add the line that should be written to the file
        lines.append("[{0}] {1}".format(datetime.now().strftime("%H:%M:%S"), line))
        # Limit the file size to a 1000 lines, and truncate to 800 lines if limit is reached
        if len(lines) > 1000:
            lines = lines[len(lines) - 200:]
        # Write the new contents of the file
        with open(file_name, "w") as fo:
            fo.writelines(lines)
        return

    def stop(self):
        self.exit_queue.put(True)
        while self.is_alive():
            pass
        self.database.close()
        while self.database.is_alive():
            pass
        return

    def __exit__(self):
        self.stop()

