# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
import tkMessageBox
# General imports
import os
# Own modules
import main
import vars
import parse
import statistics
import abilities
import realtime
import stalking
import overlay

# Class for the _frame in the fileTab of the parser
class file_frame(ttk.Frame):
    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame, width = 200, height = 400)
        self.main_window = main_window
        self.file_box = tk.Listbox(self)
        self.file_box_scroll = ttk.Scrollbar(self, orient = tk.VERTICAL)
        self.file_box_scroll.config(command = self.file_box.yview)
        self.file_box.config(yscrollcommand = self.file_box_scroll.set)
        self.match_box = tk.Listbox(self)
        self.match_box_scroll = ttk.Scrollbar(self, orient = tk.VERTICAL)
        self.match_box_scroll.config(command = self.match_box.yview)
        self.match_box.config(yscrollcommand = self.match_box_scroll.set)
        self.spawn_box = tk.Listbox(self)
        self.spawn_box_scroll = ttk.Scrollbar(self, orient = tk.VERTICAL, command = self.spawn_box.yview)
        self.spawn_box.config(yscrollcommand = self.spawn_box_scroll.set)
        self.file_box.bind("<Double-Button-1>", self.file_update)
        self.match_box.bind("<Double-Button-1>", self.match_update)
        self.spawn_box.bind("<Double-Button-1>", self.spawn_update)
        self.statistics_object = statistics.statistics()

    def grid_widgets(self):
        self.file_box.config(height = 7)
        self.match_box.config(height = 7)
        self.spawn_box.config(height = 7)
        self.file_box.grid(column = 0, row = 0, columnspan = 2, padx = 5, pady = 5)
        self.file_box_scroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.match_box.grid(column = 0, row =8, columnspan = 2, padx = 5, pady = 5)
        self.match_box_scroll.grid(column = 2, row = 8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.spawn_box.grid(column = 0, row = 16, columnspan = 2, padx = 5, pady = 5)
        self.spawn_box_scroll.grid(column = 2, row = 16, columnspan = 1, sticky = tk.N + tk.S, pady = 5)

    def add_matches(self):
        self.match_timing_strings = []
        self.match_timing_strings = [str(time.time()) for time in vars.match_timings]
        self.match_timing_strings = self.match_timing_strings[::2]
        '''
        for number in range(0, len(self.match_timing_strings) + 1):
            self.match_box.delete(number)
        '''
        self.match_box.delete(0, tk.END)
        self.match_box.insert(tk.END, "All matches")
        if len(self.match_timing_strings) == 0:
            self.match_box.delete(0, tk.END)
            self.add_spawns()
        else:
            for time in self.match_timing_strings:
                self.match_box.insert(tk.END, time)

    def add_spawns(self):
        self.spawn_timing_strings = []
        if vars.match_timing != None:
            try:
                index = self.match_timing_strings.index(vars.match_timing)
            except:
                self.spawn_box.delete(0, tk.END)
                return
            self.spawn_box.delete(0, tk.END)
            self.spawn_box.insert(tk.END, "All spawns")
            for spawn in vars.spawn_timings[index]:
                self.spawn_timing_strings.append(str(spawn.time()))
            for spawn in self.spawn_timing_strings:
                self.spawn_box.insert(tk.END, spawn)

    def add_files(self, silent=False):
        os.chdir(vars.path)
        self.file_strings = []
        self.file_box.delete(0, tk.END)
        if not silent:
            self.splash = overlay.splash_screen(self.main_window)
        try:
            os.chdir(vars.set_obj.cl_path)
        except:
            tkMessageBox.showerror("Error", "Folder not valid: " + vars.set_obj.cl_path)
            if not silent:
                self.splash.destroy()
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                if statistics.check_gsf(file):
                    self.file_strings.append(file)
                vars.files_done += 1
                if not silent:
                    self.splash.update_progress()
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file[7:-14])
        if not silent:
            self.splash.destroy()
        return

    def file_update(self, instance):
        if self.file_box.curselection() == (0,):
            print("[DEBUG] All CombatLogs selected")
            tkMessageBox.showinfo("Info", "The statistics for a whole folder aren't supported yet.")
        else:
            # Find the file name of the file selected in the list of file names
            numbers = self.file_box.curselection()
            vars.file_name = self.file_strings[numbers[0] - 1]
            # Read all the lines from the selected file
            with open(vars.file_name, "rU") as clicked_file:
                lines = clicked_file.readlines()
            # PARSING STARTS
            # Get the player ID numbers from the list of lines
            player = parse.determinePlayer(lines)
            # Parse the lines with the acquired player ID numbers
            vars.file_cube, vars.match_timings, vars.spawn_timings = parse.splitter(lines, player)
            # Start adding the matches from the file to the listbox
            self.add_matches()

    def match_update(self, instance):
        if self.match_box.curselection() == (0,):
            numbers = self.match_box.curselection()
            vars.match_timing = self.match_timing_strings[numbers[0] - 1]
            file_cube = vars.file_cube
            vars.abilities_string, vars.events_string, vars.statistics_string, vars.total_shipsdict, vars.enemies, vars.enemydamaged, vars.enemydamaget, vars.uncounted = self.statistics_object.file_statistics(file_cube)
            self.main_window.middle_frame.abilities_label_var.set(vars.abilities_string)
            self.main_window.middle_frame.events_label_var.set(vars.events_string)
            self.main_window.middle_frame.statistics_numbers_var.set(vars.statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(vars.total_shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"
            ships_string += "Uncounted\t\t" + str(vars.uncounted)
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in vars.enemies:
                self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, vars.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, vars.enemydamaget[enemy])
        else:
             numbers = self.match_box.curselection()
             vars.match_timing = self.match_timing_strings[numbers[0] - 1]
             self.add_spawns()

    def spawn_update(self, instance):
        if self.spawn_box.curselection() == (0,):
            match = vars.file_cube[self.match_timing_strings.index(vars.match_timing)]
            for spawn in match:
                vars.player_numbers.update(parse.determinePlayer(spawn))
            vars.abilities_string, vars.events_string, vars.statistics_string, vars.total_shipsdict, vars.enemies, vars.enemydamaged, vars.enemydamaget = self.statistics_object.match_statistics(match)
            self.main_window.middle_frame.abilities_label_var.set(vars.abilities_string)
            self.main_window.middle_frame.events_label_var.set(vars.events_string)
            self.main_window.middle_frame.statistics_numbers_var.set(vars.statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(vars.total_shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"

            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in vars.enemies:
                self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, vars.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, vars.enemydamaget[enemy])
        else:
            numbers = self.spawn_box.curselection()
            vars.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            match = vars.file_cube[self.match_timing_strings.index(vars.match_timing)]
            spawn = match[self.spawn_timing_strings.index(vars.spawn_timing)]
            vars.player_numbers = parse.determinePlayer(spawn)
            vars.abilities_string, vars.events_string, vars.statistics_string, vars.ships_list, vars.ships_comps, vars.enemies, vars.enemydamaged, vars.enemydamaget = self.statistics_object.spawn_statistics(spawn)
            self.main_window.middle_frame.abilities_label_var.set(vars.abilities_string)
            self.main_window.middle_frame.events_label_var.set(vars.events_string)
            self.main_window.middle_frame.statistics_numbers_var.set(vars.statistics_string)
            ships_string = "Possible ships used:\n"
            for ship in vars.ships_list:
                ships_string += str(ship) + "\n"
            ships_string += "\t\t\t\t\t\t\nWith the components:\n"
            for component in vars.ships_comps:
                ships_string += component + "\n"
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in vars.enemies:
                self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, vars.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, vars.enemydamaget[enemy])


class ship_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame, width = 300, height = 400)
        self.ship_label_var = tk.StringVar()
        self.ship_label = ttk.Label(root_frame, textvariable = self.ship_label_var, justify = tk.LEFT, wraplength = 495)
        self.ship_label.pack(side = tk.TOP)

