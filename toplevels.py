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
import tkColorChooser
import tkFileDialog
import os
import sys
import tempfile
import collections
import struct

from PIL import ImageTk, Image

import variables
from parsing import statistics, abilities
import frames.widgets


class splash_screen(tk.Toplevel):
    def __init__(self, window, boot=False, max=None, title="GSF Parser"):
        tk.Toplevel.__init__(self, window)
        self.grab_set()
        self.title(title)
        self.label = ttk.Label(self, text="Working...")
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()
        try:
            list = os.listdir(variables.settings_obj.cl_path)
        except OSError:
            tkMessageBox.showerror("Error", "The CombatLogs folder found in the settings file is not valid. Please "
                                            "choose another folder.")
            folder = tkFileDialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            list = os.listdir(variables.settings_obj.cl_path)
        except:
            print "[DEBUG] Running on UNIX, functionality disabled"
            return
        files = []
        for file in list:
            if file.endswith(".txt"):
                files.append(file)
        variables.files_done = 0
        if not max:
            self.amount_files = len(files)
        else:
            self.amount_files = max
        if (self.amount_files >= 50 and boot):
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombatLogs folder. " + \
                                  "You may want to archive some of your %s CombatLogs in order to speed up the parsing " + \
                                  "program and the startup times." % self.amount_files)
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self):
        self.progress_bar["value"] = variables.files_done
        self.update()


