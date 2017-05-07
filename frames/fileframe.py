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
import tkFileDialog
import operator
import os
import re
from datetime import datetime
import variables
from parsing import parse, abilities, folderstats, filestats, matchstats, spawnstats
from toplevels import SplashScreen


# Class for the _frame in the fileTab of the parser
class FileFrame(ttk.Frame):
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
        ttk.Frame.__init__(self, root_frame, width=200, height=420)
        self.main_window = main_window
        self.file_box = tk.Listbox(self)
        self.file_box_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.file_box_scroll.config(command=self.file_box.yview)
        self.file_box.config(yscrollcommand=self.file_box_scroll.set)
        self.match_box = tk.Listbox(self)
        self.match_box_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.match_box_scroll.config(command=self.match_box.yview)
        self.match_box.config(yscrollcommand=self.match_box_scroll.set)
        self.spawn_box = tk.Listbox(self)
        self.spawn_box_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.spawn_box.yview)
        self.spawn_box.config(yscrollcommand=self.spawn_box_scroll.set)

        self.file_box.bind("<Double-Button-1>", self.file_update)
        self.match_box.bind("<Double-Button-1>", self.match_update)
        self.spawn_box.bind("<Double-Button-1>", self.spawn_update)
        self.file_box.bind("<Return>", self.file_update)
        self.match_box.bind("<Return>", self.match_update)
        self.spawn_box.bind("<Return>", self.spawn_update)

        self.file_box.bind("<Enter>", self.bind_file)
        self.file_box.bind("<Leave>", self.unbind_file)
        self.match_box.bind("<Enter>", self.bind_match)
        self.match_box.bind("<Leave>", self.unbind_match)
        self.spawn_box.bind("<Enter>", self.bind_spawn)
        self.spawn_box.bind("<Leave>", self.unbind_spawn)

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.add_files_cb)
        self.filters_button = ttk.Button(self, text="Filters", command=self.filters)
        self.old_file = 0
        self.old_match = 0
        self.old_spawn = 0

    def scroll_file(self, event):
        self.file_box.yview_scroll(-1 * (event.delta / 100), "units")

    def bind_file(self, event):
        self.main_window.bind("<MouseWheel>", self.scroll_file)
        self.file_box.focus()

    def unbind_file(self, event):
        self.main_window.unbind("<MouseWheel>")

    def scroll_match(self, event):
        self.match_box.yview_scroll(-1 * (event.delta / 100), "units")

    def bind_match(self, event):
        self.main_window.bind("<MouseWheel>", self.scroll_match)
        self.match_box.focus()

    def unbind_match(self, event):
        self.main_window.unbind("<MouseWheel>")

    def scroll_spawn(self, event):
        self.spawn_box.yview_scroll(-1 * (event.delta / 100), "units")

    def bind_spawn(self, event):
        self.main_window.bind("<MouseWheel>", self.scroll_spawn)
        self.spawn_box.focus()

    def unbind_spawn(self, event):
        self.main_window.unbind("<MouseWheel>")

    def filters(self):
        """
        Opens Toplevel to enable filters and then adds the filtered CombatLogs to the Listboxes
        """
        tkMessageBox.showinfo("Notice", "This button is not yet functional.")

    def grid_widgets(self):
        """
        Put all widgets in the right places
        :return:
        """

        self.file_box.config(height=6)
        self.match_box.config(height=6)
        self.spawn_box.config(height=6)
        self.file_box.grid(column=0, row=0, columnspan=2, padx=5, pady=5)
        self.file_box_scroll.grid(column=2, row=0, rowspan=8, columnspan=1, sticky=tk.N + tk.S, pady=5)
        self.match_box.grid(column=0, row=8, columnspan=2, padx=5, pady=5)
        self.match_box_scroll.grid(column=2, row=8, columnspan=1, sticky=tk.N + tk.S, pady=5)
        self.spawn_box.grid(column=0, row=16, columnspan=2, padx=5, pady=5)
        self.spawn_box_scroll.grid(column=2, row=16, columnspan=1, sticky=tk.N + tk.S, pady=5)
        self.refresh_button.grid(column=0, columnspan=3, row=17, rowspan=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.filters_button.grid(column=0, columnspan=3, row=18, rowspan=1, sticky=tk.N + tk.S + tk.W + tk.E)

    def add_matches(self):
        """
        Function that adds the matches found in the file selected to the appropriate listbox
        :return:
        """

        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        with open(variables.settings_obj.cl_path + "/" + variables.file_name, "r") as file:
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

        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children(""))
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        self.spawn_timing_strings = []
        if variables.match_timing:
            try:
                index = self.match_timing_strings.index(variables.match_timing)
            except ValueError:
                self.spawn_box.delete(0, tk.END)
                return
            variables.spawn_index = index
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

        self.file_strings = []
        self.files_dict = {}
        self.file_box.delete(0, tk.END)
        self.match_box.delete(0, tk.END)
        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children(""))
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        self.splash = SplashScreen(self.main_window)
        try:
            old_path = os.getcwd()
            os.chdir(variables.settings_obj.cl_path)
            os.chdir(old_path)
        except OSError:
            tkMessageBox.showerror("Error", "The CombatLogs folder found in the settings file is not valid. Please "
                                            "choose another folder.")
            folder = tkFileDialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            variables.settings_obj.read_set()
        for file in os.listdir(variables.settings_obj.cl_path):
            if file.endswith(".txt"):
                if parse.check_gsf(variables.settings_obj.cl_path + "/" + file):
                    try:
                        if variables.settings_obj.date_format == "ymd":
                            dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
                        elif variables.settings_obj.date_format == "ydm":
                            dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime(
                                "%Y-%d-%m   %H:%M:%S")
                        else:
                            tkMessageBox.showerror("No valid date format setting found.")
                            return
                    except ValueError:
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

        self.file_strings = []
        self.files_dict = {}
        self.file_box.delete(0, tk.END)
        self.match_box.delete(0, tk.END)
        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        if not silent:
            self.splash = SplashScreen(self.main_window)
        try:
            old_cwd = os.getcwd()
            os.chdir(variables.settings_obj.cl_path)
            os.chdir(old_cwd)
        except OSError:
            tkMessageBox.showerror("Error", "The CombatLogs folder found in the settings file is not valid. Please "
                                            "choose another folder.")
            folder = tkFileDialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            variables.settings_obj.read_set()
        for file in os.listdir(variables.settings_obj.cl_path):
            if file.endswith(".txt"):
                if parse.check_gsf(variables.settings_obj.cl_path + "/" + file):
                    try:
                        dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
                    except ValueError:
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
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        for index, filestring in enumerate(self.file_box.get(0, tk.END)):
            self.file_box.itemconfig(index, background="white")
        if self.file_box.curselection() == (0,) or self.file_box.curselection() == ('0',):
            self.old_file = 0
            self.file_box.itemconfig(self.old_file, background="lightgrey")
            (abilities_dict, statistics_string, shipsdict, enemies, enemydamaged,
             enemydamaget, uncounted) = folderstats.folder_statistics()
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                if variables.settings_obj.faction == "republic":
                    name = abilities.rep_strings[ship]
                else:
                    name = ship
                try:
                    ships_string += name + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += name + "\t\t0\n"
            ships_string += "Uncounted\t\t" + str(uncounted)
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            most_used_ship = max(shipsdict.iteritems(), key=operator.itemgetter(1))[0]
            self.main_window.ship_frame.update_ship([most_used_ship])
            self.main_window.ship_frame.update()
        else:
            self.match_box.focus()
            # Find the file name of the file selected in the list of file names
            numbers = self.file_box.curselection()
            self.old_file = numbers[0]
            self.file_box.itemconfig(self.old_file, background="lightgrey")
            try:
                variables.file_name = self.files_dict[self.file_strings[numbers[0] - 1]]
            except TypeError:
                variables.file_name = self.files_dict[self.file_strings[int(numbers[0]) - 1]]
            except KeyError:
                tkMessageBox.showerror("Error", "The parser encountered an error while selecting the file. Please "
                                                "consult the issues page of the GitHub repository.")
            # Read all the lines from the selected file
            with open(variables.settings_obj.cl_path + "/" + variables.file_name, "rU") as clicked_file:
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
        for index, matchstring in enumerate(self.match_box.get(0, tk.END)):
            self.match_box.itemconfig(index, background="white")
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        if self.match_box.curselection() == (0,) or self.match_box.curselection() == ('0',):
            self.spawn_box.delete(0, tk.END)
            numbers = self.match_box.curselection()
            self.old_match = numbers[0]
            self.match_box.itemconfig(self.old_match, background="lightgrey")
            try:
                variables.match_timing = self.match_timing_strings[numbers[0] - 1]
            except TypeError:
                variables.match_timing = self.match_timing_strings[int(numbers[0]) - 1]
            file_cube = variables.file_cube
            (abilities_dict, statistics_string, shipsdict, enemies,
             enemydamaged, enemydamaget, uncounted) = filestats.file_statistics(file_cube)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                if variables.settings_obj.faction == "republic":
                    name = abilities.rep_strings[ship]
                else:
                    name = ship

                try:
                    ships_string += name + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += name + "\t\t0\n"
            ships_string += "Uncounted\t\t" + str(uncounted)
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
        else:
            self.spawn_box.focus()
            numbers = self.match_box.curselection()
            self.old_match = numbers[0]
            self.match_box.itemconfig(self.old_match, background="lightgrey")
            try:
                variables.match_timing = self.match_timing_strings[numbers[0] - 1]
            except TypeError:
                variables.match_timing = self.match_timing_strings[int(numbers[0]) - 1]
            self.add_spawns()
        self.main_window.ship_frame.remove_image()

    def spawn_update(self, instance):
        """
        Either starts the parsing of ALL spawns found in the specified match or just one of them
        and displays the results in the other frames accordingly
        :param instance: for Tkinter callback
        :return:
        """
        for index, spawnstring in enumerate(self.spawn_box.get(0, tk.END)):
            self.spawn_box.itemconfig(index, background="white")
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        if self.spawn_box.curselection() == (0,) or self.spawn_box.curselection() == ('0',):
            self.old_spawn = self.spawn_box.curselection()[0]
            self.spawn_box.itemconfig(self.old_spawn, background="lightgrey")
            match = variables.file_cube[self.match_timing_strings.index(variables.match_timing)]
            for spawn in match:
                variables.player_numbers.update(parse.determinePlayer(spawn))
            (abilities_dict, statistics_string, shipsdict, enemies,
             enemydamaged, enemydamaget) = matchstats.match_statistics(match)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                if variables.settings_obj.faction == "republic":
                    name = abilities.rep_strings[ship]
                else:
                    name = ship

                try:
                    ships_string += name + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += name + "\t\t0\n"
            ships_string += "Uncounted\t\t%s" % shipsdict["Uncounted"]
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            self.main_window.ship_frame.remove_image()
        else:
            numbers = self.spawn_box.curselection()
            self.old_spawn = numbers[0]
            self.spawn_box.itemconfig(self.old_spawn, background="lightgrey")
            try:
                variables.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            except TypeError:
                try:
                    variables.spawn_timing = self.spawn_timing_strings[int(numbers[0]) - 1]
                except:
                    tkMessageBox.showerror("Error",
                                           "The parser encountered a bug known as #19 in the repository. "
                                           "This bug has not been fixed. Check out issue #19 in the repository"
                                           " for more information.")
            try:
                match = variables.file_cube[self.match_timing_strings.index(variables.match_timing)]
            except ValueError:
                print "[DEBUG] vars.match_timing not in self.match_timing_strings!"
                return
            spawn = match[self.spawn_timing_strings.index(variables.spawn_timing)]
            variables.spawn = spawn
            variables.player_numbers = parse.determinePlayer(spawn)
            (abilities_dict, statistics_string, ships_list, ships_comps,
             enemies, enemydamaged, enemydamaget) = spawnstats.spawn_statistics(spawn)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            ships_string = "Possible ships used:\n"
            for ship in ships_list:
                if variables.settings_obj.faction == "republic":
                    name = abilities.rep_ships[ship]
                else:
                    name = ship

                ships_string += str(name) + "\n"
            ships_string += "\t\t\t\t\t\t\nWith the components:\n"
            for component in ships_comps:
                ships_string += component + "\n"
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.state(["!disabled"])
            self.main_window.ship_frame.update_ship(ships_list)
