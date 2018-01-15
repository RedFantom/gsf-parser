"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from utils import directories
from os import path


class TestDirectories(TestCase):
    def test_get_temp_directory(self):
        temp_dir = directories.get_temp_directory()
        self.assertIsInstance(temp_dir, str)
        self.assertTrue(path.exists(temp_dir))

    def test_get_assets_directory(self):
        assets_dir = directories.get_assets_directory()
        self.assertIsInstance(assets_dir, str)
        self.assertTrue(path.exists(assets_dir))

    def test_get_combatlogs_folder(self):
        combatlogs_dir = directories.get_combatlogs_folder()
        self.assertIsInstance(combatlogs_dir, str)
