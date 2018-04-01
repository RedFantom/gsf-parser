"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from network import MiniMapServer, MiniMapClient
from network import StrategyServer, StrategyClient
from network import SharingServer, SharingClient
from widgets.strategy import StrategiesList
import tkinter as tk
import random
import time
from datetime import datetime


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


class TestStrategyNetwork(TestCase):
    def setUp(self):
        self.port = random.randint(10000, 65535)
        self.server = StrategyServer("localhost", self.port)
        self.disconnect = False
        self.login = False
        self.insert = 0

    def test_server(self):
        self.server.start()
        self.server.stop()

    def test_client(self):
        self.server.start()
        client = StrategyClient(
            "localhost", self.port, "user",
            list=None,
            disconnectcallback=self.disconnect_callback,
            logincallback=self.login_callback,
            insertcallback=self.insert_callback,
            role="master"
        )
        client.start()
        client.connect()
        start = datetime.now()
        while self.login is False and (datetime.now() - start).total_seconds() < 4:
            pass
        self.assertTrue(self.login)
        client.close()

    def tearDown(self):
        self.server.stop()

    def disconnect_callback(self):
        self.disconnect = True

    def login_callback(self, success: bool):
        self.login = success

    def insert_callback(self, *args):
        self.insert += 1


