# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import mtTkinter as tk
import ttk
import tkMessageBox
# General imports
import time
# Own modules
import vars
import realtime
import stalking_alt
import overlay
import statistics

class realtime_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.parser = None
        self.main_window = main_window
        self.listbox = tk.Listbox(self, width = 105, height = 15)
        self.scrollbar = ttk.Scrollbar(self, orient = tk.VERTICAL, command = self.listbox.yview())
        self.listbox.config(yscrollcommand=self.scrollbar.set, font = ("Consolas", 10))
        self.statistics_list_label_one = ttk.Label(self, justify = tk.LEFT, text = "Damage dealt:\nDamage taken:\nSelfdamage:\nHealing received:\nSpawns:")
        self.statistics_list_label_two = ttk.Label(self, justify = tk.LEFT, text = "Abilities:")
        self.statistics_label_one_text = tk.StringVar()
        self.statistics_label_one = ttk.Label(self, textvariable=self.statistics_label_one_text, justify=tk.LEFT)
        self.start_parsing_button = ttk.Button(self, text = "Start real-time parsing", command=self.start_parsing, width = 25)
        self.upload_results_button = ttk.Button(self, text = "Start uploading events", command= self.upload_events, width = 25)
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
        self.parsing_bar = ttk.Progressbar(self, orient = tk.HORIZONTAL, mode = "indeterminate")
        self.uploading_bar = ttk.Progressbar(self, orient = tk.HORIZONTAL, mode = "indeterminate")

    def start_parsing(self):
        if not self.parsing:
            self.main_window.file_select_frame.add_files()
            # self.start_parsing_button.config(relief=tk.SUNKEN)
            self.parsing = True
            self.main_window.after(100, self.insert)
            self.stalker_obj = stalking_alt.LogStalker(callback=self.callback, folder=vars.set_obj.cl_path)
            vars.FLAG = True
            self.stalker_obj.start()
            if vars.set_obj.overlay:
                self.overlay = overlay.overlay(self.main_window)
            self.parsing_bar.start(3)
            self.start_parsing_button.configure(text="Stop real-time parsing")
        elif self.parsing:
            self.main_window.file_select_frame.add_files()
            '''
            for (id, file) in self.stalker_obj.ls:
                self.stalker_obj.unwatch(file, id)
                if file.is_open():
                    file.close()
            '''
            # self.start_parsing_button.config(relief=tk.RAISED)
            self.parsing = False
            vars.FLAG = False
            self.stalker_obj.FLAG = False
            while self.stalker_obj.is_alive():
                print "[DEBUG] stalker_obj still running"
                pass
            if vars.set_obj.overlay:
                self.overlay.destroy()
            self.parsing_bar.stop()
            self.start_parsing_button.configure(text="Start real-time parsing")

    def upload_events(self):
        tkMessageBox.showinfo("Notice", "This button is not yet functional.")

    def grid_widgets(self):
        self.start_parsing_button.grid(column = 0, row = 1, padx = 5, pady = 5)
        self.upload_results_button.grid(column = 1, row = 1, padx = 5, pady = 5)
        self.server_list.config(width = 15)
        self.faction_list.config(width = 15)
        self.server_list.grid(column = 2, row = 1, padx = 5, pady = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.faction_list.grid(column = 3, row = 1, padx = 5, pady = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.parsing_bar.grid(column = 0, columnspan = 1, row = 2, padx = 5, pady = 10, sticky = tk.N + tk.S + tk.W + tk.E)
        self.uploading_bar.grid(column =1, row=2, padx=5,pady=10,sticky=tk.N + tk.S + tk.W + tk.E)
        self.statistics_label_one.grid(column = 3, row = 2, padx = 5, pady = 5, sticky = tk.N + tk.W)
        self.statistics_list_label_one.grid(column = 2, row = 2, padx = 5, pady =5, sticky = tk.N + tk.W)
        self.listbox.grid(column = 0, row = 3, columnspan = 4, padx = 5, pady = 5, sticky=tk.N + tk.S + tk.W + tk.E)
        self.scrollbar.grid(column = 5, row = 3, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_label_one_text.set("")
        self.statistics_label_one_text.set("")

    def update_stats(self, dmg_done, dmg_taken, self_dmg, heals, abilities, spawns):
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
        if vars.set_obj.overlay:
            if vars.set_obj.size == "big":
                self.overlay.stats_var.set(str(damage_done) + "\n" +
                                           str(damage_taken) + "\n" +
                                           str(healing) + "\n" +
                                           str(selfdamage) + "\n" +
                                           str(spawns))
            elif vars.set_obj.size == "small":
                self.overlay.stats_var.set(str(damage_done) + "\n" +
                                           str(damage_taken) + "\n" +
                                           str(healing) + "\n" +
                                           str(selfdamage) + "\n")
            else:
                raise

    def callback(self, lines):
        if not self.parsing:
            return
        if not self.parser:
            self.parser = realtime.Parser(self.spawn_callback, self.match_callback, self.new_match_callback, statistics.pretty_event)
        for line in lines:
            # self.listbox.see(tk.END)
            process = realtime.line_to_dictionary(line)
            self.parser.parse(process)
            self.dmg_done = self.parser.spawn_dmg_done
            self.dmg_taken = self.parser.spawn_dmg_taken
            self.selfdamage = self.parser.spawn_selfdmg
            self.healing = self.parser.spawn_healing_rcvd
            self.abilities = self.parser.tmp_abilities
            self.spawns = self.parser.active_ids
            self.update_stats(self.dmg_done, self.dmg_taken, self.selfdamage, self.healing, self.abilities, len(self.spawns))
        for obj in self.parse:
            obj.close()

    @staticmethod
    def spawn_callback(dd, dt, hr, sd):
        vars.insert_queue.put("SPAWN ENDED: DD = %s   DT = %s   HR = %s   SD = %s" % (str(sum(dd)), str(sum(dt)), str(sum(hr)), str(sum(sd))))

    @staticmethod
    def match_callback(dd, dt, hr, sd):
        vars.insert_queue.put("MATCH ENDED: DD = %s   DT = %s   HR = %s   SD = %s" % (str(sum(dd)), str(sum(dt)), str(sum(hr)), str(sum(sd))))

    def new_match_callback(self):
        self.listbox.delete(0, tk.END)
        self.parser.rt_timing = None

    def insert(self):
        while vars.insert_queue.qsize():
            try:
                self.listbox.insert(tk.END, vars.insert_queue.get())
                time.sleep(0.1)
            except:
                print "[DEBUG] Error adding line to listbox"
        if self.parsing:
            self.main_window.after(500, self.insert)
            self.listbox.yview(tk.END)
        else:
            return
