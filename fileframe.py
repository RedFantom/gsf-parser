# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
try:
     import mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import tkMessageBox
from PIL import Image, ImageTk
# General imports
import os
import re
from datetime import datetime
# Own modules
import variables
import parse
import statistics
import abilities
import toplevels
import widgets

# Class for the _frame in the fileTab of the parser
class file_frame(ttk.Frame):
    """
    Class for a frame that contains three listboxes, one for files, one for matches and
    one for spawns, and updates them and other widgets after parsing the files using the
    methods found in the parse.py module accordingly. This frame controls the whole of file
    parsing, the other frames only display the results.
    --------------------
    | combatlog_1 | /\ |
    | combatlog_2 | || |
    | combatlog_3 | \/ |
    --------------------
    | match_1     | /\ |
    | match_2     | || |
    | match_3     | \/ |
    --------------------
    | spawn_1     | /\ |
    | spawn_2     | || |
    | spawn_3     | \/ |
    --------------------
    """

    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        """
        Create all widgets and make the links between them
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame, width = 200, height = 420)
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
        self.refresh_button = ttk.Button(self, text = "Refresh", command = self.add_files_cb)
        self.filters_button = ttk.Button(self, text = "Filters", command = self.filters)

    def filters(self):
        """
        Opens Toplevel to enable filters and then adds the filtered CombatLogs to the Listboxes
        """

        pass

    def grid_widgets(self):
        """
        Put all widgets in the right places
        :return:
        """

        self.file_box.config(height = 6)
        self.match_box.config(height = 6)
        self.spawn_box.config(height = 6)
        self.file_box.grid(column = 0, row = 0, columnspan = 2, padx = 5, pady = 5)
        self.file_box_scroll.grid(column = 2, row = 0, rowspan =8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.match_box.grid(column = 0, row =8, columnspan = 2, padx = 5, pady = 5)
        self.match_box_scroll.grid(column = 2, row = 8, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.spawn_box.grid(column = 0, row = 16, columnspan = 2, padx = 5, pady = 5)
        self.spawn_box_scroll.grid(column = 2, row = 16, columnspan = 1, sticky = tk.N + tk.S, pady = 5)
        self.refresh_button.grid(column = 0, columnspan = 3, row = 17, rowspan = 1, sticky = tk.N + tk.S + tk.E + tk.W)
        self.filters_button.grid(column = 0, columnspan = 3, row = 18, rowspan = 1, sticky = tk.N + tk.S + tk.E + tk.W)


    def add_matches(self):
        """
        Function that adds the matches found in the file selected to the appropriate listbox
        :return:
        """

        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_label_var.set("")
        self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
        self.main_window.ship_frame.ship_label_var.set("")
        with open(variables.file_name, "r") as file:
            variables.player_name = parse.determinePlayerName(file.readlines())
        self.spawn_box.delete(0, tk.END)
        self.match_timing_strings = []
        self.match_timing_strings = [str(time.time()) for time in variables.match_timings]
        self.match_timing_strings = self.match_timing_strings[::2]
        """
        for number in range(0, len(self.match_timing_strings) + 1):
            self.match_box.delete(number)
        """
        self.match_box.delete(0, tk.END)
        self.match_box.insert(tk.END, "All matches")
        if len(self.match_timing_strings) == 0:
            self.match_box.delete(0, tk.END)
            self.add_spawns()
        else:
            for time in self.match_timing_strings:
                self.match_box.insert(tk.END, time)

    def add_spawns(self):
        """
        Function that adds the spawns found in the selected match to the appropriate listbox
        :return:
        """

        self.main_window.middle_frame.abilities_label_var.set("")
        self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
        self.main_window.ship_frame.ship_label_var.set("")
        self.spawn_timing_strings = []
        if variables.match_timing != None:
            try:
                index = self.match_timing_strings.index(variables.match_timing)
                variables.spawn_index = index
            except:
                self.spawn_box.delete(0, tk.END)
                return
            self.spawn_box.delete(0, tk.END)
            self.spawn_box.insert(tk.END, "All spawns")
            for spawn in variables.spawn_timings[index]:
                self.spawn_timing_strings.append(str(spawn.time()))
            for spawn in self.spawn_timing_strings:
                self.spawn_box.insert(tk.END, spawn)

    def add_files_cb(self):
        """
        Function that adds the files to the list that are currently in the directory when the
        :return:
        """

        try:
            os.chdir(variables.settings_obj.cl_path)
        except WindowsError:
            return
        self.file_strings = []
        self.files_dict = {}
        self.file_box.delete(0, tk.END)
        self.match_box.delete(0, tk.END)
        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_label_var.set("")
        self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
        self.main_window.ship_frame.ship_label_var.set("")
        self.splash = toplevels.splash_screen(self.main_window)
        try:
            os.chdir(variables.settings_obj.cl_path)
        except WindowsError:
            tkMessageBox.showerror("Error", "Folder not valid: " + variables.settings_obj.cl_path)
            self.splash.destroy()
            return
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                if statistics.check_gsf(file):
                    try:
                        dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
                    except:
                        dt = file
                    self.files_dict[dt] = file
                    self.file_strings.append(dt)
                variables.files_done += 1
                self.splash.update_progress()
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file)
        self.splash.destroy()
        return

    def add_files(self, silent=False):
        """
        Function that checks files found in the in the settings specified folder for
        GSF matches and if those are found in a file, it gets added to the listbox
        Also calls for a splash screen if :param silent: is set to False
        :param silent:
        :return:
        """

        try:
            os.chdir(variables.settings_obj.cl_path)
        except WindowsError:
            return
        self.file_strings = []
        self.files_dict = {}
        self.file_box.delete(0, tk.END)
        self.match_box.delete(0, tk.END)
        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_label_var.set("")
        self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
        self.main_window.ship_frame.ship_label_var.set("")
        if not silent:
            self.splash = toplevels.splash_screen(self.main_window)
        try:
            os.chdir(variables.settings_obj.cl_path)
        except:
            tkMessageBox.showerror("Error", "Folder not valid: " + variables.settings_obj.cl_path)
            if not silent:
                self.splash.destroy()
            return
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                if statistics.check_gsf(file):
                    try:
                        dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
                        # print "[DEBUG] Generated time: ", dt
                    except:
                        dt = file
                    self.files_dict[dt] = file
                    self.file_strings.append(dt)
                variables.files_done += 1
                if not silent:
                    self.splash.update_progress()
                else:
                    self.main_window.splash.update_progress()
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file)
        if not silent:
            self.splash.destroy()
        return

    def file_update(self, instance):
        """
        Function either sets the file and calls add_matches to add the matches found in the file
        to the matches_listbox, or starts the parsing of all files found in the specified folder
        and displays the results in the other frames.
        :param instance: for Tkinter callback
        :return:
        """

        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
        if self.file_box.curselection() == (0,):
            print("[DEBUG] All CombatLogs selected")
            stat_obj = statistics.statistics()
            stats_string = stat_obj.folder_statistics()
            self.main_window.middle_frame.statistics_numbers_var.set(stats_string)
            self.main_window.middle_frame.abilities_label_var.set("Abilities is currently not available for a whole folder.")
            self.main_window.ship_frame.ship_label_var.set("Ships currently not available for a whole folder.")
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
        else:
            # Find the file name of the file selected in the list of file names
            numbers = self.file_box.curselection()
            try:
                variables.file_name = self.files_dict[self.file_strings[numbers[0] - 1]]
            except TypeError:
                try:
                    variables.file_name = self.file_strings[int(numbers[0]) - 1]
                except:
                    tkMessageBox.showerror("Error", "The parser encountered a bug known as #19 in the repository. "
                                                    "This bug has not been fixed. Check out issue #19 in the repository"
                                                    " for more information.")
            except KeyError:
                tkMessageBox.showerror("Error", "The parser encountered an error while selecting the file. Please "
                                                "consult the issues page of the GitHub repository.")
            # Read all the lines from the selected file
            with open(variables.file_name, "rU") as clicked_file:
                lines = clicked_file.readlines()
            # PARSING STARTS
            # Get the player ID numbers from the list of lines
            player = parse.determinePlayer(lines)
            # Parse the lines with the acquired player ID numbers
            variables.file_cube, variables.match_timings, variables.spawn_timings = parse.splitter(lines, player)
            # Start adding the matches from the file to the listbox
            self.add_matches()
        self.main_window.ship_frame.remove_image()

    def match_update(self, instance):
        """
        Either adds sets the match and calls add_spawns to add the spawns found in the match
        or starts the parsing of all files found in the specified file and displays the results
        in the other frames.
        :param instance: for Tkinter callback
        :return:
        """

        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
        self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
        if self.match_box.curselection() == (0,):
            self.spawn_box.delete(0, tk.END)
            numbers = self.match_box.curselection()
            variables.match_timing = self.match_timing_strings[numbers[0] - 1]
            file_cube = variables.file_cube
            (variables.abilities_string, variables.statistics_string, variables.total_shipsdict, variables.enemies, variables.enemydamaged,
             variables.enemydamaget, variables.uncounted) = self.statistics_object.file_statistics(file_cube)
            self.main_window.middle_frame.abilities_label_var.set(variables.abilities_string)
            self.main_window.middle_frame.statistics_numbers_var.set(variables.statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(variables.total_shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"
            ships_string += "Uncounted\t\t" + str(variables.uncounted)
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in variables.enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, "System")
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy)
                else:
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, variables.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, variables.enemydamaget[enemy])
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
        else:
             numbers = self.match_box.curselection()
             variables.match_timing = self.match_timing_strings[numbers[0] - 1]
             self.add_spawns()
        self.main_window.ship_frame.remove_image()

    def spawn_update(self, instance):
        """
        Either starts the parsing of ALL spawns found in the specified match or just one of them
        and displays the results in the other frames accordingly
        :param instance: for Tkinter callback
        :return:
        """
        if self.spawn_box.curselection() == (0,):
            try:
                match = variables.file_cube[self.match_timing_strings.index(variables.match_timing)]
            except ValueError:
                print "[DEBUG] vars.match_timing not in self.match_timing_strings!"
            for spawn in match:
                variables.player_numbers.update(parse.determinePlayer(spawn))
            (variables.abilities_string, variables.statistics_string, variables.total_shipsdict, variables.enemies, variables.enemydamaged,
             variables.enemydamaget) = self.statistics_object.match_statistics(match)
            self.main_window.middle_frame.abilities_label_var.set(variables.abilities_string)
            self.main_window.middle_frame.statistics_numbers_var.set(variables.statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(variables.total_shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"
            ships_string += "Uncounted\t\t%s" % variables.total_shipsdict["Uncounted"]
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in variables.enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, "System")
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy)
                else:
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, variables.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, variables.enemydamaget[enemy])
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            self.main_window.ship_frame.remove_image()
        else:
            numbers = self.spawn_box.curselection()
            variables.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            try:
                match = variables.file_cube[self.match_timing_strings.index(variables.match_timing)]
            except ValueError:
                print "[DEBUG] vars.match_timing not in self.match_timing_strings!"
                return
            spawn = match[self.spawn_timing_strings.index(variables.spawn_timing)]
            variables.spawn = spawn
            variables.player_numbers = parse.determinePlayer(spawn)
            (variables.abilities_string, variables.statistics_string, variables.ships_list, variables.ships_comps, variables.enemies,
             variables.enemydamaged, variables.enemydamaget) = self.statistics_object.spawn_statistics(spawn)
            self.main_window.middle_frame.abilities_label_var.set(variables.abilities_string)
            self.main_window.middle_frame.statistics_numbers_var.set(variables.statistics_string)
            ships_string = "Possible ships used:\n"
            for ship in variables.ships_list:
                ships_string += str(ship) + "\n"
            ships_string += "\t\t\t\t\t\t\nWith the components:\n"
            for component in variables.ships_comps:
                ships_string += component + "\n"
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            self.main_window.middle_frame.enemies_listbox.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaged.delete(0, tk.END)
            self.main_window.middle_frame.enemies_damaget.delete(0, tk.END)
            for enemy in variables.enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, "System")
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy)
                else:
                    self.main_window.middle_frame.enemies_listbox.insert(tk.END, enemy[6:])
                self.main_window.middle_frame.enemies_damaged.insert(tk.END, variables.enemydamaged[enemy])
                self.main_window.middle_frame.enemies_damaget.insert(tk.END, variables.enemydamaget[enemy])
            self.main_window.middle_frame.events_button.state(["!disabled"])
            self.main_window.ship_frame.update_ship(variables.ships_list)

class ship_frame(ttk.Frame):
    """
    Simple frame with a picture and a string containing information about the ships
    used by the player.
    -----------------------------------
    | ------------------------------- |
    | |                             | |
    | | image of ship of player     | |
    | |                             | |
    | ------------------------------- |
    | string                          |
    | of                              |
    | text                            |
    |                                 |
    -----------------------------------
    """

    def __init__(self, root_frame):
        """
        Create all labels and variables
        :param root_frame:
        """
        ttk.Frame.__init__(self, root_frame, width = 300, height = 410)
        self.ship_label_var = tk.StringVar()
        self.ship_label_var.set("No match or spawn selected yet.")
        self.ship_label = ttk.Label(self, textvariable = self.ship_label_var, justify = tk.LEFT, wraplength = 495)
        self.ship_image = ttk.Label(self)

    def grid_widgets(self):
        """
        Put the widgets in the right place
        :return:
        """
        self.ship_image.grid(column = 0, row = 0, sticky =tk.N+tk.S+tk.W+tk.E)
        self.ship_label.grid(column = 0, row = 1, sticky =tk.N+tk.S+tk.W+tk.E)
        self.remove_image()

    def update_ship(self, ships_list):
        """
        Update the picture of the ship by using the ships_list as reference
        If more ships are possible, set the default.
        If zero ships are possible, there must be an error somewhere in the abilities module
        :param ships_list:
        :return:
        """
        if len(ships_list) > 1:
            print "[DEBUG] Ship_list larger than 1, setting default.png"
            try:
                self.set_image(os.path.dirname(__file__) + "\\assets\\img\\default.png")
            except IOError:
                print "[DEBUG] File not found."
                tkMessageBox.showerror("Error", "The specified picture can not be found. Is the assets folder copied correctly?")
                return
        elif len(ships_list) == 0:
            raise ValueError("Ships_list == 0")
        else:
            print "[DEBUG]  Ship_list not larger than one, setting appropriate image"
            try:
                self.set_image(os.path.dirname(__file__) + "\\assets\\img\\" + ships_list[0] + ".png")
            except IOError:
                print "[DEBUG] File not found: ", os.path.dirname(__file__) + "\\assets\\img\\" + ships_list[0] + ".png"
                tkMessageBox.showerror("Error", "The specified picture can not be found. Is the assets folder copied correctly?")
                return
        return

    def set_image(self, file):
        """
        Set the image file, unless there is an IOError, because  then the assets folder is not in place
        :param file:
        :return:
        """
        try:
            self.img = Image.open(file)
            self.img = self.img.resize((300,180), Image.ANTIALIAS)
            self.pic = ImageTk.PhotoImage(self.img)
            self.ship_image.config(image=self.pic)
        except IOError:
            raise IOError
        except tk.TclError:
            pass

    def remove_image(self):
        """
        Set the default image
        :return:
        """
        try:
            self.pic = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.realpath(__file__)) + \
                                                     "\\assets\\img\\default.png").resize((300,180),Image.ANTIALIAS))
        except IOError:
            print "[DEBUG] default.png can not be opened."
            return
        try:
            self.ship_image.config(image=self.pic)
        except tk.TclError:
            pass

class middle_frame(ttk.Frame):
    """
    A simple frame containing a notebook with three tabs to show statistics and information to the user
    Main frame:
    ----------------------------------
    |  _____ _____ _____             |
    | |_____|_____|_____|___________ |
    | | frame to display            ||
    | |_____________________________||
    ----------------------------------

    Statistics tab:
    ----------------------------------
    | list                           |
    | of                             |
    | stats                          |
    ----------------------------------

    Enemies tab:
    -----------------------------
    | Help string               |
    | ______ ______ ______ ____ |
    | |enem| |dmgd| |dmgt| |/\| |
    | |enem| |dmgd| |dmgt| |||| |
    | |enem| |dmgd| |dmgt| |\/| |
    | |____| |____| |____| |__| |
    -----------------------------

    Abilities tab:
    -----------------------------
    | ability              |/\| |
    | ability              |||| |
    | ability              |\/| |
    -----------------------------
    """
    def __init__(self, root_frame, main_window):
        """
        Set up all widgets and variables. StringVars can be manipulated by the file frame,
        so that frame can set the statistics to be shown in this frame. Strings for Tkinter
        cannot span multiple lines!
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = main_window
        self.notebook = ttk.Notebook(self, width = 300, height = 310)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text = "Statistics")
        self.notebook.add(self.enemies_frame, text = "Enemies")
        self.events_frame = ttk.Frame(self, width = 300)
        self.events_button = ttk.Button(self.events_frame, text = "Show events for spawn", command=self.show_events,
                                        state=tk.DISABLED, width = 43)
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt to\nDamage dealt:\nDamage taken:\nDamage ratio:\nSelfdamage:\nHealing received:\n" + \
                  "Hitcount:\nCriticalcount:\nCriticalluck:\nDeaths:\nDuration:\nDPS:"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable = self.statistics_label_var, justify = tk.LEFT,
                                          wraplength = 145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable = self.statistics_numbers_var,
                                            justify = tk.LEFT, wraplength = 145)
        self.enemies_label = ttk.Label(self.enemies_frame, text = "Name\t          Damage taken\t      Damage dealt\n")
        self.enemies_listbox = tk.Listbox(self.enemies_frame, width = 17, height = 17)
        self.enemies_damaget = tk.Listbox(self.enemies_frame, width = 14, height = 17)
        self.enemies_damaged = tk.Listbox(self.enemies_frame, width = 14, height = 17)
        self.enemies_scroll = ttk.Scrollbar(self.enemies_frame, orient = tk.VERTICAL,)
        self.enemies_scroll.config(command = self.enemies_scroll_yview)
        self.enemies_listbox.config(yscrollcommand = self.enemies_listbox_scroll)
        self.enemies_damaget.config(yscrollcommand = self.enemies_damaget_scroll)
        self.enemies_damaged.config(yscrollcommand = self.enemies_damaged_scroll)
        self.abilities_scrollable_frame = widgets.vertical_scroll_frame(self.notebook)
        self.abilities_frame = self.abilities_scrollable_frame.interior
        self.notebook.add(self.abilities_scrollable_frame, text = "Abilities")
        self.abilities_label_var = tk.StringVar()
        self.abilities_label = ttk.Label(self.abilities_frame, textvariable = self.abilities_label_var,
                                         justify = tk.LEFT, wraplength = 295)
        self.notice_label = ttk.Label(self.stats_frame, text = "\n\n\n\nThe damage dealt for bombers can not be" +
                " accurately calculated due to CombatLog limitations, as damage dealt by bombs is not recorded.",
                                      justify = tk.LEFT, wraplength = 290)

    def show_events(self):
        """
        Open a TopLevel of the overlay module to show the lines of a Combatlog in a human-readable manner
        :return:
        """
        self.toplevel = toplevels.events_view(self.window, variables.spawn, variables.player_numbers)

    def enemies_scroll_yview(self, *args):
        """
        Combine the scrolling of three listboxes into one
        :param args:
        :return:
        """
        self.enemies_listbox.yview(*args)
        self.enemies_damaged.yview(*args)
        self.enemies_damaget.yview(*args)

    """
    Three functions, all with the same goal: keeping the scroll point of the
    three listboxes synchronized in order to show the correct damage for the
    correct enemy.
    """
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
        """
        Put all widgets in the right place
        :return:
        """
        self.abilities_label.grid(column = 0, row = 2, columnspan = 4, sticky = tk.N + tk.W)
        self.notebook.grid(column = 0, row = 0, columnspan = 4, sticky = tk.N  + tk.W + tk.E)
        self.events_frame.grid(column = 0, row = 1, columnspan = 4, sticky=tk.N+tk.W+tk.S+tk.E)
        self.events_button.grid(column = 0, row = 1,sticky=tk.N+tk.W+tk.S+tk.E, columnspan = 4, pady = 12)
        self.statistics_label.grid(column = 0, row = 2, columnspan = 2, sticky = tk.N + tk.S + tk.W + tk.E)
        self.statistics_numbers.grid(column = 2, row = 2, columnspan = 2, sticky = tk.N + tk.W + tk.E)
        self.notice_label.grid(column = 0, row = 3, columnspan = 4, sticky = tk.W+tk.E+tk.S)
        self.enemies_label.grid(column = 0, row = 0, columnspan = 3)
        self.enemies_listbox.grid(column = 0, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaged.grid(column = 1, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_damaget.grid(column = 2, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
        self.enemies_scroll.grid(column = 3, row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