class overlay(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.update_position()
        if sys.platform == "win32":
            try:
                with open(tempfile.gettempdir().replace("temp", "") + "/SWTOR/swtor/settings/client_settings.ini",
                          "r") as swtor:
                    if "D3DFullScreen = true" in swtor:
                        tkMessageBox.showerror("Error",
                                               "The overlay cannot be shown with the current SWTOR settings. " + \
                                               "Please set SWTOR to Fullscreen (windowed) in the Graphics settings.")
            except IOError:
                tkMessageBox.showerror("Error",
                                       "The settings file for SWTOR cannot be found. Is SWTOR correctly installed?")
        print "[DEBUG] Setting overlay font to: ", (
            variables.settings_obj.overlay_tx_font, variables.settings_obj.overlay_tx_size)
        if variables.settings_obj.size == "big":
            self.text_label = ttk.Label(self, text="Damage done:\nDamage taken:\nHealing "
                                                   "recv:\nSelfdamage:\nRecent enemies:\nSpawns:",
                                        justify=tk.LEFT, font=(
                variables.settings_obj.overlay_tx_font, int(variables.settings_obj.overlay_tx_size)),
                                        foreground=variables.settings_obj.overlay_tx_color,
                                        background=variables.settings_obj.overlay_bg_color)
        elif variables.settings_obj.size == "small":
            self.text_label = ttk.Label(self, text="DD:\nDT:\nHR:\nSD:", justify=tk.LEFT,
                                        font=(variables.settings_obj.overlay_tx_font,
                                              int(variables.settings_obj.overlay_tx_size)),
                                        foreground=variables.settings_obj.overlay_tx_color,
                                        background=variables.settings_obj.overlay_bg_color)
        else:
            raise ValueError("Size setting not valid.")
        self.stats_var = tk.StringVar()
        self.stats_label = ttk.Label(self, textvariable=self.stats_var, justify=tk.RIGHT,
                                     font=(variables.settings_obj.overlay_tx_font,
                                           int(variables.settings_obj.overlay_tx_size)),
                                     foreground=variables.settings_obj.overlay_tx_color,
                                     background=variables.settings_obj.overlay_bg_color)
        self.text_label.pack(side=tk.LEFT)
        self.stats_label.pack(side=tk.RIGHT)
        self.configure(background=variables.settings_obj.overlay_bg_color)
        self.wm_attributes("-transparentcolor", variables.settings_obj.overlay_tr_color)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", variables.settings_obj.opacity)

    def update_position(self):
        if variables.settings_obj.size == "big":
            h_req = (int(variables.settings_obj.overlay_tx_size) * 1.6) * 6
            w_req = ((int(variables.settings_obj.overlay_tx_size) / 1.5) + 2) * (14 + 6)
        elif variables.settings_obj.size == "small":
            h_req = (int(variables.settings_obj.overlay_tx_size) * 1.6) * 4
            w_req = ((int(variables.settings_obj.overlay_tx_size) / 1.5) + 2) * (4 + 6)
        else:
            raise
        if variables.settings_obj.pos == "TL":
            pos_c = "+0+0"
        elif variables.settings_obj.pos == "BL":
            pos_c = "+0+%s" % (int(variables.screen_h) - int(h_req))
        elif variables.settings_obj.pos == "TR":
            pos_c = "+%s+0" % (int(variables.screen_w) - int(w_req))
        elif variables.settings_obj.pos == "BR":
            pos_c = "+%s+%s" % (int(variables.screen_w) - int(w_req), int(variables.screen_h) - int(h_req))
        elif variables.settings_obj.pos == "UC":
            pos_c = "+0+%s" % int(0.25 * variables.screen_h)
        elif variables.settings_obj.pos == "NQ":
            pos_c = "+%s+%s" % (int(variables.screen_w * 0.25), int(variables.screen_h) - int(h_req))
        elif variables.settings_obj.pos == "UT":
            pos_c = "+%s+%s" % (int(variables.screen_w) - int(w_req),
                                variables.screen_h - int(0.75 * variables.screen_h))
        else:
            raise ValueError("vars.settings_obj.pos not valid")
        self.wm_geometry("%sx%s" % (int(w_req), int(h_req)) + pos_c)
        print "[DEBUG] Overlay position set to: ", "%sx%s" % (int(w_req), int(h_req)) + pos_c


class privacy(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        privacy = variables.client_obj.get_privacy()
        privacy_listbox = tk.Listbox(self, height=10, width=30)
        privacy_listbox.pack(side=tk.LEFT)
        privacy_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=privacy_listbox.yview)
        privacy_listbox.config(yscrollcommand=privacy_scroll.set)
        if privacy == -1:
            self.destroy()
            return
        try:
            privacy_list = list(privacy)
        except:
            tkMessageBox.showerror("Error", "Data in privacy statement received is not valid.")
            return
        index = 0
        for line in privacy_list:
            privacy_listbox.insert(0, line)
            index += 1


class boot_splash(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Starting...")
        print variables.settings_obj.logo_color
        try:
            self.logo = ImageTk.PhotoImage(
                Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\assets\\logos\\logo_" + \
                           variables.settings_obj.logo_color + ".png"))
            self.panel = ttk.Label(self, image=self.logo)
            self.panel.pack()
        except:
            print "[DEBUG] No logo.png found in the home folder."
        self.window = window
        self.label_var = tk.StringVar()
        self.label_var.set("Connecting to specified server...")
        self.label = ttk.Label(self, textvariable=self.label_var)
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=462, mode="determinate")
        self.progress_bar.pack()
        try:
            directory = os.listdir(window.default_path)
        except OSError:
            tkMessageBox.showerror("Error", "The CombatLogs folder found in the settings file is not valid. Please "
                                            "choose another folder.")
            folder = tkFileDialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            variables.settings_obj.read_set()
            os.chdir(variables.settings_obj.cl_path)
            directory = os.listdir(os.getcwd())
        files = []
        for file in directory:
            if file.endswith(".txt"):
                files.append(file)
        variables.files_done = 0
        self.amount_files = len(files)
        """
        if self.amount_files >= 50:
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombadwLogs folder. "+\
            "You may want to archive some of your %s CombatLogs in order to speed up the parsing program and the "+\
            "startup times." % self.amount_files)
        """
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()
        self.done = False

    def update_progress(self):
        if variables.files_done != self.amount_files:
            self.label_var.set("Parsing the files...")
            self.progress_bar["value"] = variables.files_done
            self.update()
        else:
            return


class conn_splash(tk.Toplevel):
    def __init__(self, window=variables.main_window):
        tk.Toplevel.__init__(self, window)
        self.window = window
        self.FLAG = False
        self.title("GSF Parser: Connecting...")
        self.label = ttk.Label(self, text="Connecting to specified server...")
        self.label.pack()
        self.conn_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate")
        self.conn_bar.pack()
        self.window.after(500, self.connect)

    def connect(self):
        if not self.FLAG:
            self.update()
            self.window.after(500, self.connect)
        else:
            return


class events_view(tk.Toplevel):
    def __init__(self, window, spawn, player):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Events for spawn on %s of match started at %s" % (
        variables.spawn_timing, variables.match_timing))
        self.listbox = tk.Listbox(self, width=100, height=15, font=("Consolas", 10))
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.grid(column=1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.scroll.grid(column=2, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.resizable(width=False, height=False)
        for line in spawn:
            event = statistics.print_event(line, variables.spawn_timing, player)
            if not isinstance(event, tuple):
                pass
            if event is not None:
                self.listbox.insert(tk.END, event[0])
                self.listbox.itemconfig(tk.END, fg=event[2], bg=event[1])


class event_colors(tk.Toplevel):
    """
    A class for a Toplevel that lets the user set their own custom HTML colors for events.
    List of colors that need to be set:
    Damage dealt primaries
    Damage taken primaries
    Damage dealt secondaries
    Damage taken secondaries
    Selfdamage
    Healing
    Selfhealing
    Engine ability
    Shield ability
    System ability
    Other abilities
    """

    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Choose event colors")
        self.resizable(False, False)
        self.column_label_one = ttk.Label(self, text="Type of event", font=("Calibri", 12))
        self.column_label_two = ttk.Label(self, text="Background color", font=("Calibri", 12))
        self.column_label_three = ttk.Label(self, text="Text color", font=("Calibri", 12))
        self.colors = collections.OrderedDict()
        variables.color_scheme.set_scheme(variables.settings_obj.event_scheme)
        self.colors['dmgd_pri'] = [variables.color_scheme['dmgd_pri'][0], variables.color_scheme['dmgd_pri'][1]]
        self.colors['dmgt_pri'] = [variables.color_scheme['dmgt_pri'][0], variables.color_scheme['dmgt_pri'][1]]
        self.colors['dmgd_sec'] = [variables.color_scheme['dmgd_sec'][0], variables.color_scheme['dmgd_sec'][1]]
        self.colors['dmgt_sec'] = [variables.color_scheme['dmgt_sec'][0], variables.color_scheme['dmgt_sec'][1]]
        self.colors['selfdmg'] = [variables.color_scheme['selfdmg'][0], variables.color_scheme['selfdmg'][1]]
        self.colors['healing'] = [variables.color_scheme['healing'][0], variables.color_scheme['healing'][1]]
        self.colors['selfheal'] = [variables.color_scheme['selfheal'][0], variables.color_scheme['selfheal'][1]]
        self.colors['engine'] = [variables.color_scheme['engine'][0], variables.color_scheme['engine'][1]]
        self.colors['shield'] = [variables.color_scheme['shield'][0], variables.color_scheme['shield'][1]]
        self.colors['system'] = [variables.color_scheme['system'][0], variables.color_scheme['system'][1]]
        self.colors['other'] = [variables.color_scheme['other'][0], variables.color_scheme['other'][1]]
        self.colors['spawn'] = [variables.color_scheme['spawn'][0], variables.color_scheme['spawn'][1]]
        self.colors['match'] = [variables.color_scheme['match'][0], variables.color_scheme['match'][1]]
        self.colors['default'] = [variables.color_scheme['default'][0], variables.color_scheme['default'][1]]
        self.color_descriptions = {'dmgd_pri': "Damage dealt by Primary Weapons: ",
                                   'dmgt_pri': "Damage taken from Primary Weapons: ",
                                   'dmgd_sec': "Damage dealt by Secondary Weapons: ",
                                   'dmgt_sec': "Damage taken from Secondary Weapons: ",
                                   'selfdmg': "Selfdamage: ",
                                   'healing': "Healing received from others: ",
                                   'selfheal': "Healing received from yourself: ",
                                   'engine': "Activation of engine abilities: ",
                                   'shield': "Activation of shield abilities: ",
                                   'system': "Activation of system abilities: ",
                                   'other': "Activation of other abilities: ",
                                   'spawn': "End of a spawn: ",
                                   'match': "End of a match: ",
                                   'default': "Unmatched categories: "}
        self.color_labels = {}
        self.color_entry_vars_bg = {}
        self.color_entry_vars_fg = {}
        self.color_entry_widgets_bg = {}
        self.color_entry_widgets_fg = {}
        self.color_button_widgets_fg = {}
        self.color_button_widgets_bg = {}
        for key in self.colors.iterkeys():
            self.color_labels[key] = ttk.Label(self, text=self.color_descriptions[key], justify=tk.LEFT)
            self.color_button_widgets_fg[key] = ttk.Button(self, text="Choose",
                                                           command=lambda color=key: self.set_color(color, fg=True))
            self.color_button_widgets_bg[key] = ttk.Button(self, text="Choose",
                                                           command=lambda color=key: self.set_color(color))
            self.color_entry_widgets_fg[key] = tk.Entry(self, font=("Consolas", 10), width=10)
            self.color_entry_widgets_bg[key] = tk.Entry(self, font=("Consolas", 10), width=10)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.ok_button = ttk.Button(self, text="OK", width=10, command=self.ok_button_cb)
        self.cancel_button = ttk.Button(self, text="Cancel", width=10, command=self.cancel_button_cb)
        self.import_button = ttk.Button(self, text="Import", width=10, command=self.import_button_cb)
        self.export_button = ttk.Button(self, text="Export", width=10, command=self.export_button_cb)
        for key in self.color_descriptions.iterkeys():
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(0, self.colors[key][0])
            self.color_entry_widgets_fg[key].insert(0, self.colors[key][1])
            color_tuple = struct.unpack("BBB", self.colors[key][0].replace("#", "").decode('hex'))
            red = int(color_tuple[0])
            green = int(color_tuple[1])
            blue = int(color_tuple[2])
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_bg[key].config(foreground=foreground_color, background=self.colors[key][0])
            color_tuple = struct.unpack("BBB", self.colors[key][1].replace("#", "").decode('hex'))
            red = int(color_tuple[0])
            green = int(color_tuple[1])
            blue = int(color_tuple[2])
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_fg[key].config(foreground=foreground_color, background=self.colors[key][1])

    def import_button_cb(self):
        file_to_open = tkFileDialog.askopenfile(filetypes=[("Settings file", ".ini")],
                                                initialdir=tempfile.gettempdir().replace("temp", "GSF Parser") \
                                                           + "\\event_colors.ini",
                                                parent=self, title="GSF Parser: Import colors from file")
        if not file_to_open:
            self.focus_set()
            return
        variables.color_scheme.set_scheme("custom", custom_file=file_to_open)
        self.colors['dmgd_pri'] = [variables.color_scheme['dmgd_pri'][0], variables.color_scheme['dmgd_pri'][1]]
        self.colors['dmgt_pri'] = [variables.color_scheme['dmgt_pri'][0], variables.color_scheme['dmgt_pri'][1]]
        self.colors['dmgd_sec'] = [variables.color_scheme['dmgd_sec'][0], variables.color_scheme['dmgd_sec'][1]]
        self.colors['dmgt_sec'] = [variables.color_scheme['dmgt_sec'][0], variables.color_scheme['dmgt_sec'][1]]
        self.colors['selfdmg'] = [variables.color_scheme['selfdmg'][0], variables.color_scheme['selfdmg'][1]]
        self.colors['healing'] = [variables.color_scheme['healing'][0], variables.color_scheme['healing'][1]]
        self.colors['selfheal'] = [variables.color_scheme['selfheal'][0], variables.color_scheme['selfheal'][1]]
        self.colors['engine'] = [variables.color_scheme['engine'][0], variables.color_scheme['engine'][1]]
        self.colors['shield'] = [variables.color_scheme['shield'][0], variables.color_scheme['shield'][1]]
        self.colors['system'] = [variables.color_scheme['system'][0], variables.color_scheme['system'][1]]
        self.colors['other'] = [variables.color_scheme['other'][0], variables.color_scheme['other'][1]]
        self.colors['spawn'] = [variables.color_scheme['spawn'][0], variables.color_scheme['spawn'][1]]
        self.colors['match'] = [variables.color_scheme['match'][0], variables.color_scheme['match'][1]]
        self.colors['default'] = [variables.color_scheme['default'][0], variables.color_scheme['default'][1]]
        for key in self.color_entry_vars_bg.iterkeys():
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(self.colors[key][0])
            self.color_entry_widgets_fg[key].insert(self.colors[key][1])
        self.focus_set()

    def export_button_cb(self):
        file_to_save = tkFileDialog.asksaveasfilename(defaultextension=".ini", filetypes=[("Settings file", ".ini")],
                                                      initialdir=tempfile.gettempdir().replace("temp", "GSF Parser") \
                                                                 + "\\event_colors.ini",
                                                      parent=self, title="GSF Parser: Export colors to file")
        if not file_to_save:
            self.focus_set()
            return
        for color, variable in self.color_entry_vars_bg.iteritems():
            self.colors[color][0] = variable.get()
        for color, variable in self.color_entry_vars_fg.iteritems():
            self.colors[color][1] = variable.get()
        for color, lst in self.colors.iteritems():
            variables.color_scheme[color] = lst
        variables.color_scheme.write_custom(custom_file=file_to_save)
        self.focus_set()

    def set_color(self, key, fg=False):
        if not fg:
            color_tuple = tkColorChooser.askcolor(color=self.color_entry_widgets_bg[key].get(),
                                                  title="GSF Parser: Choose color for %s" % self.color_descriptions[
                                                      key])
            try:
                red = int(color_tuple[0][0])
                green = int(color_tuple[0][1])
                blue = int(color_tuple[0][2])
            except TypeError:
                self.focus_set()
                return
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(0, color_tuple[1])
            self.color_entry_widgets_bg[key].config(background=color_tuple[1],
                                                    foreground=foreground_color)
        else:
            color_tuple = tkColorChooser.askcolor(color=self.color_entry_widgets_fg[key].get(),
                                                  title="GSF Parser: Choose color for %s" % self.color_descriptions[
                                                      key])
            try:
                red = int(color_tuple[0][0])
                green = int(color_tuple[0][1])
                blue = int(color_tuple[0][2])
            except TypeError:
                self.focus_set()
                return
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].insert(0, color_tuple[1])
            self.color_entry_widgets_fg[key].config(background=color_tuple[1],
                                                    foreground=foreground_color)
        self.focus_set()

    def ok_button_cb(self):
        for color, widget in self.color_entry_widgets_bg.iteritems():
            self.colors[color][0] = widget.get()
        for color, widget in self.color_entry_widgets_fg.iteritems():
            self.colors[color][1] = widget.get()
        for color, lst in self.colors.iteritems():
            variables.color_scheme[color] = lst
        variables.color_scheme.write_custom()
        self.destroy()

    def cancel_button_cb(self):
        self.destroy()

    def grid_widgets(self):
        self.column_label_one.grid(column=0, columnspan=2, row=0, sticky=tk.W)
        self.column_label_two.grid(column=2, columnspan=2, row=0, sticky=tk.W)
        self.column_label_three.grid(column=4, columnspan=2, row=0, sticky=tk.W)
        set_row = 1
        for key in self.colors.iterkeys():
            self.color_labels[key].grid(column=0, columnspan=2, row=set_row, sticky=tk.W)
            self.color_entry_widgets_bg[key].grid(column=2, row=set_row, sticky=tk.W, padx=5)
            self.color_button_widgets_bg[key].grid(column=3, row=set_row, sticky=tk.W)
            self.color_entry_widgets_fg[key].grid(column=4, row=set_row, sticky=tk.W, padx=5)
            self.color_button_widgets_fg[key].grid(column=5, row=set_row, sticky=tk.W)
            set_row += 1
        self.separator.grid(column=0, columnspan=6, sticky=tk.N+tk.S+tk.W+tk.E, pady=5)
        set_row += 1
        self.cancel_button.grid(column=3, columnspan=2, row=set_row, sticky=tk.N + tk.S + tk.E)
        self.ok_button.grid(column=5, row=set_row, sticky=tk.N+tk.S+tk.W+tk.E)
        self.import_button.grid(column=0, row=set_row, sticky=tk.N+tk.S+tk.W+tk.E)
        self.export_button.grid(column=1, row=set_row, sticky=tk.N+tk.S+tk.W+tk.E)


class filters(tk.Toplevel):
    """
    A class for a Toplevel that shows all possible filters that can be applied to CombatLogs. Using expandable frames,
    the settings in a certain category can be shown or hidden. If all settings are set, the user can click OK and a
    special function is called passing a dictionary of files.
    """

    def __init__(self, window=None):
        tk.Toplevel.__init__(self, window)
        self.description_label = ttk.Label(self, text="Please enter the filters you want to apply",
                                           font=("Calibri", 12))
        print "[DEBUG] Setting up Type filters"
        self.type_frame = frames.widgets.ToggledFrame(self, text="Type")
        self.type_variable = tk.StringVar()
        self.type_variable.set("any")
        self.any_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="Any", variable=self.type_variable,
                                         value="any")
        self.logs_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="CombatLogs", variable=self.type_variable,
                                          value="logs")
        self.matches_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="Matches", variable=self.type_variable,
                                             value="matches")
        self.spawns_radio = ttk.Radiobutton(self.type_frame.sub_frame, text="Spawns", variable=self.type_variable,
                                            value="spawns")
        print "[DEBUG] Setting up date filters"
        self.dateframe = frames.widgets.ToggledFrame(self, text="Date")
        self.start_date_widget = frames.widgets.Calendar(self.dateframe.sub_frame)
        self.end_date_widget = frames.widgets.Calendar(self.dateframe.sub_frame)
        print "[DEBUG] Setting up components filters"
        self.components_frame = frames.widgets.ToggledFrame(self, text="Components")
        self.primaries_frame = frames.widgets.ToggledFrame(self.components_frame.sub_frame, text="Primaries")
        self.secondaries_frame = frames.widgets.ToggledFrame(self.components_frame.sub_frame, text="Secondaries")
        self.engines_frame = frames.widgets.ToggledFrame(self.components_frame.sub_frame, text="Engines")
        self.shields_frame = frames.widgets.ToggledFrame(self.components_frame.sub_frame, text="Shields")
        self.systems_frame = frames.widgets.ToggledFrame(self.components_frame.sub_frame, text="Sytems")
        self.primaries_tickboxes = {}
        self.primaries_tickboxes_vars = {}
        self.secondaries_tickboxes = {}
        self.secondaries_tickboxes_vars = {}
        self.engines_tickboxes = {}
        self.engines_tickboxes_vars = {}
        self.shields_tickboxes = {}
        self.shields_tickboxes_vars = {}
        self.systems_tickboxes = {}
        self.systems_tickboxes_vars = {}
        for primary in abilities.primaries:
            primary_var = tk.IntVar()
            primary_chk = ttk.Checkbutton(self.primaries_frame.sub_frame, text=primary)
            self.primaries_tickboxes[primary] = primary_chk
            self.primaries_tickboxes_vars[primary_chk] = primary_var
        for secondary in abilities.secondaries:
            secondary_var = tk.IntVar()
            secondary_chk = ttk.Checkbutton(self.secondaries_frame.sub_frame, text=secondary)
            self.secondaries_tickboxes[secondary] = secondary_chk
            self.secondaries_tickboxes_vars[secondary_chk] = secondary_var
        for engine in abilities.engines:
            engine_var = tk.IntVar()
            engine_chk = ttk.Checkbutton(self.engines_frame.sub_frame, text=engine)
            self.engines_tickboxes[engine] = engine_chk
            self.engines_tickboxes_vars[engine_chk] = engine_var
        for shield in abilities.shields:
            shield_var = tk.IntVar()
            shield_chk = ttk.Checkbutton(self.shields_frame.sub_frame, text=shield)
            self.shields_tickboxes[shield] = shield_chk
            self.shields_tickboxes_vars[shield_chk] = shield_var
        for system in abilities.systems:
            system_var = tk.IntVar()
            system_chk = ttk.Checkbutton(self.systems_frame.sub_frame, text=system)
            self.systems_tickboxes[system] = system_chk
            self.systems_tickboxes_vars[system_chk] = system_var
        self.comps_dicts = [self.primaries_tickboxes, self.secondaries_tickboxes, self.engines_tickboxes,
                            self.shields_tickboxes, self.systems_tickboxes]
        self.ships_frame = frames.widgets.ToggledFrame(self, text="Ships")
        print "[DEBUG] Setting up buttons"
        self.complete_button = ttk.Button(self, text="Filter", command=self.filter_files)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.search_button = ttk.Button(self, text="Search", command=self.search_files)
        print "[DEBUG] Gridding widgets"
        self.grid_widgets()

    def filter_files(self):
        pass

    def search_files(self):
        """
        Take the inserted filters and calculate how many files/matches/spawns are found when the filters are applied.
        Display a tkMessageBox.showinfo() box to show the user how many are found and show a splash screen while
        searching.
        :return:
        """
        pass

    def grid_widgets(self):
        self.description_label.grid(row=1, column=1, columnspan=3, sticky=tk.W + tk.N + tk.S + tk.E)
        self.type_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W + tk.N + tk.S + tk.E)
        self.dateframe.grid(row=3, column=1, columnspan=3, sticky=tk.W + tk.N + tk.S + tk.E)
        self.components_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W + tk.N + tk.S + tk.E)
        self.ships_frame.grid(row=5, column=1, columnspan=3, sticky=tk.W + tk.N + tk.S + tk.E)
        self.complete_button.grid(row=6, column=1, sticky=tk.W + tk.N + tk.S + tk.E)
        self.search_button.grid(row=6, column=2, sticky=tk.W + tk.N + tk.S + tk.E)
        self.cancel_button.grid(row=6, column=3, sticky=tk.W + tk.N + tk.S + tk.E)

        self.any_radio.grid(row=1, column=1, sticky=tk.W + tk.N + tk.S + tk.E)
        self.logs_radio.grid(row=1, column=2, sticky=tk.W + tk.N + tk.S + tk.E)
        self.matches_radio.grid(row=1, column=3, sticky=tk.W + tk.N + tk.S + tk.E)
        self.spawns_radio.grid(row=1, column=4, sticky=tk.W + tk.N + tk.S + tk.E)

        self.start_date_widget.grid(row=1, column=1, sticky=tk.W + tk.N + tk.S + tk.E)
        self.end_date_widget.grid(row=1, column=2, sticky=tk.W + tk.N + tk.S + tk.E)

        start_row = 1
        start_column = 1
        for dictionary in self.comps_dicts:
            for widget in dictionary.itervalues():
                widget.grid(row=start_row, column=start_column, sticky=tk.W + tk.N)
                start_column += 1
                if start_column == 6:
                    start_column = 1
                    start_row += 1
            start_row += 1

            # TODO: Ships filters frame
