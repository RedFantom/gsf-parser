"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from unittest import TestCase
import _pickle as pickle
import os
# Project Modules
from parsing.strategies import StrategyDatabase, Strategy, Phase, Item
from utils.directories import get_assets_directory


class TestStrategyDatabase(TestCase):
    Strategy = Strategy("strategy", ("dom", "km"))
    files = ["db1.db", "db2.db", "strategies.bak.db"]

    def setUp(self):
        self.db = StrategyDatabase()

    def test_file_name_kwarg(self):
        StrategyDatabase(file_name="strategies.bak.db")

    def test_add_strategy(self):
        self.db["strategy"] = self.Strategy
        self.assertRaises(ValueError, lambda: self.db.__setitem__("strategy", {"strategy": "some_data"}))

    def test_del_strategy(self):
        self.db["strategy"] = self.Strategy
        del self.db["strategy"]

    def test_merge_database(self):
        strategies = {
            "strategy1": Strategy("one", ("dom", "km")),
            "strategy2": Strategy("two", ("dom", "km"))
        }
        db1 = StrategyDatabase(file_name="db1.db")
        db2 = StrategyDatabase(file_name="db2.db")
        db1["strategy1"] = strategies["strategy1"]
        db2["strategy2"] = strategies["strategy2"]
        db1.merge_database(db2)
        self.assertTrue("strategy2" in db1)

    def tearDown(self):
        for name in self.files:
            if not os.path.exists(name):
                continue
            os.remove(name)


class TestStrategy(TestCase):
    def setUp(self):
        with open(os.path.join(get_assets_directory(), "sample.str"), "rb") as fi:
            self.strategy = pickle.load(fi)

    def test_serialize(self):
        self.assertIsInstance(self.strategy, Strategy)
        self.assertIsInstance(self.strategy.serialize(), str)

    def test_deserialize(self):
        serialized = self.strategy.serialize()
        strategy = Strategy.deserialize(serialized)
        self.assertIsInstance(strategy, Strategy)
        for phase_name, phase in self.strategy.phases.items():
            self.assertTrue(phase_name in strategy.phases)
            for item_key, item in phase.items.items():
                self.assertTrue(item_key in strategy[phase_name].items)
                self.assertIsInstance(item, Item)
            self.assertIsInstance(phase, Phase)
