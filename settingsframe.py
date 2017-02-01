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
import tkFileDialog
# General imports
import re
# Own modules
import variables
import toplevels
import widgets

class settings_frame(ttk.Frame):
    """
    A rather complicated Frame with lots of widgets containing the widgets for
    all user-changable settings of the parser. The instance calls on functions
    of a settings.settings instance to write the settings to the file and read
    the settings from the file. The settings.settings instance used is created
    in the variables.py file.
    """

    def __init__(self, root_frame, main_window):
        ### LAY-OUT ###
        ttk.Frame.__init__(self, root_frame)
        self.frame = widgets.vertical_scroll_frame(self, width=790, height=400)
        self.gui_frame = ttk.Frame(self.frame.interior)
        self.entry_frame = ttk.Frame(self.frame.interior)
        self.privacy_frame = ttk.Frame(self.frame.interior)
        self.server_frame = ttk.Frame(self.frame.interior)
        self.upload_frame = ttk.Frame(self.frame.interior)
        self.realtime_frame = ttk.Frame(self.frame.interior)
        self.save_frame = ttk.Frame(self.frame.interior)
        self.license_frame = ttk.Frame(self.frame.interior)
        self.main_window = main_window
        ### GUI SETTINGS ###
        # TODO Add more GUI settings including colours
        self.gui_label = ttk.Label(self.frame.interior, text = "GUI settings", justify=tk.LEFT)
        self.color_label = ttk.Label(self.gui_frame, text = "\tParser text color: ")
        self.color = tk.StringVar()
        self.custom_color_entry = ttk.Entry(self.gui_frame, width = 10)
        self.color_options = []
        self.color_choices = ["darkgreen", "darkblue", "darkred", "black", "white", "custom: "]
        for color in self.color_choices:
            self.color_options.append(ttk.Radiobutton(self.gui_frame, value = str(color), text = color,
                                                      variable = self.color))
        self.color.set(variables.set_obj.color)
        self.logo_color_label = ttk.Label(self.gui_frame, text = "\tParser logo color: ")
        self.logo_color = tk.StringVar()
        self.logo_color_choices = ["green", "blue", "red"]
        self.logo_color_options = []
        self.logo_color.set(variables.set_obj.logo_color)
        for color in self.logo_color_choices:
            self.logo_color_options.append(ttk.Radiobutton(self.gui_frame, value = str(color), text = color,
                                                           variable = self.logo_color))
        ### PARSING SETTINGS ###
        self.parsing_label = ttk.Label(self.frame.interior, text = "Parsing settings", justify=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.entry_frame, width=85, textvariable = self.path_var)
        self.path_entry_button = ttk.Button(self.entry_frame, text = "Choose", command = self.set_directory_dialog)
        self.path_entry_label = ttk.Label(self.entry_frame, text = "\tCombatLogs folder: ")
        self.privacy_label = ttk.Label(self.privacy_frame, text = "\tConnect to server for player identification: ")
        self.privacy_var = tk.BooleanVar()
        self.privacy_select_true = ttk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = True,
                                                   text = "Yes")
        self.privacy_select_false = ttk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = False,
                                                    text = "No")
        ### SHARING SETTINGS ###
        self.sharing_label = ttk.Label(self.frame.interior, text = "Share settings", justify=tk.LEFT)
        self.server_label = ttk.Label(self.server_frame, text = "\tServer for sharing: ")
        self.server_address_entry = ttk.Entry(self.server_frame, width=35)
        self.server_colon_label = ttk.Label(self.server_frame, text = ":")
        self.server_port_entry = ttk.Entry(self.server_frame, width=8)
        self.auto_upload_label = ttk.Label(self.upload_frame, text="\tAuto-upload CombatLogs to the server:\t\t")
        self.auto_upload_var = tk.BooleanVar()
        self.auto_upload_false = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=False,
                                                 text="No")
        self.auto_upload_true = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=True,
                                                text="Yes")
        ### REAL-TIME SETTINGS ###
        # TODO Add more colours for the overlay
        # TODO Add events view possibility to the overlay
        self.realtime_settings_label = ttk.Label(self.realtime_frame, text = "Real-time parsing settings")
        self.overlay_enable_label = ttk.Label(self.realtime_frame, text = "\tEnable overlay for real-time parsing: ")
        self.overlay_enable_radio_var = tk.BooleanVar()
        self.overlay_enable_radio_yes = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_enable_radio_var,
                                                        value=True, text="Yes")
        self.overlay_enable_radio_no = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_enable_radio_var,
                                                       value=False, text="No")
        self.overlay_opacity_label = ttk.Label(self.realtime_frame, text = "\tOverlay opacity (between 0 and 1):")
        self.overlay_opacity_input = ttk.Entry(self.realtime_frame, width = 4)
        self.overlay_size_label = ttk.Label(self.realtime_frame, text = "\tOverlay window size: ")
        self.overlay_size_var = tk.StringVar()
        self.overlay_size_radio_big = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_size_var,
                                                      value = "big", text = "Big")
        self.overlay_size_radio_small = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_size_var,
                                                        value = "small", text = "Small")
        self.overlay_position_label = ttk.Label(self.realtime_frame, text = "\tPosition of the in-game overlay:")
        self.overlay_position_var = tk.StringVar()
        self.overlay_position_var.set(variables.set_obj.pos)
        self.overlay_position_radio_tl = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var,
                                                         value = "TL", text =  "Top left")
        self.overlay_position_radio_bl = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var,
                                                         value = "BL", text = "Bottom left")
        self.overlay_position_radio_tr = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var,
                                                         value = "TR", text = "Top right")
        self.overlay_position_radio_br = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var,
                                                         value = "BR", text = "Bottom right")
        self.overlay_color_options = ["white", "black", "yellow", "green", "blue", "red"]
        self.overlay_bg_color_radios = []
        self.overlay_bg_color = tk.StringVar()
        self.overlay_tx_color_radios = []
        self.overlay_tx_color = tk.StringVar()
        self.overlay_tr_color_radios = []
        self.overlay_tr_color = tk.StringVar()
        for color in self.overlay_color_options:
            self.overlay_bg_color_radios.append(ttk.Radiobutton(self.realtime_frame, variable = self.overlay_bg_color,
                                                                value = color, text = color))
            self.overlay_tx_color_radios.append(ttk.Radiobutton(self.realtime_frame, variable = self.overlay_tx_color,
                                                                value = color, text = color))
            self.overlay_tr_color_radios.append(ttk.Radiobutton(self.realtime_frame, variable = self.overlay_tr_color,
                                                                value = color, text = color))
        self.overlay_bg_label = ttk.Label(self.realtime_frame, text = "\tOverlay background colour: ")
        self.overlay_tx_label = ttk.Label(self.realtime_frame, text = "\tOverlay text colour: ")
        self.overlay_tr_label = ttk.Label(self.realtime_frame, text = "\tOverlay transparent colour: ")
        self.overlay_font_label = ttk.Label(self.realtime_frame, text = "\tOverlay font: ")
        self.overlay_font_options = ["Calibri", "Arial", "Consolas"]
        self.overlay_font_radios = []
        self.overlay_font = tk.StringVar()
        for font in self.overlay_font_options:
            self.overlay_font_radios.append(ttk.Radiobutton(self.realtime_frame, variable = self.overlay_font,
                                                            value = font, text = font))
        self.overlay_text_size_label = ttk.Label(self.realtime_frame, text = "\tOverlay text size: ")
        self.overlay_text_size_entry = ttk.Entry(self.realtime_frame, width = 5)
        self.overlay_when_gsf_label = ttk.Label(self.realtime_frame, text = "\tOnly display overlay in a GSF match: ")
        self.overlay_when_gsf = tk.BooleanVar()
        self.overlay_when_gsf_true = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_when_gsf,
                                                     text = "Yes", value = True)
        self.overlay_when_gsf_false = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_when_gsf,
                                                      text = "No", value = False)
        ### MISC ###
        self.separator = ttk.Separator(self.frame.interior, orient=tk.HORIZONTAL)
        self.save_settings_button = ttk.Button(self.save_frame, text="  Save  ", command=self.save_settings)
        self.discard_settings_button = ttk.Button(self.save_frame, text="Discard", command=self.discard_settings)
        self.default_settings_button = ttk.Button(self.save_frame, text="Defaults", command = self.default_settings)
        self.license_button = ttk.Button(self.license_frame, text="License", command=self.show_license)
        self.privacy_button = ttk.Button(self.license_frame, text = "Privacy statement for server", command=self.show_privacy)
        self.version_label = ttk.Label(self.license_frame, text="Version 2.0")
        self.update_label_var = tk.StringVar()
        self.update_label = ttk.Label(self.license_frame, textvariable=self.update_label_var)
        self.copyright_label = ttk.Label(self.license_frame, text = "Copyright (C) 2016 by RedFantom and Daethyra",
                                         justify=tk.LEFT)
        self.thanks_label = ttk.Label(self.license_frame, text = "Special thanks to Nightmaregale for bèta testing",
                                      justify=tk.LEFT)
        self.update_settings()

    def set_directory_dialog(self):
        directory = tkFileDialog.askdirectory(initialdir = self.path_var.get(), mustexist = True,
                                              parent = self.main_window, title = "GSF Parser: Choosing directory")
        if directory == "":
            return
        self.path_var.set(directory)

    def grid_widgets(self):
        ### GUI SETTINGS ###
        self.gui_label.grid(column = 0, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.gui_frame.grid(column = 0, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        self.color_label.grid(column = 0, row = 0, sticky=tk.N+tk.S+tk.W+tk.E)
        set_column = 0
        for radio in self.color_options:
            set_column += 1
            radio.grid(column=set_column, row=0,sticky=tk.N+tk.S+tk.W+tk.E)
        self.custom_color_entry.grid(column=set_column+1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.logo_color_label.grid(column=0, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        set_column = 0
        for radio in self.logo_color_options:
            set_column += 1
            radio.grid(column=set_column, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        ### PARSING SETTINGS ###
        self.parsing_label.grid(column=0, row=2, sticky=tk.W)
        self.path_entry_label.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E, padx =5)
        self.path_entry_button.grid(column = 2, row = 0, sticky = tk.N+tk.S+tk.W+tk.E, padx = 3)
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
        self.overlay_size_label.grid(column = 0, row = 3, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_size_radio_big.grid(column = 1, row = 3, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_size_radio_small.grid(column = 2, row = 3, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_position_label.grid(column = 0, row = 4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_position_radio_tl.grid(column = 1, row = 4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_position_radio_bl.grid(column = 2, row = 4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_position_radio_tr.grid(column = 3, row = 4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_position_radio_br.grid(column = 4, row = 4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.realtime_frame.grid(column = 0, row = 8, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_tx_label.grid(column=0, row = 5, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_bg_label.grid(column = 0, row = 6, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_tr_label.grid(column=0,row=7, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_font_label.grid(column=0,row=8, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_text_size_label.grid(column = 0, row = 9, sticky=tk.N+tk.S+tk.W+tk.E)
        self.overlay_text_size_entry.grid(column = 1, row = 9, sticky=tk.N+tk.S+tk.W+tk.E)
        set_column = 1
        for radio in self.overlay_tx_color_radios:
            radio.grid(column = set_column, row = 5,sticky=tk.N+tk.S+tk.W+tk.E)
            set_column += 1
        set_column = 1
        for radio in self.overlay_bg_color_radios:
            radio.grid(column = set_column, row = 6,sticky=tk.N+tk.S+tk.W+tk.E)
            set_column += 1
        set_column = 1
        for radio in self.overlay_tr_color_radios:
            radio.grid(column = set_column, row = 7,sticky=tk.N+tk.S+tk.W+tk.E)
            set_column += 1
        set_column = 1
        for radio in self.overlay_font_radios:
            radio.grid(column = set_column, row = 8, sticky=tk.N+tk.S+tk.W+tk.E)
            set_column += 1
        self.overlay_when_gsf_label.grid(column = 0, row = 10)
        self.overlay_when_gsf_true.grid(column = 1, row = 10)
        self.overlay_when_gsf_false.grid(column = 2, row = 10)
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
        ### FINAL FRAME ###
        self.frame.grid(sticky=tk.N+tk.S+tk.W+tk.E)
        self.grid(column=0,row=0,sticky=tk.N+tk.S+tk.W+tk.E)

    def update_settings(self):
        self.path_var.set(variables.set_obj.cl_path)
        self.privacy_var.set(bool(variables.set_obj.auto_ident))
        self.server_address_entry.delete(0, tk.END)
        self.server_address_entry.insert(0, str(variables.set_obj.server_address))
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, int(variables.set_obj.server_port))
        self.auto_upload_var.set(bool(variables.set_obj.auto_upl))
        self.overlay_enable_radio_var.set(bool(variables.set_obj.overlay))
        self.overlay_opacity_input.delete(0, tk.END)
        self.overlay_opacity_input.insert(0, variables.set_obj.opacity)
        self.overlay_size_var.set(variables.set_obj.size)
        self.overlay_position_var.set(variables.set_obj.pos)
        self.logo_color.set(variables.set_obj.logo_color)
        self.color.set(variables.set_obj.color)
        self.overlay_bg_color.set(variables.set_obj.overlay_bg_color)
        self.overlay_tx_color.set(variables.set_obj.overlay_tx_color)
        self.overlay_tr_color.set(variables.set_obj.overlay_tr_color)
        self.overlay_font.set(variables.set_obj.overlay_tx_font)
        self.overlay_text_size_entry.delete(0, tk.END)
        self.overlay_text_size_entry.insert(0, variables.set_obj.overlay_tx_size)
        self.overlay_when_gsf.set(variables.set_obj.overlay_when_gsf)

    def save_settings(self):
        print "[DEBUG] Save_settings called!"
        if str(self.color.get()) == variables.set_obj.color and self.logo_color.get() == variables.set_obj.logo_color:
            reboot = False
        else:
            reboot = True
        print self.color.get()
        if "custom" in self.color.get():
            hex_color = re.search(r"^#(?:[0-9a-fA-F]{1,2}){3}$", self.custom_color_entry.get())
            print hex_color
            if not hex_color:
                tkMessageBox.showerror("Error", "The custom color you entered is not valid. It must be a hex color code.")
                return
            color = self.custom_color_entry.get()
        else:
            color = self.color.get()
        if self.overlay_when_gsf.get() and not variables.set_obj.overlay_when_gsf:
            help_string = """This setting makes the overlay only appear inside GSF matches. Please note that the overlay will only appear after the
                             first GSF ability is executed, so the overlay may appear to display a little late, but this is normal behaviour."""
            tkMessageBox.showinfo("Notice", help_string.replace("\n", "").replace("  ", ""))
        variables.set_obj.write_set(cl_path=str(self.path_var.get()), auto_ident=str(self.privacy_var.get()),
                                    server_address=str(self.server_address_entry.get()), server_port=str(self.server_port_entry.get()),
                                    auto_upl=str(self.auto_upload_var.get()), overlay=str(self.overlay_enable_radio_var.get()),
                                    opacity=str(self.overlay_opacity_input.get()), size=str(self.overlay_size_var.get()),
                                    pos=str(self.overlay_position_var.get()), color=color, logo_color=self.logo_color.get(),
                                    bg_color=self.overlay_bg_color.get(), tr_color=self.overlay_tr_color.get(),
                                    tx_color=self.overlay_tx_color.get(), tx_font=self.overlay_font.get(),
                                    tx_size=self.overlay_text_size_entry.get(), overlay_when_gsf=self.overlay_when_gsf.get())
        self.update_settings()
        self.main_window.file_select_frame.add_files()
        if reboot:
            self.main_window.update_style()

    def discard_settings(self):
        self.update_settings()

    def default_settings(self):
        variables.set_obj.write_def()
        self.update_settings()

    @staticmethod
    def show_license():
        tkMessageBox.showinfo("License", "This program is licensed under the General Public License Version 3, by GNU. See LICENSE in the installation directory for more details")

    def show_privacy(self):
        if not variables.client_obj.INIT:
            tkMessageBox.showerror("Error","The connection to the server was not initialized correctly.")
            return
        toplevels.privacy(self.main_window)
