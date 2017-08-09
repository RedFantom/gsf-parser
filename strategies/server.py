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
from strategies.clienthandler import ClientHandler
from tools.admin import is_user_admin
from tools.utilities import get_temp_directory


class Server(threading.Thread):
    def __init__(self, host, port):
        if not is_user_admin():
            raise RuntimeError("Attempted to open a server while user is not admin.")
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(4)
        if not Server.check_host_validity(host, port):
            raise ValueError("The host or port value is not valid: {0}:{1}".format(host, port))
        try:
            self.socket.bind((host, port))
        except socket.error:
            raise RuntimeError("Binding to the address and port failed.")
        self.client_handlers = []
        self.exit_queue = Queue()
        self.server_queue = Queue()
        self.master_handler = None

    def run(self):
        if not socket.getdefaulttimeout() == 4:
            raise ValueError()
        self.socket.listen(8)
        while True:
            if not self.exit_queue.empty():
                if self.exit_queue.get():
                    print("Strategy server is exiting loop")
                    break
            if self.socket in select([self.socket], [], [], 0)[0]:
                connection, address = self.socket.accept()
                self.client_handlers.append(ClientHandler(connection, address, self.server_queue))
            else:
                continue
            for client_handler in self.client_handlers:
                client_handler.update()
            if not self.server_queue.empty():
                message = self.server_queue.get()
                if isinstance(message, tuple) and len(message) == 2 and isinstance(message[1], ClientHandler):
                    if message[0] == "master_login":
                        if self.master_handler:
                            raise RuntimeError("master_login but master_handler already set to: {0}".
                                               format(self.master_handler.name))
                        self.master_handler = message[1]
                    elif message[0] == "client_login":
                        self.master_handler.client_queue.put("client_login_{0}".format(message[1].name))
                    else:
                        raise ValueError("Unknown command format found: {0}".format(message))
                else:
                    for client_handler in self.client_handlers:
                        if client_handler is self.master_handler:
                            continue
                        client_handler.client_queue.put(message)
            continue
        for client_handler in self.client_handlers:
            client_handler.close()
        print("Strategy server is returning from run()")
        return

    def do_action_for_client_handler(self, client_handler, command):
        if not self.is_alive():
            raise RuntimeError("Attempted to perform action {0} for client_handler {1} while server is not running.".
                               format(command, client_handler))

    @staticmethod
    def check_host_validity(host, port):
        if not isinstance(host, str) or not isinstance(port, int):
            return False
        elements = host.split(".")
        if not len(elements) == 4:
            return False
        for item in elements:
            try:
                int(item)
            except TypeError:
                return False
        if not port < 9999:
            return False
        return True

    @staticmethod
    def write_log(line):
        with open(os.path.join(get_temp_directory(), "strategy_server.log"), "a") as fo:
            fo.write("[{0}] {1}".format(datetime.now().strftime("%H:%M:%S"), line))

if __name__ == '__main__':
    Server("", 6500).start()
