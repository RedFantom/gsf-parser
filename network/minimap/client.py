"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from network.client import Client
from queue import Queue


health_colors = {
    100: "green",
    75: "yellow",
    50: "orange",
    25: "red",
    0: "black"
}


class MiniMapClient(Client):
    """
    Supports connecting to a server and sending the player location to
    a server. Uses a callback that can be called to put a location
    in the queue to be sent.
    """

    supported_commands = [
        "login",
        "logout",
        "location",
        "health",
    ]

    def __init__(self, host: str, port: int, username: str):
        """Sets up the client, connects and logs into the server"""
        Client.__init__(self, host, port)
        self.location_queue = Queue()
        self.health_queue = Queue()
        self.connect()
        self.login(username)
        self._user = username

    def login(self, username: str):
        """Login to the server after the connection has been setup"""
        self.send("login_{}".format(username))
        message = self.get_message()
        if message != "login":
            raise RuntimeError("Unsupported response: {}".format(message))
        return True

    def update(self):
        """Periodically send the location to the server"""
        self.receive()
        if self.location_queue.empty():
            return
        location = None
        health = None
        while not self.health_queue.empty():
            health = self.health_queue.get()
        while not self.location_queue.empty():
            location = self.location_queue.get()
        if health is None or location is None:
            print("[MiniMapClient] Invalid values for health or location: {}, {}".format(health, location))
            return
        self.send("location_{}_{}".format(self._user, location))
        self.send("health_{}_{}".format(self._user, health))

    def send_location(self, location: tuple):
        """Send a location tuple"""
        assert isinstance(location, tuple)
        assert len(location) == 2
        if location[0] is None:
            return
        self.location_queue.put(location)

    def send_health(self, health: (str, int)):
        """Send a health value"""
        if not isinstance(health, str):
            health = health_colors[int(health)]
        self.health_queue.put(health)

    def close(self):
        """Logout and close"""
        self.send("logout")
        Client.close(self)

