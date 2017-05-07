# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
try:
    import mttkinter.mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import tkMessageBox
import tkSimpleDialog
import time
import platform
from Queue import Queue
import variables
from parsing import stalking_alt, realtime, lineops
from toplevels import RealtimeOverlay
from utilities import write_debug_log
from parsing.screen import ScreenParser


class realtime_frame(ttk.Frame):
    """
    A frame that contains all buttons and widgets involved in real-time parsing
    Callbacks for the buttons control the parsing and a listbox displays the events
    that have been recorded in the real-time parsing process

    --------------------------------------------------------------------------
    | ________________  ________________  ________________  ________________ |
    | |Start parsing |  |Start upload  |  |Server dropd  |  |Faction dropd | |
    |                                                                        |
    | ________________  ________________  Stastics string                    |
    | | parsing bar  |  |uploading bar |  Stastics string                    |
    | ______________________________________________________________________ |
    | | event                                                          |/\|| |
    | | event                                                          ||||| |
    | | event                                                          |  || |
    | |________________________________________________________________|\/|| |
    | Watching string                                                        |
    --------------------------------------------------------------------------
    """

    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.parser = None
        self.overlay = None
        self.main_window = main_window
        self.listbox = tk.Listbox(self, width=105, height=15)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set, font=("Consolas", 10))
        self.statistics_list_label_one = ttk.Label(self, justify=tk.LEFT, text="Damage dealt:\nDamage taken:\n" + \
                                                                               "Selfdamage:\nHealing received:\nSpawns:")
        self.statistics_list_label_two = ttk.Label(self, justify=tk.LEFT, text="Abilities:")
        self.statistics_label_one_text = tk.StringVar()
        self.statistics_label_one = ttk.Label(self, textvariable=self.statistics_label_one_text, justify=tk.LEFT)
        self.start_parsing_button = ttk.Button(self, text="Start real-time parsing", command=self.start_parsing,
                                               width=25)
        self.upload_results_button = ttk.Button(self, text="Start uploading events", command=self.upload_events,
                                                width=25)
        self.server = tk.StringVar()
        self.faction = tk.StringVar()
        self.faction_list = ttk.OptionMenu(self, self.faction,
                                           "Select a faction",
                                           "Imperial Faction",
                                           "Republic Faction")
        self.server_list = ttk.OptionMenu(self, self.server,
                                          "Select a server",
                                          "The Bastion",
                                          "Begeren Colony",
                                          "The Harbinger",
                                          "The Shadowlands",
                                          "Jung Ma",
                                          "The Ebon Hawk",
                                          "Prophecy of the Five",
                                          "Jedi Covenant",
                                          "T3-M4",
                                          "Darth Nihilus",
                                          "The Tomb of Freedon Nadd",
                                          "Jar'kai Sword",
                                          "The Progenitor",
                                          "Vanjervalis Chain",
                                          "Battle Meditation",
                                          "Mantle of the Force",
                                          "The Red Eclipse")
        self.parsing = False
        self.parse = []
        self.parsing_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="indeterminate")
        self.uploading_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="indeterminate")
        self.watching_stringvar = tk.StringVar()
        self.watching_label = ttk.Label(self, textvariable=self.watching_stringvar, justify=tk.LEFT)
        self.watching_stringvar.set("Watching no CombatLog...")

    def start_parsing(self):
        if not self.parsing:
            # self.main_window.file_select_frame.add_files()
            # self.start_parsing_button.config(relief=tk.SUNKEN)
            self.parsing = True
            self.main_window.after(100, self.insert)
            if variables.settings_obj.screenparsing:
                self.data_queue = Queue()
                self.exit_queue = Queue()
                self.query_queue = Queue()
                self.return_queue = Queue()
                self.return_queue.put(0)
                self.screenparser = ScreenParser(data_queue=self.data_queue, exit_queue=self.exit_queue,
                                                 query_queue=self.query_queue, return_queue=self.return_queue)
                self.screenparser.start()
            else:
                self.screenparser = None
                self.data_queue = None
            self.parser = realtime.Parser(self.spawn_callback, self.match_callback, self.new_match_callback,
                                          lineops.pretty_event, screen=variables.settings_obj.screenparsing,
                                          screenoverlay=variables.settings_obj.screenparsing_overlay,
                                          data_queue=self.data_queue)
            self.stalker_obj = stalking_alt.LogStalker(callback=self.callback,
                                                       folder=variables.settings_obj.cl_path,
                                                       watching_stringvar=self.watching_stringvar,
                                                       newfilecallback=self.parser.new_file)
            variables.FLAG = True
            if variables.settings_obj.overlay and not variables.settings_obj.overlay_when_gsf:
                self.overlay = RealtimeOverlay(self.main_window)
            self.parsing_bar.start(3)
            self.start_parsing_button.configure(text="Stop real-time parsing")
            self.stalker_obj.start()
            self.stalking_exit_queue = self.stalker_obj.exit_queue
        elif self.parsing:
            print "[DEBUG] Detected Windows version: ", platform.release()
            if (platform.release() != "10" and platform.release() != "8" and platform.release() != "8.1"
               and platform.release().lower() != "post2008Server".lower()):
                self.main_window.file_select_frame.add_files_cb()
            write_debug_log("Stopping real-time parsing")
            self.exit_queue.put(False)
            write_debug_log("Put False in exit_queue of Parser")
            print "Joining threads"
            if variables.settings_obj.screenparsing:
                print "Joining ScreenParser thread"
                self.screenparser.join()
                print "Screenparser thread joined"
            self.stalking_exit_queue.put(False)
            print "Joining LogStalker thread"
            self.stalker_obj.join()
            print "LogStalker thread joined"
            print "Threads joined"
            self.parsing = False
            write_debug_log("Real-time parsing joining threads")
            if variables.settings_obj.overlay and self.overlay:
                self.overlay.destroy()
            self.overlay = None
            self.parsing_bar.stop()
            self.start_parsing_button.configure(text="Start real-time parsing")
            self.watching_stringvar.set("Watching no CombatLog...")
            write_debug_log("Finished stopping parsing...")

    def upload_events(self):
        tkMessageBox.showinfo("Notice", "This button is not yet functional.")
        return
        mainname = tkSimpleDialog.askstring("Main character name", "Please enter the name of the main character you " + \
                                            "want the character you're playing now to belong to in the database. Enter" + \
                                            "nothing or the name of the character you're currently playing on to " + \
                                            "create a new main character.")

    def grid_widgets(self):
        self.start_parsing_button.grid(column=0, row=1, padx=5, pady=5)
        self.upload_results_button.grid(column=1, row=1, padx=5, pady=5)
        self.server_list.config(width=15)
        self.faction_list.config(width=15)
        self.server_list.grid(column=2, row=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.W + tk.E)
        self.faction_list.grid(column=3, row=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.W + tk.E)
        self.parsing_bar.grid(column=0, columnspan=1, row=2, padx=5, pady=10, sticky=tk.N + tk.S + tk.W + tk.E)
        self.uploading_bar.grid(column=1, row=2, padx=5, pady=10, sticky=tk.N + tk.S + tk.W + tk.E)
        self.statistics_label_one.grid(column=3, row=2, padx=5, pady=5, sticky=tk.N + tk.W)
        self.statistics_list_label_one.grid(column=2, row=2, padx=5, pady=5, sticky=tk.N + tk.W)
        self.listbox.grid(column=0, row=3, columnspan=4, padx=5, pady=5, sticky=tk.N + tk.S + tk.W + tk.E)
        self.scrollbar.grid(column=5, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.statistics_label_one_text.set("")
        self.statistics_label_one_text.set("")
        self.watching_label.grid(column=0, row=4, columnspan=2, sticky=tk.W)

    def update_stats(self, dmg_done, dmg_taken, self_dmg, heals, abilities, enemies, spawns):
        damage_done = 0
        damage_taken = 0
        selfdamage = 0
        healing = 0
        for dmg in dmg_done:
            damage_done += dmg
        for dmg in dmg_taken:
            damage_taken += dmg
        for dmg in self_dmg:
            selfdamage += dmg
        for heal in heals:
            healing += heal
        self.statistics_label_one_text.set(str(damage_done) + "\n" +
                                           str(damage_taken) + "\n" +
                                           str(selfdamage) + "\n" +
                                           str(healing) + "\n" +
                                           str(spawns))
        if self.overlay:
            if variables.settings_obj.size == "big":
                self.overlay.stats_var.set(str(damage_done) + "\n" +
                                           str(damage_taken) + "\n" +
                                           str(healing) + "\n" +
                                           str(selfdamage) + "\n" +
                                           str(enemies) + "\n" +
                                           str(spawns))
            elif variables.settings_obj.size == "small":
                self.overlay.stats_var.set(str(damage_done) + "\n" +
                                           str(damage_taken) + "\n" +
                                           str(healing) + "\n" +
                                           str(selfdamage) + "\n")
            else:
                raise

    def callback(self, lines):
        if not self.parsing:
            return
        for line in lines:
            # self.listbox.see(tk.END)
            process = realtime.line_to_dictionary(line)
            self.parser.parse(process)
            self.dmg_done = self.parser.spawn_dmg_done
            self.dmg_taken = self.parser.spawn_dmg_taken
            self.selfdamage = self.parser.spawn_selfdmg
            self.healing = self.parser.spawn_healing_rcvd
            self.abilities = self.parser.tmp_abilities
            self.enemies = self.parser.recent_enemies
            self.spawns = self.parser.active_ids
            self.update_stats(self.dmg_done, self.dmg_taken, self.selfdamage, self.healing, self.abilities,
                              len(self.enemies), len(self.spawns))
        for obj in self.parse:
            obj.close()

    @staticmethod
    def spawn_callback(dd, dt, hr, sd):
        variables.insert_queue.put("SPAWN ENDED: DD = %s   DT = %s   HR = %s   SD = %s" % (str(sum(dd)), str(sum(dt)),
                                                                                           str(sum(hr)), str(sum(sd))))

    def match_callback(self, dd, dt, hr, sd):
        variables.insert_queue.put("MATCH ENDED: DD = %s   DT = %s   HR = %s   SD = %s" % (str(sum(dd)), str(sum(dt)),
                                                                                           str(sum(hr)), str(sum(sd))))
        if variables.settings_obj.overlay_when_gsf and self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def new_match_callback(self):
        self.listbox.delete(0, tk.END)
        self.parser.rt_timing = None
        if variables.settings_obj.overlay_when_gsf and not self.overlay:
            self.overlay = RealtimeOverlay(self.main_window)

    def insert(self):
        while variables.insert_queue.qsize():
            try:
                items = variables.insert_queue.get()
                if isinstance(items, tuple):
                    self.listbox.insert(tk.END, items[0])
                    self.listbox.itemconfig(tk.END, bg=items[1], fg=items[2])
                else:
                    self.listbox.insert(tk.END, items)
                    self.listbox.itemconfig(tk.END, bg="black", fg="white")
                time.sleep(0.1)
            except:
                print "[DEBUG] Error adding line to listbox"
        if self.parsing:
            self.main_window.after(500, self.insert)
            self.listbox.yview(tk.END)
        else:
            return
