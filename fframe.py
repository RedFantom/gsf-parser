# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import mtTkinter as tk
import ttk
import tkMessageBox
# General imports
import os
# Own modules
import vars
import parse
import statistics
import abilities
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
                vars.spawn_index = index
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
            return
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                if statistics.check_gsf(file):
                    self.file_strings.append(file)
                vars.files_done += 1
                if not silent:
                    self.splash.update_progress()
                else:
                    self.main_window.splash.update_progress()
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
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
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
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
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
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
        else:
            numbers = self.spawn_box.curselection()
            vars.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            match = vars.file_cube[self.match_timing_strings.index(vars.match_timing)]
            spawn = match[self.spawn_timing_strings.index(vars.spawn_timing)]
            vars.spawn = spawn
            vars.player_numbers = parse.determinePlayer(spawn)
            vars.abilities_string, vars.events_string, vars.statistics_string, vars.ships_list, vars.ships_comps, vars.enemies, vars.enemydamaged, vars.enemydamaget = self.statistics_object.spawn_statistics(spawn)
            self.main_window.middle_frame.abilities_label_var.set(vars.abilities_string)
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
            self.main_window.middle_frame.events_button.state(["!disabled"])

class ship_frame(ttk.Frame):
    # TODO Add possibility of pictures to the Ship Frame
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame, width = 300, height = 400)
        self.ship_label_var = tk.StringVar()
        self.ship_label = ttk.Label(root_frame, textvariable = self.ship_label_var, justify = tk.LEFT, wraplength = 495)
        self.ship_label.pack(side = tk.TOP)

class middle_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.window = main_window
        self.notebook = ttk.Notebook(self, width = 300, height = 300)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text = "Statistics")
        self.notebook.add(self.enemies_frame, text = "Enemies")
        self.events_frame = ttk.Frame(self, width = 300)
        self.events_button = ttk.Button(self.events_frame, text = "Show events for spawn", command=self.show_events, state=tk.DISABLED, width = 43)
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt to\nDamage dealt:\nDamage taken:\nSelfdamage:\nHealing received:\nHitcount:\nCriticalcount:\nCriticalluck:\nDeaths:\n"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable = self.statistics_label_var, justify = tk.LEFT, wraplength = 145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable = self.statistics_numbers_var, justify = tk.LEFT, wraplength = 145)
        self.enemies_label = ttk.Label(self.enemies_frame, text = "Name\tDamage taken\tDamage dealt\n")
        self.enemies_listbox = tk.Listbox(self.enemies_frame, width = 14, height = 16)
        self.enemies_damaget = tk.Listbox(self.enemies_frame, width = 14, height = 16)
        self.enemies_damaged = tk.Listbox(self.enemies_frame, width = 14, height = 16)
        self.enemies_scroll = ttk.Scrollbar(self.enemies_frame, orient = tk.VERTICAL,)
        self.enemies_scroll.config(command = self.enemies_scroll_yview)
        self.enemies_listbox.config(yscrollcommand = self.enemies_listbox_scroll)
        self.enemies_damaget.config(yscrollcommand = self.enemies_damaget_scroll)
        self.enemies_damaged.config(yscrollcommand = self.enemies_damaged_scroll)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.abilities_frame, text = "Abilities")
        self.abilities_label_var = tk.StringVar()
        self.abilities_label = ttk.Label(self.abilities_frame, textvariable = self.abilities_label_var, justify = tk.LEFT, wraplength = 295)

    def show_events(self):
        self.toplevel = overlay.events_view(self.window, vars.spawn, vars.player_numbers)

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
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N  + tk.W + tk.E)
        self.events_frame.grid(column = 0, row = 1, columnspan = 4, sticky=tk.N+tk.W+tk.S+tk.E)
        self.events_button.grid(column = 0, row = 1,sticky=tk.N+tk.W+tk.S+tk.E, columnspan = 4)
        self.statistics_label.grid(column = 0, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_numbers.grid(column = 2, row = 2, columnspan = 2, sticky = tk.N + tk.W + tk.E)
        self.enemies_label.grid(column = 0, row = 0, columnspan = 3)
        self.enemies_listbox.grid(column = 0, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaged.grid(column = 1, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaget.grid(column = 2, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_scroll.grid(column = 3, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)