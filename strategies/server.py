# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from datetime import datetime
import asyncore
import socket
from queue import Queue
from strategies.tools import get_temp_directory
import os


class Server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(8)
        self._handlers = []
        self._master_handler = None

    def handle_accept(self):
        pair = self.accept()
        if not pair:
            return
        sock, _ = pair
        handler = ClientHandler(sock, callback=self._callback)
        self._handlers.append(handler)

    def _callback(self, client_handler, data):
        self.write_log(
            "Received command \"{0}\" from client_handler with name \"{1}\"".format(data, client_handler.name)
        )
        assert isinstance(data, str)
        elements = data.split("_")
        assert len(elements) >= 1
        command = elements[0]
        if command == "login":
            assert len(elements) is 3
            role = elements[1]
            if role == "master":
                self._master_handler = client_handler
            print("Logging in {0} as {1}".format(elements[2], role))
            for handler in self._handlers:
                handler.send(data)
            print("Done logging in {0}".format(elements[2]))
        elif command == "logout":
            if (not client_handler is self._master_handler) and isinstance(self._master_handler, ClientHandler):
                self._master_handler.send(data)
            while client_handler in self._handlers:
                self._handlers.remove(client_handler)
            self.send_to_client_handlers(data)
        elif command == "setstrategy":
            if not client_handler == self._master_handler:
                client_handler.send("requires_master")
                return
            self.send_to_client_handlers(data)
        elif command == "update":
            if client_handler is not self._master_handler:
                client_handler.send("requires_master")
            self.send_to_client_handlers(data)
        elif command == "sharestrategy":
            pass
        else:
            print("The following command was not recognized: {0}".format(command))
            self.write_log("The following command was not recognized: {0}".format(command))

    def send_to_client_handlers(self, data):
        for handler in self._handlers:
            if handler is self._master_handler:
                continue
            handler.send(data)
        return

    @staticmethod
    def write_log(line):
        with open(os.path.join(get_temp_directory(), "log_server.txt"), "a") as fo:
            fo.write("[{0}] ".format(datetime.now().strftime("%H:%M:%S")) + line.replace("\n", "") + "\n")
        return


class ClientHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, callback=None):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.role = None
        self.name = None
        self._callback = callback
        self._backlog = Queue()

    def handle_read(self):
        data = self.recv(8192)
        if not data:
            return
        command, value = self.check_data(data)
        self.interpret_data(command, value)

    # def handle_close(self):
    #     self.callback("logout_{0}_{1}".format(self.role, self.name))

    def interpret_data(self, command, value):
        if command == "role":
            if self.role:
                print("Attempted to set role, but already set")
                return
            self.role = value
            if self.role and self.name:
                self.callback("login_{0]_{1}".format(self.role, self.name))
        elif command == "name":
            if self.name:
                print("Attempted to set name, but already set")
                return
            self.name = value
            if self.role and self.name:
                self.callback("login_{0}_{1}".format(self.role, self.name))
        elif command == "setstrategy":
            self.callback("strategy_{0}".format(value))
        elif command == "update":
            self.callback("update_{0}".format(value))
        elif command == "sharestrategy":
            self.callback("sharestrategy_{0}".format(value))
        elif command == "logout":
            self.close()
        else:
            print("The client handler did not recognize the command: \"{0}\"".format(command))
        return

    def callback(self, command):
        if callable(self._callback):
            self._callback(self, command)
        return

    @staticmethod
    def check_data(data):
        if not isinstance(data, str):
            data = data.decode()
        assert "=" in data
        elements = data.split("=")
        if len(elements) is not 2:
            print("len(elements) is not 2 with these elements: ", elements)
        command, value = elements
        return command, value

    def send(self, data):
        if not isinstance(data, str):
            data = data.decode()
        data = (data + ".").encode()
        try:
            asyncore.dispatcher_with_send.send(self, data)
        except OSError:
            self.close()

    def recv(self, buffer):
        data = asyncore.dispatcher_with_send.recv(self, buffer)
        if not data:
            if not self._backlog.empty():
                return self._backlog.get()
            else:
                return None
        if not isinstance(data, str):
            data = data.decode()
        elements = data.split(".")
        for item in elements:
            self._backlog.put(item)
        return self._backlog.get()


if __name__ == '__main__':
    server = Server("0.0.0.0", 64739)
    asyncore.loop()
