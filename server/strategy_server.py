# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
import os
import threading
from queue import Queue
from datetime import datetime
from select import select
# Own modules
from server.strategy_clienthandler import ClientHandler
from tools.admin import is_user_admin
from tools.utilities import get_temp_directory

# TODO: Send all Clients new logins
# TODO: Send all Clients the logins of all Clients already connected upon login


class Server(threading.Thread):
    """
    A Thread that runs a socket.socket server to listen for incoming tools.strategy_client.Client connections to allow
    the sharing and real-time editing of Strategy objects. Runs in a Thread to minimize performance penalty for the
    Tkinter mainloop.
    """
    def __init__(self, host, port):
        """
        :param host: hostname to bind to, binds to all available if empty string
        :param port: port number, int only
        :raises: RuntimeError if the user is not running with administrator rights
        :raises: RuntimeError if the binding to the hostname and port fails
        :raises: ValueError if the host and/or port are found to be invalid values
        """
        if not is_user_admin():
            raise RuntimeError("Attempted to open a server while user is not admin.")
        threading.Thread.__init__(self)
        # Create a non-blocking socket to provide the best performance in the loop
        # The socket is a SOCK_STREAM (TCP) socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0)
        if not Server.check_host_validity(host, port):
            raise ValueError("The host or port value is not valid: {0}:{1}".format(host, port))
        try:
            self.socket.bind((host, port))
        except socket.error:
            # This will actually provide two errors with two stack traces
            raise RuntimeError("Binding to the address and port failed.")
        self.client_handlers = []
        self.client_names = []
        # The master_handler is a ClientHandler object with a Client with the "master" role
        self.master_handler = None
        # The exit_queue is normally empty. However, if an object with a truth value of True is found, then the
        # server loop in run() will exit.
        self.exit_queue = Queue()
        # The server_queue is where the commands from the ClientHandlers are put in.
        self.server_queue = Queue()
        # The banned list contains IP addresses that will not be accepted
        self.banned = []

    def run(self):
        """
        Loop to provide all the Server functionality. Ends if a True value is found in the exit_queue Queue attribute.
        Allows for maximum of eighth people to be logged in at the same time. The Server logs to its own log file, which
        is located in the temporary directory of the GSF Parser.
        """
        # TODO: Allow the user to customize the amount of Clients allowed
        self.socket.listen(8)

        while True:
            # Check if the Server should exit its loop
            if not self.exit_queue.empty() and self.exit_queue.get():
                Server.write_log("Strategy server is exiting loop")
                break
            # The select.select function is used so the Server can immediately continue with its operations if there are
            # no new clients. This could also be done with a try/except socket.error block, but this would introduce
            # a rather high performance penalty, so the select function is used.
            if self.socket in select([self.socket], [], [], 0)[0]:
                Server.write_log("server ready to accept")
                connection, address = self.socket.accept()
                # Check if the IP is banned
                if address not in self.banned:
                    # The ClientHandler is created and then added to the list of active ClientHandlers
                    self.client_handlers.append(ClientHandler(connection, address, self.server_queue))
                else:
                    # If the IP is banned, then a message is sent
                    connection.send(b"banned")
                    connection.close()
            # Check if the Server should exit its loop for the second time in this loop
            if not self.exit_queue.empty() and self.exit_queue.get():
                break
            # Call the update() function on each of the active ClientHandlers to update their state
            # This is a rather long part of the loop. If there are performance issues, the update() function should
            # be checked for problems first, unless the problem in loop code is apparent.
            for client_handler in self.client_handlers:
                client_handler.update()
            # The server_queue contains commands from ClientHandlers, and these should *all* be handled before
            # continuing.
            while not self.server_queue.empty():
                self.do_action_for_server_queue()
            # This is the end of a cycle

        # The loop is broken because an exit was requested. All ClientHandlers are requested to close their
        # their functionality (and sockets)
        Server.write_log("Server closing ClientHandlers")
        for client_handler in self.client_handlers:
            client_handler.close()
            Server.write_log("Server closed ClientHandler {0}".format(client_handler.name))
        Server.write_log("Strategy server is returning from run()")
        # Last but not least close the listening socket to release the bind on the address
        self.socket.close()

    def do_action_for_server_queue(self):
        """
        Function called by the Server loop if the server_queue is not empty. Does not perform checks, so must only be
        called after checking that the server_queue is not empty.

        Retrieves the command of a ClientHandler from the server_queue and handles it accordingly. See line comments
        for more details.
        """
        message = self.server_queue.get()
        if isinstance(message[0], bytes):
            message = (message[0].decode(), message[1])
        Server.write_log("Server received {0} in server queue".format(message))

        # Start the handling of the message received in the server_queue
        if message[0] == "master_login":
            # A master_login event is created by a ClientHandler whose Client role is master
            Server.write_log("Server received master_login")

            if message[1].name in self.client_names or message[1].name == "" or message[1].name == "username":
                Server.write_log("Name for newly logged in Client is not valid")
                message[1].client_queue.put("invalidname")
                return
            message[1].client_queue.put("login")

            # If a master was already set, then the user is kicked for trying this
            if self.master_handler:
                message[1].client_queue.put("kick")
                return
            # The master_handler is set, and the ClientHandler who logged in is added to the client_handlers list
            self.master_handler = message[1]
            self.client_handlers.append(self.master_handler)
            # The master_handler is notified of all the current logged in Clients with role client
            # TODO: Upon sending this, the master Client sends all Strategies it has, for each client_login
            # TODO: The Strategies should only be sent once to improve performance
            for client_handler in self.client_handlers:
                self.master_handler.client_queue.put("master_login_{0}".format(client_handler.name))

        elif message[0] == "client_login":
            # A client_login is created by a ClientHandler whose Client role is client
            Server.write_log("Server received client_login from {0}".format(message[1].address))
            if message[1].name in self.client_names or message[1].name == "" or message[1].name == "username":
                Server.write_log("Name for newly logged in Client is not valid")
                message[1].client_queue.put("invalidname")
                return

            elif self.master_handler:
                # The master_handler, if it is available, is notified of this login
                # The other ClientHandlers are not notified
                self.master_handler.client_queue.put("client_login_{0}".format(message[1].name))

            # Send all previous logins to this new client
            for client_handler in self.client_handlers:
                if client_handler is self.master_handler:
                    message[1].client_queue.put("master_login_{}".format(client_handler.name))
                    continue
                message[1].client_queue.put("client_login_{}".format(client_handler.name))

        elif message[0] == "logout":
            # A logout is created by a ClientHandler whose Client has disconnected, for whatever reason
            Server.write_log("Server received logout")
            if message[1] is self.master_handler:
                # If the logout is a master logout, then the master_handler must be reset to None
                Server.write_log("Logout is a master logout")
                self.client_handlers.remove(self.master_handler)
                self.master_handler = None
            elif self.master_handler:
                # The logout is a client logout, and the master_handler should be notified if its available
                self.master_handler.client_queue.put("logout_{0}".format(message[1].name))
            else:
                # The logout is a client logout, but the master_handler is not available. Nothign happens.
                pass
            # The logged-out ClientHandler is removed from the list of active ClientHandlers.
            self.client_handlers.remove(message[1])

        elif message[0] == "kick":
            command, player = message[0].split("_")
            Server.write_log("Server received a command to kick a player {0}".format(player))
            if message[1] is not self.master_handler:
                # If anyone else but the master_handler tries to kick, then the player requesting the kick is kicked
                # as that behaviour should not be possible without modified code.
                Server.write_log("Only the master_handler is allowed to kick a player, but received the kick command "
                                 "from the ClientHandler for {0}. Kicking this person instead.".format(message[1].name))
                player = message[1].name
            sent = False
            for handler in self.client_handlers:
                if player == handler.name:
                    handler.client_queue.put("kick")
                    sent = True
                    self.server_queue.put(("logout_{}".format(player), None))
            if not sent:
                Server.write_log("Server could not find the player name. Kicking failed.")

        elif message[0].split("_") == "ban":
            command, player = message[0].split("_")
            Server.write_log("Server received a command to ban a player {0}".format(player))
            if message[1] is not self.master_handler:
                # If anyone but the master_handler tries to ban, then ban the requesting client instead
                player = message[1].name
            sent = False
            # The loop means that anyone with this name is banned.
            for handler in self.client_handlers:
                if player == handler.name:
                    # Even if banning fails, the IP should be added to the list of banned IPs
                    self.banned.append(handler.address)
                    handler.client_queue.put("ban")
                    sent = True
                    self.server_queue.put(("logout_{}".format(player), None))
            if not sent:
                Server.write_log("Server could not find player name. Banning failed.")

        elif message[0] == "master":
            Server.write_log("Master handler change requested.")
            if not message[2] is self.master_handler:
                Server.write_log("Someone other than the master_handler attempted to set a new master: {0}. "
                                 "Kicking this person instead.".format(message[2].name))
                self.server_queue.put(("kick_{0}".format(message[2].name), self.master_handler))
            else:
                command, name, handler_object = message
                # Only the first match gets the master rights
                handler = None
                for client_handler in self.client_handlers:
                    if client_handler.name == name:
                        handler = client_handler
                        break
                if not handler:
                    Server.write_log("Server failed to find a Client with name {0}".format(name))
                    handler = self.master_handler
                self.master_handler = handler
                for client_handler in self.client_handlers:
                    client_handler.client_queue.put("master_{}".format(self.master_handler.name))
                self.write_log("Successfully changed the master to {}".format(self.master_handler.name))
        else:
            # The command is not a login or a logout, and thus a Map operation
            # The command is distributed to all active ClientHandlers, except to the master_handler, as the
            # master_handler is the source of the operation
            Server.write_log("Sending data to other client handlers")
            for client_handler in self.client_handlers:
                # The client_handler is checked against the source of the operation
                if client_handler is message[1]:
                    continue
                Server.write_log("Sending data to ClientHandler {0}".format(client_handler.name))
                # The data is put into the client_queue of the ClientHandler, so the ClientHandler will send the data to
                # its Client
                client_handler.client_queue.put(message[0])

        # Update the list of client names
        self.client_names.clear()
        for client_handler in self.client_handlers:
            self.client_names.append(client_handler.name)
        return

    @staticmethod
    def check_host_validity(host, port):
        """
        Checks if the host and port are valid values, returns True if valid, False if not
        """
        # The host should be str type, the port int type
        if not isinstance(host, str) or not isinstance(port, int):
            return False
        # The host should be an IP-address, thus four numbers separated by a .
        # IPv6 is not supported!
        elements = host.split(".")
        if not len(elements) == 4 and host != "":
            return False
        # All of the four elements should be translatable to an int number
        if host != "":
            for item in elements:
                try:
                    int(item)
                except (TypeError, ValueError):
                    return False
        # The maximum port number allowed is 9998
        if not port < 9999:
            return False
        return True

    @staticmethod
    def write_log(line):
        """
        Write a line to the log file, but also check if the log file is not too bit and truncate if required
        """
        line = line.strip() + "\n"
        file_name = os.path.join(get_temp_directory(), "strategy_server.log")
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


if __name__ == '__main__':
    Server("", 6500).start()
