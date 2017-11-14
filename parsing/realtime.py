﻿# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Written by Daethyra, edited by RedFantom
from decimal import Decimal
import datetime
import re
from tkinter.messagebox import showerror
import variables
from tools.utilities import write_debug_log


class Parser(object):
    """Parse a SWTOR combat log file. Each instance is a different
    file. The parser is designed for GSF battles

    For each statistic (damage done, taken and self damage, healing
    recieved, abilities used, critical luck) there is a list where
    each element is the respective amount done per match.
    (=> length of list = # of matches)

    The elements of these lists are themselves a list where the elements represent
    the spawns. The only elements not to be a list are abilites and crit luck,
    which are a tuple and a dictionary respectively.
    (=> length of list = # of spawns)

    The abilities dictionary has as key the name of the ability and
    as value a ?list/dictionary? containing the respective amount for each statistic.
    This dictionary is then stored in the list abilities for each match.

    The crit luck tuple contains the absolute amount of critical hit,
    and the relative amount #critcal hit / #hit.
    There is no specific crit luck information per spawn. This is
    calculated only per match.

    To clarify which list is what, here is a short reference:
    :var: spawn_* is the list updated live
    :var: tmp_* is the list of the live match, containing infos per spawn
    :var: * is the list of the parse, containing infos per match
    """

    DEBUG = False

    def __init__(self, spawn_callback, match_callback, new_match_callback, insert, screen=False, screenoverlay=False,
                 ship=None, screen_parser=None, data_queue=None, return_queue=None):
        if screen is False and screenoverlay is True:
            showerror("Error", "Screen parsing disabled but screen parsing overlay enabled.")
            raise ValueError("screenoverlay True but screen False")
        if screen is True and ship is None:
            # showerror("Error", "Screen parsing enabled but no ship object acquired.")
            # raise ValueError("screen True but ship None")
            pass

        self.screen_parser = screen_parser
        self.data_queue = data_queue
        self.return_queue = return_queue
        if self.screen_parser is not None and self.data_queue is not None:
            self.screenparser = True
        self.player_name = ''
        self.crit_nr = 0
        self.is_match = False

        self.spawn_callback = spawn_callback  # Function to call when a new spawn is detected
        self.match_callback = match_callback  # Function to call when the end of a match is detected
        self.new_match_callback = new_match_callback  # Function to call when a new match is detected
        self.insert = insert  # Function to call when a new line is parsed to insert it into the events box of the UI

        self.abilities, self.dmg_done, self.dmg_taken = [], [], []
        self.healing_rcvd, self.self_dmg, self.crit_luck = [], [], []
        self.recent_enemies = {}

        self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd = [], [], []
        self.tmp_selfdmg = []
        self.tmp_abilities = {}

        self.spawn_dmg_done, self.spawn_dmg_taken = [], []
        self.spawn_healing_rcvd, self.spawn_selfdmg = [], []

        self.active_id = ''
        self.active_ids = []

        self.hold = 0
        self.hold_list = []

        self.spawns = 0  # The amount of spawns so far

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def parse(self, line, recursion=False):
        write_debug_log("Parser.parse function called with line: %s" % line)
        self.dprint("[DEBUG] line", line)
        if not line:
            print("[DEBUG] Line is of NoneType")
            return
        if self.screenparser:
            self.screen_parser.line_queue.put((line, self.active_id))

        if "SetLevel" in line:
            return

        # This block is for keeping track of recent enemies, but it causes RuntimeErrors
        # time_now = datetime.datetime.now()
        # for enemy, time in self.recent_enemies.iteritems():
        #    # Remove enemies that weren't registered in last ten seconds
        #    if (time_now - time).seconds >= 10:
        #        del self.recent_enemies[enemy]

        # If first line of the file, save the player name
        if self.player_name == '' and '@' in line['source']:
            self.player_name = line['source'][1:]
            variables.rt_name = self.player_name
            print(self.player_name)
        # Sometimes multiple log-ins are stored in one log
        # Then the player_name must be changed if it is a self-targeted ability
        if line['source'] == line['destination'] and "@" not in line['source'] and ":" not in line['source'] and \
                not bool(re.search(r'\d', line['source'])):
            if line['source'][1:] != self.player_name:
                self.player_name = line['source'][1:]
                variables.rt_name = self.player_name
                print(self.player_name)

        if not self.is_match and ('@' in line['source'] or '@' in line['destination']):
            self.dprint("[DEBUG] out of match, skip")
            return

        # if the active id is neither source nor destination, the player id has changed
        # meaning a new spawn.
        if self.active_id not in line['source'] and self.active_id not in line['destination']:
            print(("[NEW SPAWN]", sum(self.spawn_dmg_done), sum(self.spawn_dmg_taken), sum(self.spawn_healing_rcvd),
                   sum(self.spawn_selfdmg)))
            # Call the new spawn callback
            time = datetime.datetime.strptime(line['time'][:-4], "%H:%M:%S")
            self.data_queue.put(("spawn", time))
            self.spawn_callback(self.spawn_dmg_done, self.spawn_dmg_taken, self.spawn_healing_rcvd, self.spawn_selfdmg)
            self.spawns += 1
            self.active_id = ''
            self.dprint("[DEBUG] resetting active id")
            self.dprint("[DEBUG] updating tmp_* and resetting spawn_*", self.spawn_dmg_done, sum(self.spawn_dmg_done))
            self.tmp_dmg_done.append(sum(self.spawn_dmg_done))
            self.tmp_dmg_taken.append(sum(self.spawn_dmg_taken))
            self.tmp_healing_rcvd.append(sum(self.spawn_healing_rcvd))
            self.tmp_selfdmg.append(sum(self.spawn_selfdmg))
            self.spawn_dmg_done, self.spawn_dmg_taken = [], []
            self.spawn_healing_rcvd, self.spawn_selfdmg = [], []
            self.dprint("[DEBUG] tmp_* updated", self.tmp_dmg_done)

        # if a self targeted ability update the active player id
        if line['source'] == line['destination']:
            self.dprint("[DEBUG] setting active id")
            self.active_id = line['source']
            if self.active_id not in self.active_ids:
                self.active_ids.append(self.active_id)

        self.dprint("[DEBUG] active id \'", self.active_id, "\'")

        # Insert the line (or the pretty version of it) into the events box of real-time parsing
        self.insert(line, variables.rt_timing, self.active_id)

        # if the active player id is emtpy, it is impossible to determine if
        # player is target or source, thus put this line on hold and return.
        # elif there is and active id and lines on hold, parse them again.
        if self.active_id is '':
            self.hold += 1
            self.hold_list.append(line)
            self.dprint("[DEBUG] hold", self.hold, self.hold_list)
            return
        elif self.active_id is not '' and self.hold > 0 and not recursion:
            self.dprint("[DEBUG] catching up")
            for elem in self.hold_list:
                self.parse(elem, recursion=True)
                self.hold_list = self.hold_list[1:]
            self.hold = 0
            self.dprint("[DEBUG] caught up")
            return

        self.dprint("[DEBUG] hold", self.hold)

        # start of a match
        if not self.is_match and '@' not in line['source']:
            self.is_match = True
            # Call the callback for a new match
            self.new_match_callback()
            time = datetime.datetime.strptime(line['time'][:-4], "%H:%M:%S")
            variables.rt_timing = time
            if self.screenparser:
                write_debug_log("Parser announcing new match to ScreenParser")
                self.data_queue.put(("match", True, time))

        if self.is_match:
            if '@' in line['source']:
                if "Safe Login" not in line['ability']:
                    self.dprint("[DEBUG] Line with '@' but no end of match detected")
                    return
                self.dprint("[DEBUG] end of match, resetting")
                # Call the end of match callback
                self.match_callback(self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd, self.tmp_selfdmg)
                self.dprint("[DEBUG]", self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd, self.tmp_selfdmg)
                print(("[END OF MATCH]", sum(self.tmp_dmg_done), sum(self.tmp_dmg_taken), sum(self.tmp_healing_rcvd),
                       sum(self.tmp_selfdmg)))
                self.is_match = False
                self.dmg_done.append(self.tmp_dmg_done)
                self.dmg_taken.append(self.tmp_dmg_taken)
                self.healing_rcvd.append(self.tmp_healing_rcvd)
                self.self_dmg.append(self.tmp_selfdmg)
                self.abilities.append(self.tmp_abilities)

                try:
                    crits = Decimal(float(self.crit_nr) / len(self.tmp_dmg_done))
                except ZeroDivisionError:
                    crits = 0
                crits = round(crits * 100, 1)
                self.crit_luck.append((self.crit_nr, crits))

                self.crit_nr = 0
                self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd = [], [], []
                self.tmp_selfdmg = []
                self.tmp_abilities = {}
                self.active_id = ''
                self.spawns = 1
                self.active_ids = []
                # self.recent_enemies.clear()
                if self.screenparser:
                    write_debug_log("Parser announcing end of match to ScreenParser")
                    time = datetime.datetime.strptime(line['time'][:-4], "%H:%M:%S")
                    self.data_queue.put(("match", False, time))
                return

            # Start parsing
            if 'Heal' in line['effect']:
                self.spawn_healing_rcvd.append(int(line['amount'].replace('*', '')))
                self.dprint("[DEBUG] heal", self.spawn_healing_rcvd)

            elif 'Damage' in line['effect']:
                if not line['amount'] is '':
                    if 'Selfdamage' in line['ability']:
                        self.spawn_selfdmg.append(int(line['amount'].replace('*', '')))
                        self.dprint("[DEBUG] self damage", self.spawn_selfdmg)

                    elif line['source'] in self.active_id:
                        if '*' in line['amount']:
                            self.crit_nr += 1

                        if line['amount'] is not '0':
                            self.spawn_dmg_done.append(int(line['amount'].replace('*', '')))
                            self.dprint("[DEBUG] damage done", self.spawn_dmg_done)
                    else:
                        self.spawn_dmg_taken.append(int(line['amount'].replace('*', '')))
                        self.dprint("[DEBUG] damage taken", self.spawn_dmg_taken)
                        # self.recent_enemies[line['destination']] = \
                        #    datetime.datetime.strptime(line['time'][:-4], "%H:%M:%S")

            if line['ability'] in self.tmp_abilities:
                self.tmp_abilities[line['ability']] += 1
            else:
                self.tmp_abilities[line['ability']] = 1

    def close(self):
        pass

    def dprint(self, *args):
        if self.DEBUG:
            print(args)

    def new_file(self, filename):
        if self.screenparser:
            self.data_queue.put(("file", filename))
