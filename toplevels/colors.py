# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
import variables
import tkinter.colorchooser
import collections
import struct
import tkinter.filedialog
import tempfile


class EventColors(tk.Toplevel):
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
        for key in self.colors.keys():
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
        for key in self.color_descriptions.keys():
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
        file_to_open = tkinter.filedialog.askopenfile(filetypes=[("Settings file", ".ini")],
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
        for key in self.color_entry_vars_bg.keys():
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(self.colors[key][0])
            self.color_entry_widgets_fg[key].insert(self.colors[key][1])
        self.focus_set()

    def export_button_cb(self):
        file_to_save = tkinter.filedialog.asksaveasfilename(defaultextension=".ini",
                                                            filetypes=[("Settings file", ".ini")],
                                                            initialdir=tempfile.gettempdir().replace("temp",
                                                                                                     "GSF Parser") \
                                                                       + "\\event_colors.ini",
                                                            parent=self, title="GSF Parser: Export colors to file")
        if not file_to_save:
            self.focus_set()
            return
        for color, variable in self.color_entry_vars_bg.items():
            self.colors[color][0] = variable.get()
        for color, variable in self.color_entry_vars_fg.items():
            self.colors[color][1] = variable.get()
        for color, lst in self.colors.items():
            variables.color_scheme[color] = lst
        variables.color_scheme.write_custom(custom_file=file_to_save)
        self.focus_set()

    def set_color(self, key, fg=False):
        if not fg:
            color_tuple = tkinter.colorchooser.askcolor(color=self.color_entry_widgets_bg[key].get(),
                                                        title="GSF Parser: Choose color for %s" %
                                                              self.color_descriptions[
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
            color_tuple = tkinter.colorchooser.askcolor(color=self.color_entry_widgets_fg[key].get(),
                                                        title="GSF Parser: Choose color for %s" %
                                                              self.color_descriptions[
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
        for color, widget in self.color_entry_widgets_bg.items():
            self.colors[color][0] = widget.get()
        for color, widget in self.color_entry_widgets_fg.items():
            self.colors[color][1] = widget.get()
        for color, lst in self.colors.items():
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
        for key in self.colors.keys():
            self.color_labels[key].grid(column=0, columnspan=2, row=set_row, sticky=tk.W)
            self.color_entry_widgets_bg[key].grid(column=2, row=set_row, sticky=tk.W, padx=5)
            self.color_button_widgets_bg[key].grid(column=3, row=set_row, sticky=tk.W)
            self.color_entry_widgets_fg[key].grid(column=4, row=set_row, sticky=tk.W, padx=5)
            self.color_button_widgets_fg[key].grid(column=5, row=set_row, sticky=tk.W)
            set_row += 1
        self.separator.grid(column=0, columnspan=6, sticky=tk.N + tk.S + tk.W + tk.E, pady=5)
        set_row += 1
        self.cancel_button.grid(column=3, columnspan=2, row=set_row, sticky=tk.N + tk.S + tk.E)
        self.ok_button.grid(column=5, row=set_row, sticky=tk.N + tk.S + tk.W + tk.E)
        self.import_button.grid(column=0, row=set_row, sticky=tk.N + tk.S + tk.W + tk.E)
        self.export_button.grid(column=1, row=set_row, sticky=tk.N + tk.S + tk.W + tk.E)
