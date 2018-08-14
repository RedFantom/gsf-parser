"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from parsing.thread import *

from parsing.characters import CharacterDatabase
from parsing.filehandler import FileHandler
from parsing.filestats import file_statistics
from parsing.folderstats import folder_statistics
from parsing.gsfinterface import GSFInterface
from parsing.guiparsing import GUIParser, get_player_guiname
from parsing.imageops import get_brightest_pixel, get_similarity, get_similarity_pixels
from parsing.logstalker import LogStalker
from parsing.matchstats import match_statistics
from parsing.parser import Parser
from parsing.realtime import RealTimeParser
from parsing.realtimedb import RealTimeDB
from parsing.ships import Ship, Component
from parsing.shipstats import ShipStats
from parsing.spawnstats import spawn_statistics
from parsing.strategies import Strategy, StrategyDatabase, Phase
from parsing.timer import TimerParser
from parsing.vision import *
