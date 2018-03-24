"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from network.minimap.server import MiniMapServer
from network.minimap.client import MiniMapClient
import random
import time


class TestMiniMapNetwork(TestCase):
    def setUp(self):
        self.port = random.randint(10000, 65535)
        self.server = MiniMapServer("localhost", self.port)

    def test_server_init(self):
        self.server.start()
        self.server.stop()

    def test_client_init(self):
        self.server.start()
        client = MiniMapClient("localhost", self.port, "user")
        client.start()
        time.sleep(2)
        self.assertEqual(len(self.server.client_sockets), 1)
        client.close()

    def tearDown(self):
        self.server.stop()


