import asyncore
import socket
from queue import Queue


class Client(asyncore.dispatcher_with_send):
    def __init__(self, sock, host, port):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.connect((host, port))
        self._backlog = Queue()

    def handle_accepted(self, socket, address):
        print("Client was accepted by the Server")

    def handle_read(self):
        data = self.recv(8192)
        print("Client received the following data: ", data)

    def login(self, role, name):
        assert isinstance(role, str) and isinstance(name, str)
        assert role is "master" or role is "client"
        assert len(name) >= 1
        self.send("role={0}".format(role).encode())
        self.send("name={0}".format(name).encode())

    def send(self, data):
        if not isinstance(data, str):
            data = data.decode()
        data = (data + ".").encode()
        asyncore.dispatcher_with_send.send(self, data)

    def recv(self, buffer):
        data = asyncore.dispatcher_with_send.recv(self, buffer)
        if not data:
            if not self._backlog.empty():
                return self._backlog.get()
            else:
                return None
        elements = data.split(".")
        for item in elements:
            self._backlog.put(item)
        return self._backlog.get()

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = Client(sock, "127.0.0.1", 64739)
    client.login("master", "RedFantom")
    asyncore.loop()


