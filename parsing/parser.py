# A new parsing engine built by RedFantom based on principles from parse.py and realtime.py
# Is capable of parsing files as well as realtime parsing
import re
import os
from datetime import datetime
# Own modules
from parsing.lineops import line_to_dictionary
from parsing.screen import ScreenParser, FileHandler


class Parser(object):
    """
    A Parsing engine that can sequentially parse CombatLog lines and supports staticmethods for parsing individual
    spawns and matches to keep some backwards compatibility with the functions found in parse.py. Replaces the Parsing
    engine found in realtime.py.

    Capabilities:
    - Determine player name and IDs
    - Count damage and healing
    - Count hits and critical hits
    - Parse screenshots separately
    - In real-time mode, determine hits/misses
    - Determine ship and components
    - Count ability usage
    - Save build data for a match and read it when required
    - Manage a spawn events Treeview
    """
    def __init__(self):
        pass