class middle_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.notebook = ttk.Notebook(self, width = 300, height = 200)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text = "Statistics")
        self.notebook.add(self.enemies_frame, text = "Enemies")
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt to\nDamage dealt:\nDamage taken:\nSelfdamage:\nHealing received:\nHitcount:\nCriticalcount:\nCriticalluck:\nDeaths:\n"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable = self.statistics_label_var, justify = tk.LEFT, wraplength = 145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable = self.statistics_numbers_var, justify = tk.LEFT, wraplength = 145)
        self.enemies_label = ttk.Label(self.enemies_frame, text = "Name\tDamage taken\tDamage dealt\n")
        self.enemies_listbox = tk.Listbox(self.enemies_frame, width = 14, height = 10)
        self.enemies_damaget = tk.Listbox(self.enemies_frame, width = 14, height = 10)
        self.enemies_damaged = tk.Listbox(self.enemies_frame, width = 14, height = 10)
        self.enemies_scroll = ttk.Scrollbar(self.enemies_frame, orient = tk.VERTICAL,)
        self.enemies_scroll.config(command = self.enemies_scroll_yview)
        self.enemies_listbox.config(yscrollcommand = self.enemies_listbox_scroll)
        self.enemies_damaget.config(yscrollcommand = self.enemies_damaget_scroll)
        self.enemies_damaged.config(yscrollcommand = self.enemies_damaged_scroll)
        self.events_frame = ttk.Frame(self.notebook)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.abilities_frame, text = "Abilities")
        self.notebook.add(self.events_frame, text = "Events")
        self.abilities_label_var = tk.StringVar()
        self.abilities_label = ttk.Label(self.abilities_frame, textvariable = self.abilities_label_var, justify = tk.LEFT, wraplength = 295)
        self.events_label_var = tk.StringVar()
        self.events_label = ttk.Label(self.events_frame, textvariable = self.events_label_var, justify = tk.LEFT, wraplength = 295)

    def enemies_scroll_yview(self, *args):
        self.enemies_listbox.yview(*args)
        self.enemies_damaged.yview(*args)
        self.enemies_damaget.yview(*args)

    def enemies_listbox_scroll(self, *args):
        if self.enemies_damaged.yview() != self.enemies_listbox.yview():
            self.enemies_damaged.yview_moveto(args[0])
        if self.enemies_damaget.yview() != self.enemies_listbox.yview():
            self.enemies_damaget.yview_moveto(args[0])
        self.enemies_scroll.set(*args)

    def enemies_damaged_scroll(self, *args):
        if self.enemies_listbox.yview() != self.enemies_damaged.yview():
            self.enemies_listbox.yview_moveto(args[0])
        if self.enemies_damaget.yview() != self.enemies_damaged.yview():
            self.enemies_damaget.yview_moveto(args[0])
        self.enemies_scroll.set(*args)

    def enemies_damaget_scroll(self, *args):
        if self.enemies_listbox.yview() != self.enemies_damaget.yview():
            self.enemies_listbox.yview_moveto(args[0])
        if self.enemies_damaged.yview() != self.enemies_damaget.yview():
            self.enemies_damaged.yview_moveto(args[0])
        self.enemies_scroll.set(*args)

    def grid_widgets(self):
        self.abilities_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.events_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N  + tk.W + tk.E)
        self.statistics_label.grid(column = 0, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_numbers.grid(column = 2, row = 2, columnspan = 2, sticky = tk.N + tk.W + tk.E)
        self.enemies_label.grid(column = 0, row = 0, columnspan = 3)
        self.enemies_listbox.grid(column = 0, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaged.grid(column = 1, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaget.grid(column = 2, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_scroll.grid(column = 3, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)


class realtime_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.main_window = main_window
        self.listbox = tk.Listbox(self, width = 130, height = 15)
        self.statistics_list_label_one = ttk.Label(self, justify = tk.LEFT, text = "Damage dealt:\nDamage taken:\nSelfdamage:\nHealing received:")
        self.statistics_list_label_two = ttk.Label(self, justify = tk.LEFT, text = "Abilities:")
        self.statistics_label_one_text = tk.StringVar()
        self.statistics_label_one = ttk.Label(self, textvariable=self.statistics_label_one_text, justify=tk.LEFT)
        self.statistics_label_two_text = tk.StringVar()
        self.statistics_label_two = ttk.Label(self, textvariable=self.statistics_label_two_text, justify = tk.LEFT)
        self.start_parsing_button = ttk.Button(self, text = "Start real-time parsing", command=self.start_parsing)
        self.upload_results_button = ttk.Button(self, text = "Upload events", command= self.upload_events)
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
        self.parsing_bar = ttk.Progressbar(self, orient = "horizontal", mode = "indeterminate")

    def start_parsing(self):
        if not self.parsing:
            self.main_window.file_select_frame.add_files()
            # self.start_parsing_button.config(relief=tk.SUNKEN)
            self.parsing = True
            self.stalker_obj = stalking.LogStalker(self.callback, folder=vars.set_obj.cl_path)
            vars.FLAG = True
            self.stalker_obj.start()
            if vars.set_obj.overlay:
                self.overlay = overlay.overlay(self.main_window)
            self.parsing_bar.start(3)
            self.start_parsing_button.configure(text="Stop real-time parsing  ")
        elif self.parsing:
            self.main_window.file_select_frame.add_files()
            # self.start_parsing_button.config(relief=tk.RAISED)
            self.parsing = False
            vars.FLAG = False
            while self.stalker_obj.is_alive():
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
        self.server_list.grid(column = 3, row = 1, padx = 5, pady = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.faction_list.grid(column = 4, row = 1, padx = 5, pady = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.parsing_bar.grid(column = 0, columnspan = 1, row = 2, padx = 5, pady = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_label_one.grid(column = 3, row = 2, padx = 5, pady = 5, sticky = tk.N + tk.W)
        self.statistics_label_two.grid(column = 4, row = 2, padx = 5, pady = 5, sticky = tk.N + tk.W)
        self.statistics_list_label_one.grid(column = 1, row = 2, padx = 5, pady =5, sticky = tk.N + tk.W)
        self.statistics_list_label_two.grid(column = 3, row = 2, padx = 5, pady =5, sticky = tk.N + tk.W)
        self.listbox.grid(column = 0, row = 3, columnspan = 5, padx = 5, pady = 5)
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
                                           str(healing) + "\n")
        self.statistics_label_two_text.set(str(abilities))
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

    def callback(self, filename, lines):
        if not self.parsing:
            return
        print "[DEBUG] callback called"
        for elem in self.parse:
            if elem.fname is filename:
                parser = elem
        if not self.parse:
            self.parser = realtime.Parser(filename)
            self.parse.append(self.parser)
        for line in lines:
            process = realtime.line_to_dictionary(line)
            self.parser.parse(process)
            self.dmg_done = self.parser.spawn_dmg_done
            self.dmg_taken = self.parser.spawn_dmg_taken
            self.selfdamage = self.parser.spawn_selfdmg
            self.healing = self.parser.spawn_healing_rcvd
            self.abilities = self.parser.tmp_abilities
            self.spawns = self.parser.spawns
            self.update_stats(self.dmg_done, self.dmg_taken, self.selfdamage, self.healing, self.abilities, self.spawns)
        for obj in self.parse:
            obj.close()

class share_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)

class settings_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ### LAY-OUT ###
        ttk.Frame.__init__(self, root_frame)
        self.gui_frame = ttk.Frame(root_frame)
        self.entry_frame = ttk.Frame(root_frame)
        self.privacy_frame = ttk.Frame(root_frame)
        self.server_frame = ttk.Frame(root_frame)
        self.upload_frame = ttk.Frame(root_frame)
        self.realtime_frame = ttk.Frame(root_frame)
        self.save_frame = ttk.Frame(root_frame)
        self.license_frame = ttk.Frame(root_frame)
        self.main_window = main_window
        ### GUI SETTINGS ###
        self.gui_label = ttk.Label(root_frame, text = "GUI settings", justify=tk.LEFT)
        self.style_label = ttk.Label(self.gui_frame, text = "\tParser style: ")
        self.style_options = []
        self.style = tk.StringVar()
        self.style.set(main_window.style.theme_use())
        for style in main_window.styles:
            self.style_options.append(ttk.Radiobutton(self.gui_frame, value = str(style), text = style, variable = self.style))
        ### PARSING SETTINGS ###
        self.parsing_label = ttk.Label(root_frame, text = "Parsing settings", justify=tk.LEFT)
        self.path_entry = ttk.Entry(self.entry_frame, width=75)
        self.path_entry_label = ttk.Label(self.entry_frame, text = "\tCombatLogs folder:")
        self.privacy_label = ttk.Label(self.privacy_frame, text = "\tConnect to server for player identification:")
        self.privacy_var = tk.BooleanVar()
        self.privacy_select_true = ttk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = True, text = "Yes")
        self.privacy_select_false = ttk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = False, text = "No")
        ### SHARING SETTINGS ###
        self.sharing_label = ttk.Label(root_frame, text = "Share settings", justify=tk.LEFT)
        self.server_label = ttk.Label(self.server_frame, text = "\tServer for sharing: ")
        self.server_address_entry = ttk.Entry(self.server_frame, width=35)
        self.server_colon_label = ttk.Label(self.server_frame, text = ":")
        self.server_port_entry = ttk.Entry(self.server_frame, width=8)
        self.auto_upload_label = ttk.Label(self.upload_frame, text="\tAuto-upload CombatLogs to the server:\t\t")
        self.auto_upload_var = tk.BooleanVar()
        self.auto_upload_false = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=False, text="No")
        self.auto_upload_true = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=True, text="Yes")
        ### REAL-TIME SETTINGS ###
        self.realtime_settings_label = ttk.Label(self.realtime_frame, text = "Real-time parsing settings")
        self.overlay_enable_label = ttk.Label(self.realtime_frame, text = "\tEnable overlay for real-time parsing: ")
        self.overlay_enable_radio_var = tk.BooleanVar()
        self.overlay_enable_radio_yes = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_enable_radio_var, value=True, text="Yes")
        self.overlay_enable_radio_no = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_enable_radio_var, value=False, text="No")
        self.overlay_opacity_label = ttk.Label(self.realtime_frame, text = "\tOverlay opacity (between 0 and 1):")
        self.overlay_opacity_input = ttk.Entry(self.realtime_frame, width = 3)
        self.overlay_size_label = ttk.Label(self.realtime_frame, text = "\tOverlay window size: ")
        self.overlay_size_var = tk.StringVar()
        self.overlay_size_radio_big = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_size_var, value = "big", text = "Big")
        self.overlay_size_radio_small = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_size_var, value = "small", text = "Small")
        self.overlay_position_label = ttk.Label(self.realtime_frame, text = "\tPosition of the in-game overlay:")
        self.overlay_position_var = tk.StringVar()
        self.overlay_position_var.set(vars.set_obj.pos)
        self.overlay_position_radio_tl = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "TL", text =  "Top left")
        self.overlay_position_radio_bl = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "BL", text = "Bottom left")
        self.overlay_position_radio_tr = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "TR", text = "Top right")
        self.overlay_position_radio_br = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "BR", text = "Bottom right")
        ### MISC ###
        self.separator = ttk.Separator(root_frame, orient=tk.HORIZONTAL)
        self.save_settings_button = ttk.Button(self.save_frame, text="  Save  ", command=self.save_settings)
        self.discard_settings_button = ttk.Button(self.save_frame, text="Discard", command=self.discard_settings)
        self.default_settings_button = ttk.Button(self.save_frame, text="Defaults", command = self.default_settings)
        self.license_button = ttk.Button(self.license_frame, text="License", command=self.show_license)
        self.privacy_button = ttk.Button(self.license_frame, text = "Privacy statement for server", command=self.show_privacy)
        self.version_label = ttk.Label(self.license_frame, text="Version 2.0")
        self.update_label_var = tk.StringVar()
        self.update_label = ttk.Label(self.license_frame, textvariable=self.update_label_var)
        self.copyright_label = ttk.Label(self.license_frame, text = "Copyright (C) 2016 by RedFantom and Daethyra", justify=tk.LEFT)
        self.thanks_label = ttk.Label(self.license_frame, text = "Special thanks to Nightmaregale for bèta testing", justify=tk.LEFT)
        self.update_settings()

    def grid_widgets(self):
        ### GUI SETTINGS ###
        self.gui_label.grid(column = 0, row=0, sticky=tk.W)
        self.gui_frame.grid(column = 0, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        self.style_label.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        set_column = 0
        for radio in self.style_options:
            set_column += 1
            radio.grid(column=set_column, row=0,sticky=tk.N+tk.S+tk.W+tk.E)
        ### PARSING SETTINGS ###
        self.parsing_label.grid(column=0, row=2, sticky=tk.W)
        self.path_entry_label.grid(column=0, row=0, sticky=tk.W)
        self.path_entry.grid(column=1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.entry_frame.grid(column=0, row=3, sticky=tk.N+tk.S+tk.W+tk.E)
        self.privacy_label.grid(column=0, row=0,sticky=tk.W)
        self.privacy_select_true.grid(column=1, row=0)
        self.privacy_select_false.grid(column=2, row=0)
        self.privacy_frame.grid(column=0, row=4, sticky=tk.N+tk.S+tk.W+tk.E)
        ### SHARING SETTINGS ###
        self.sharing_label.grid(column=0, row=5, sticky=tk.W)
        self.server_label.grid(column=0, row=0, sticky=tk.W)
        self.server_address_entry.grid(column=1,row=0)
        self.server_colon_label.grid(column=2,row=0)
        self.server_port_entry.grid(column=3,row=0)
        self.server_frame.grid(column=0, row=6, sticky=tk.N+tk.S+tk.W+tk.E)
        self.auto_upload_label.grid(column=0, row=0)
        self.auto_upload_true.grid(column=1,row=0)
        self.auto_upload_false.grid(column=2,row=0)
        self.upload_frame.grid(column=0,row=7,sticky=tk.N+tk.S+tk.W+tk.E)
        ### REALTIME SETTINGS ###
        self.overlay_enable_label.grid(column = 0, row =1, sticky=tk.W)
        self.overlay_enable_radio_yes.grid(column = 1, row = 1, sticky=tk.W)
        self.overlay_enable_radio_no.grid(column = 2, row = 1, sticky=tk.W)
        self.overlay_opacity_label.grid(column = 0, row = 2, sticky=tk.W)
        self.overlay_opacity_input.grid(column = 1, row = 2, sticky=tk.W)
        self.realtime_settings_label.grid(column = 0, row = 0, sticky=tk.W)
        self.overlay_size_label.grid(column = 0, row = 3, sticky = tk.W)
        self.overlay_size_radio_big.grid(column = 1, row = 3, sticky = tk.W)
        self.overlay_size_radio_small.grid(column = 2, row = 3, sticky = tk.W)
        self.overlay_position_label.grid(column = 0, row = 4, sticky = tk.W)
        self.overlay_position_radio_tl.grid(column = 1, row = 4, sticky = tk.W)
        self.overlay_position_radio_bl.grid(column = 2, row = 4, sticky = tk.W)
        self.overlay_position_radio_tr.grid(column = 3, row = 4, sticky = tk.W)
        self.overlay_position_radio_br.grid(column = 4, row = 4, sticky = tk.W)
        self.realtime_frame.grid(column = 0, row = 8, sticky=tk.N+tk.S+tk.W+tk.E)
        ### MISC ###
        self.save_settings_button.grid(column=0, row=0, padx=2)
        self.discard_settings_button.grid(column=1, row=0, padx=2)
        self.default_settings_button.grid(column=2, row=0, padx=2)
        self.save_frame.grid(column=0, row=9, sticky=tk.W)
        self.license_button.grid(column=1,row=0,sticky=tk.W, padx=5)
        self.privacy_button.grid(column=2,row=0,sticky=tk.W, padx=5)
        self.copyright_label.grid(column=0, row=0, sticky=tk.W)
        self.update_label.grid(column=0, row=2, sticky=tk.W)
        self.thanks_label.grid(column=0,row=1, sticky=tk.W)
        self.separator.grid(column = 0, row = 10, sticky = tk.N+tk.S+tk.W+tk.E, pady=10)
        self.license_frame.grid(column=0, row=11, sticky=tk.N+tk.S+tk.W+tk.E)

    def update_settings(self):
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, vars.set_obj.cl_path)
        self.privacy_var.set(bool(vars.set_obj.auto_ident))
        self.server_address_entry.delete(0, tk.END)
        self.server_address_entry.insert(0, str(vars.set_obj.server_address))
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, int(vars.set_obj.server_port))
        self.auto_upload_var.set(bool(vars.set_obj.auto_upl))
        self.overlay_enable_radio_var.set(bool(vars.set_obj.overlay))
        self.overlay_opacity_input.delete(0, tk.END)
        self.overlay_opacity_input.insert(0, vars.set_obj.opacity)
        self.overlay_size_var.set(vars.set_obj.size)
        self.overlay_position_var.set(vars.set_obj.pos)

    def save_settings(self):
        print "[DEBUG] Save_settings called!"
        if str(self.style.get()) == vars.set_obj.style:
            reboot = False
        else:
            reboot = True
        vars.set_obj.write_set(cl_path=str(self.path_entry.get()), auto_ident=str(self.privacy_var.get()),
                               server_address=str(self.server_address_entry.get()), server_port=str(self.server_port_entry.get()),
                               auto_upl=str(self.auto_upload_var.get()), overlay=str(self.overlay_enable_radio_var.get()),
                               opacity=str(self.overlay_opacity_input.get()), size=str(self.overlay_size_var.get()), pos=str(self.overlay_position_var.get()),
                               style=str(self.style.get()))
        print self.style.get()
        self.update_settings()
        self.main_window.file_select_frame.add_files()
        if reboot:
            self.main_window.update_style()

    def discard_settings(self):
        self.update_settings()

    def default_settings(self):
        vars.set_obj.write_def()
        self.update_settings()

    @staticmethod
    def show_license():
        tkMessageBox.showinfo("License", "This program is licensed under the General Public License Version 3, by GNU. See LICENSE in the installation directory for more details")

    def show_privacy(self):
        overlay.privacy(self.main_window)
