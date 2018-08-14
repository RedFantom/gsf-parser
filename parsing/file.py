"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from multiprocessing import Process, Pipe, Event
from time import sleep
from typing import Any, Tuple
# Packages
from pypresence import Presence
# Project Modules
from data.abilities import REPUBLIC_SHIPS
from data.maps import MAP_TYPE_NAMES, MAP_NAMES
from data.servers import SERVERS
from network.discord import DiscordClient
from parsing import GSFInterface, LogStalker, Parser, ScreenParser, Ship
from parsing.guiparsing import get_player_guiname
import variables


class UnhandledException(Exception):
    """Exception the FileParser does not catch"""
    pass


class FileParser(Process):
    """
    Class that runs a LogStalker to parse individual CombatLog lines

    The FileParser runs in a separate Process and runs a loop that reads
    the most recent CombatLog through a LogStalker. This Process also
    manages a ScreenParser that runs in yet another Process.
    """

    def __init__(self, data_pipe, exit_event: Event, char_db: dict, char_i: tuple, **kwargs):
        """
        :param data_pipe: Pipe used for communication with the
            MainThread. Used for sending data, including the overlay
            and performance strings as well as event dictionaries.
        :param exit_event: Event that is set once the controlling
            Process requests this process and its children to exit.
        :param char_db, char_i: CharacterDatabase and character
            identifier to retrieve data with
        """
        self.kwargs = kwargs.copy()

        Process.__init__(self)

        self.options = variables.settings.dict()
        self.rpc: Presence = None
        self.discord: DiscordClient = None

        self.pipe, self.exit = data_pipe, exit_event
        self.char_db, self.char_i = char_db.copy(), char_i
        self.char_data = self.char_db[char_i]

        self.stalker = LogStalker(watching_callback=self.watching_callback)
        self.interface: GSFInterface = GSFInterface(get_player_guiname(*reversed(char_i)))

        self.dmg_d, self.dmg_t, self.dmg_s, self.healing, self.abilities = 0, 0, 0, 0, dict()
        self.active_id, self.active_ids, self.hold, = "", list(), list()
        self.player_name = ""

        self.is_match: bool = False
        self.tutorial: bool = False
        self.match_start: datetime = None

        self.screen: ScreenParser = None
        self.sc_pipe, self.sc_string = None, None

        self.ship: Ship = None
        self.map: Tuple[str, str] = None
        self.ship_config = True

        self.primary_weapon, self.secondary_weapon, self.scope_mode = False, False, False

    def watching_callback(self, file_name: str):
        """Callback for LogStalker to put new file in Pipe"""
        self.pipe.send(("file", file_name))

    def setup(self):
        """Initialize not yet initialized attributes in this Process"""
        if self.options["realtime"]["drp"]:
            self.rpc = Presence(436173115064713216)
        if self.options["sharing"]["enabled"]:
            self.discord = DiscordClient()
        if self.options["screen"]["enabled"]:
            self.sc_pipe, conn = Pipe()
            self.screen = ScreenParser(conn, self.exit, self.options, self.interface, **self.kwargs)
            self.screen.start()

    def cleanup(self):
        """Clean up the attributes initialized in setup"""
        if self.rpc is not None:
            self.rpc.close()
        if self.discord is not None:
            self.discord.close()

    def start(self):
        """Start the Process"""
        print("[FileParser] Starting Process...")
        Process.start(self)

    def run(self):
        """Run the Loop in the Process"""
        self.pipe.send(("pid", self.pid))
        self.setup()
        while True:
            if self.exit.is_set():
                break
            try:
                self.update()
            except Exception as e:  # Catch unhandled errors
                self.error(repr(e))
                break
        self.pipe.close()
        self.cleanup()
        print("[FileParser] Loop end")

    def update(self):
        """Run a single loop iteration"""
        start = datetime.now()
        lines = self.stalker.get_new_lines()
        for line in lines:
            if line is None:
                continue
            self.process_line(line)
        self.update_presence()
        self.update_screen_parser()
        self.pipe.send(("string", self.string))
        diff: float = (datetime.now() - start).total_seconds()
        if self.options["realtime"]["sleep"] is True and diff < 0.25:
            sleep(0.25 - diff)

    def update_presence(self):
        """Update the Rich Presence state"""
        if self.rpc is None:
            return
        if self.char_data["Discord"] is False:
            self.rpc.update(self.pid, "Activity Hidden", large_image="starfighter")
            return
        details = "{}: {}".format(self.char_data["Server"], self.player_name)
        if self.is_match is False:
            self.rpc.update(self.pid, "Out of Match", large_image="starfighter", details=details)
            return
        l_img, l_txt, s_img, s_txt = "starfighter", "Galactic StarFighter", None, None
        if self.map is not None:
            map_type, map_name = self.map
            l_txt = MAP_TYPE_NAMES[map_type][map_name]
            l_img = MAP_NAMES[l_txt]
        if self.ship is not None:
            s_img = self.ship.name.lower().replace(" ", "_")
            s_txt = self.ship.ship_name
        start = None
        if self.match_start is not None:
            start = self.match_start.timestamp()
        self.rpc.update(
            pid=self.pid, state="In Match", details=details, start=start,
            large_image=l_img, large_text=l_txt, small_image=s_img, small_text=s_txt)

    def process_line(self, line: dict):
        """Parse a single event dictionary"""
        if Parser.is_ignorable(line):
            return
        if Parser.is_login(line):
            self.handle_login(line)
        if self.is_match_end(line):
            self.handle_match_end(line)
            return
        if not self.is_match:
            if not Parser.is_gsf_event(line):
                return  # Out of match event
            self.handle_match_start(line)
        self.process_match_line(line)

    def process_match_line(self, line: dict):
        """Parse an event that is determined to be an in-match event"""
        if self.is_new_spawn(line):
            self.handle_spawn()
        self.update_player_id(line)
        if self.active_id == "":
            print("[FileParser] Holding line")
            self.hold.append(line)
            return
        self.parse_line(line)
        self.process_weapon_swap(line)
        self.update_ship()
        if self.match_start is None:
            print("[FileParser] Match start not set while event is match event")
            return
        self.pipe.send(("event", (line, self.player_name, self.active_ids, self.match_start)))
        if self.sc_pipe is not None:
            self.sc_pipe.send(("event", (line, self.player_name, self.active_ids, self.match_start)))

    def process_weapon_swap(self, line: dict):
        """Check if the line includes a weapon swap event"""
        if line["ability"] == "Scope Mode":
            self.scope_mode = True
        elif "Weapon Swap" in line["ability"]:
            weapon_type: str = line["ability"].split(" ", 1)[0]
            attr = "{}_weapon".format(weapon_type.lower())
            setattr(self, attr, not getattr(self, attr))
            if self.sc_pipe is not None:
                self.sc_pipe.send(("swap", attr))

    def parse_line(self, line: dict):
        """Parse the line for interesting data"""
        if Parser.is_tutorial_event(line):
            self.tutorial = True
        if "Heal" in line["effect"] and line["target"] == self.active_id:
            self.healing += line["damage"]
        elif "Damage" in line["effect"]:
            if line["ability"] == "Selfdamage":
                self.dmg_s += line["damage"]
            elif line["source"] == self.active_id:
                self.dmg_d += line["damage"]
            else:
                self.dmg_t += line["damage"]

        if line["ability"] not in self.abilities:
            self.abilities[line["ability"]] = 0
        self.abilities[line["ability"]] += 1

    def is_new_spawn(self, line: dict):
        """Determine whether a line indicates a new spawn"""
        return self.active_id not in (line["source"], line["target"])

    def is_match_end(self, line: dict):
        """Determine whether this line is the end of a match"""
        return self.is_match and not Parser.is_gsf_event(line)

    def handle_login(self, line: dict):
        """Handle a Login event: Update the character data selected"""
        self.player_name = line["source"].strip("@")
        print("[FileParser] Player Login: {}".format(self.player_name))
        if self.player_name != self.char_i[1]:
            self.char_i = (self.char_i[0], self.player_name)
            if self.char_i not in self.char_db:
                self.error("Character not present in database")
                return
            self.char_data = self.char_db[self.char_i]

    def handle_match_end(self, line: dict):
        """Handle the end of a match: Reset data attributes"""
        print("[FileParser] Match end: {}".format(line["line"]))
        self.is_match, self.tutorial, self.ship_config = False, False, True
        self.abilities.clear()
        self.dmg_d, self.dmg_t, self.dmg_s, self.healing = 0, 0, 0, 0
        self.primary_weapon, self.secondary_weapon, self.scope_mode = False, False, False
        if self.discord is not None:
            server, date, time = self.char_data["Server"], self.match_start, line["time"]
            self.discord.send_match_end(server, date, self.match_start, self.active_id[:8], time)
        self.match_start = None

    def handle_match_start(self, line: dict):
        """Handle the start of a match"""
        print("[FileParser] Match start")
        self.match_start = datetime.combine(datetime.now().date(), line["time"].time())
        self.is_match = True
        self.pipe.send(("match", self.match_start))

    def handle_spawn(self):
        """Handle a new spawn"""
        self.abilities.clear()
        self.active_id = ""
        self.primary_weapon, self.secondary_weapon, self.scope_mode = False, False, False
        self.ship, self.ship_config = None, True
        self.pipe.send(("spawn", None))

    def update_player_id(self, line: dict):
        """Attempt to update the active player ID from an event"""
        if self.active_id != "" or line["source"] != line["target"]:
            return  # Active ID already set or new ID unknown
        self.active_id = line["source"]
        if self.sc_pipe is not None:
            self.sc_pipe.send(("id", self.active_id))
        print("[FileParser] Player ID: {}".format(self.active_id))
        self.active_ids.append(line["source"])
        if self.discord is not None:
            server, date, start = self.char_data["Server"], self.match_start, self.match_start
            self.discord.send_match_start(server, date, start, self.active_id[:8])
        for line in reversed(self.hold):
            self.process_line(line)
        self.hold.clear()

    def update_ship(self):
        """Update the ship if necessary based on the abilities"""
        if self.screen is None or self.ship is not None:
            return
        ships = Parser.get_ship_for_dict(self.abilities.copy())
        if len(ships) > 1:
            return  # Multiple possible ships
        elif len(ships) == 0:
            print("[FileParser] No ships possible: {}".format(self.abilities))
            self.abilities.clear()  # Safety mechanism
            return
        name = ships[0]
        if self.char_data["Faction"].lower() == "republic":
            name = REPUBLIC_SHIPS[name]
        ship_obj: Ship = self.char_data["Ship Objects"][name]
        if ship_obj is None:
            self.ship_config = False

    def update_screen_parser(self):
        """Update the screen parser: Receive and handle data from it"""
        if self.screen is None or self.sc_pipe is None:
            return
        while self.sc_pipe.poll():
            self.process_screen_data(self.sc_pipe.recv())

    def process_screen_data(self, data: Tuple[str, Any]):
        """Process data received from the screen parser Pipe"""
        type, data = data
        if type == "error":
            self.error(data)
        elif type == "map":
            self.map = data
        elif type == "string":
            self.sc_string = data
        elif type == "config":
            self.ship_config = False
        elif type == "event":
            self.pipe.send(("event", (data, self.player_name, self.active_ids, self.match_start)))
        else:
            self.pipe.send((type, data))

    def error(self, message: str):
        """Exit the Process with an error message"""
        self.pipe.send(("error", message))
        raise UnhandledException(message)

    @property
    def string(self) -> str:
        """Build a nicely formatted string for in the overlay"""
        char_string = \
            "Character: {}\n".format(self.player_name) + \
            "Server: {}\n".format(SERVERS[self.char_data["Server"]])
        if self.is_match is False:
            return char_string
        ship = "Unknown"
        if self.ship is not None:
            ship = self.ship.name
            if self.ship_config is False:
                ship += " (Not fully configured)"
        string = \
            char_string + \
            "Ship: {}\n".format(ship) + \
            "\n" \
            "Damage dealt: {}\n" \
            "Damage taken: {}\n" \
            "Selfdamage: {}\n" \
            "Healing received: {}\n".format(
                self.dmg_d, self.dmg_t, self.dmg_s, self.healing)
        if self.sc_string is not None:
            string += self.sc_string
        return string
