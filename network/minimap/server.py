"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import socket
import threading
from queue import Queue
from select import select
from ast import literal_eval
from network.connection import Connection


class MiniMapServer(threading.Thread):
    """
    Server for MiniMap location sharing. Passes on all locations
    to all Clients. No security is provided.
    """
    def __init__(self, host: str, port: int):
        """
        :param host: hostname to bind to
        :param port: port to bind to
        """
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0)
        self.socket.setblocking(False)
        self.socket.bind((host, port))
        self.client_sockets = list()
        self.client_names = dict()
        self.exit_queue = Queue()
        self.banned = list()

    def run(self):
        """
        Receive commands from the various clients and distribute their
        commands to the other Clients on the Server. This Server
        DOES NOT support banning or any form of user control at the
        moment.
        """
        self.socket.listen(12)

        while True:
            if not self.exit_queue.empty() and self.exit_queue.get() is True:
                print("[MiniMapServer] Exit signal received.")
                break
            self.accept_clients()
            self.update_clients()
        for client in self.client_sockets:
            client.close("exit")

    def update_clients(self):
        """Get location information from Clients"""
        for client in self.client_sockets.copy():
            try:
                message = client.get_message()
            except socket.timeout:
                continue

            # Logout Clients
            if message == "logout":
                self.client_sockets.remove(client)
                name = self.client_names[client]
                for client_alt in self.client_sockets:
                    client_alt.send("logout_{}".format(name))
                del self.client_names[client]
                continue

            # Update location
            elems = message.split("_")
            if len(elems) != 3 or elems[0] != "location":
                raise RuntimeError("Unsupported command: {}".format(message))
            _, name, location_tuple = elems
            # Safely evaluate location_tuple
            tup = literal_eval(location_tuple)
            assert isinstance(tup, tuple)
            assert len(tup) == 2
            # Send location update to other clients
            iterator = self.client_sockets.copy()
            iterator.remove(client)
            for other in iterator:
                other.send(message)
        # Done
        return True

    def accept_clients(self):
        """Accept new Clients if the Socket is ready"""
        if self.socket in select([self.socket], [], [], 0)[0]:
            print("[MiniMapServer] Accepting new Client.")
            conn, addr = self.socket.accept()
            if addr in self.banned:
                print("[MiniMapServer] Banned Client attempted to connect: {}".format(addr))
                conn.close()
                return False
            # Login procedure
            self.login_client(conn, addr)
        return True

    def login_client(self, conn, addr):
        """Log a Client into the Server if it gives the right commands"""
        conn = Connection(sock=conn)
        mess = conn.get_message()
        if mess is None:
            return
        elems = mess.split("_")
        # elems: ("login", username: str)
        if len(elems) != 2 or elems[0] != "login" or elems[1] in self.client_names.values():
            conn.close("exit")
        # Login succeed
        for client in self.client_sockets:
            client.send(mess)  # login_username
        conn.send("login")  # Confirmation
        # Save connection
        self.client_sockets.append(conn)
        self.client_names[conn] = elems[1]

    def stop(self):
        """Stop the Server's activities"""
        self.exit_queue.put(True)
