# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import unittest
import time
from parsing import stalking_alt as stalking
from parsing import realtime
import os
from tools import utilities


class TestRealtimeParsing(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(utilities.get_assets_directory(), "logs", "CombatLog.txt")) as log:
            self.lines = log.readlines()
        self.stalking_lines = []
        self.stalker = stalking.LogStalker(callback=self.line_callback, newfilecallback=self.new_file_callback)
        self.rlt = realtime.Parser(spawn_callback=self.spawn_callback,
                                   match_callback=self.match_callback,
                                   new_match_callback=self.new_match_callback,
                                   insert=self.insert)
        self.stalker.start()

    def tearDown(self):
        self.stalker.FLAG = False
        time.sleep(5)
        self.assertFalse(self.stalker.is_alive())

    def test_realtime_parsing(self):
        pass

    '''
    def test_stalking(self):
        log = open((os.path.expanduser("~") + "\\Documents\\Star Wars - The Old Republic\\CombatLogs\\").
                    replace("\\", "/") + "combat_2017-04-27_12_00_00_000000.txt", "w")
        for line in self.lines:
            print "Wrote: ", line.replace("\n", "")
            log.write(line)
            time.sleep(5.0)
            self.assertTrue(line in self.stalking_lines)
        log.close()
    '''

    def insert(self, *args):
        pass

    def line_callback(self, lines):
        for line in lines:
            self.rlt.parse(line, False)

    def stalking_callback(self, lines):
        for line in lines:
            print "Read: ", line.replace("\n", "")
            self.stalking_lines.append(line)

    def spawn_callback(self, *args):
        self.spawn = True

    def match_callback(self, *args):
        self.match = False
        self.spawn = False

    def new_match_callback(self, *args):
        self.match = True

    def new_file_callback(self, *args):
        pass
