# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.filedialog
import re
import variables
from widgets import VerticalScrollFrame
from toplevels.colors import EventColors
from toplevels.privacy import Privacy


class SettingsFrame(ttk.Frame):
    """
    A rather complicated Frame with lots of widgets containing the widgets for
    all user-changable settings of the parser. The instance calls on functions
    of a settings.settings instance to write the settings to the file and read
    the settings from the file. The settings.settings instance used is created
    in the variables.py file.
    """

    def __init__(self, root_frame, main_window):
        # LAY-OUT
        ttk.Frame.__init__(self, root_frame)
        self.frame = VerticalScrollFrame(self, canvasheight=295, canvaswidth=780)
        self.gui_frame = ttk.Frame(self.frame.interior)
        self.entry_frame = ttk.Frame(self.frame.interior)
        self.privacy_frame = ttk.Frame(self.frame.interior)
        self.server_frame = ttk.Frame(self.frame.interior)
        self.upload_frame = ttk.Frame(self.frame.interior)
        self.realtime_frame = ttk.Frame(self.frame.interior)
        self.bottom_frame = ttk.Frame(self)
        self.save_frame = ttk.Frame(self.bottom_frame)
        self.license_frame = ttk.Frame(self.bottom_frame)
        self.top_frame = self.frame
        self.main_window = main_window
        # GUI SETTINGS
        # TODO Add more GUI settings including colors
        self.gui_label = ttk.Label(self.frame.interior, text="GUI settings", justify=tk.LEFT,
                                   font=("Calibri", 12))
        self.color_label = ttk.Label(self.gui_frame, text="\tParser text color: ")
        self.color = tk.StringVar()
        self.custom_color_entry = ttk.Entry(self.gui_frame, width=10)
        self.color_options = []
        self.color_choices = ["Darkgreen", "Darkblue", "Darkred", "Black", "Custom: "]
        self.color_options.append(
            ttk.Radiobutton(self.gui_frame, value="#236ab2", text="Default", variable=self.color,
                            width=8))
        for color in self.color_choices:
            self.color_options.append(ttk.Radiobutton(self.gui_frame, value=str(color).lower(), text=color,
                                                      variable=self.color, width=8))
        self.color.set(variables.settings_obj.color)
        self.logo_color_label = ttk.Label(self.gui_frame, text="\tParser logo color: ")
        self.logo_color = tk.StringVar()
        self.logo_color_choices = ["Green", "Blue", "Red"]
        self.logo_color_options = []
        self.logo_color.set(variables.settings_obj.logo_color)
        for color in self.logo_color_choices:
            self.logo_color_options.append(ttk.Radiobutton(self.gui_frame, value=str(color).lower(), text=color,
                                                           variable=self.logo_color, width=10))
        self.event_colors_label = ttk.Label(self.gui_frame, text="\tEvent colors: ")
        self.event_colors = tk.StringVar()
        self.event_colors_none = ttk.Radiobutton(self.gui_frame, text="None", variable=self.event_colors,
                                                 value="none")
        self.event_colors_basic = ttk.Radiobutton(self.gui_frame, text="Basic", variable=self.event_colors,
                                                  value="basic")
        self.event_colors_adv = ttk.Radiobutton(self.gui_frame, text="Advanced", variable=self.event_colors,
                                                value="advanced")

        self.event_scheme = tk.StringVar()
        self.event_scheme_label = ttk.Label(self.gui_frame, text="\tEvent color scheme: ")
        self.event_scheme_default = ttk.Radiobutton(self.gui_frame, text="Default", variable=self.event_scheme,
                                                    value="default")
        self.event_scheme_pastel = ttk.Radiobutton(self.gui_frame, text="Pastel", variable=self.event_scheme,
                                                   value="pastel")
        self.event_scheme_custom = ttk.Radiobutton(self.gui_frame, text="Custom", variable=self.event_scheme,
                                                   value="custom")
        self.event_scheme_custom_button = ttk.Button(self.gui_frame, text="Choose colors",
                                                     command=self.set_custom_event_colors)
        self.date_format_label = ttk.Label(self.gui_frame, text="\tDate format: ")
        self.date_format = tk.StringVar()
        self.date_format_ymd = ttk.Radiobutton(self.gui_frame, text="YYYY-MM-DD", value="ymd",
                                               variable=self.date_format)
        self.date_format_ydm = ttk.Radiobutton(self.gui_frame, text="YYYY-DD-MM", value="ydm",
                                               variable=self.date_format)
        self.faction_label = ttk.Label(self.gui_frame, text="\tFaction: ")
        self.faction = tk.StringVar()
        self.faction_choices = ["Imperial", "Republic"]
        self.faction_options = []
        self.faction.set(variables.settings_obj.faction)
        for faction in self.faction_choices:
            self.faction_options.append(ttk.Radiobutton(self.gui_frame, value=str(faction).lower(), text=faction,
                                                        variable=self.faction, width=8))

        # PARSING SETTINGS
        self.parsing_label = ttk.Label(self.frame.interior, text="Parsing settings", justify=tk.LEFT,
                                       font=("Calibri", 12))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.entry_frame, width=80, textvariable=self.path_var)
        self.path_entry_button = ttk.Button(self.entry_frame, text="Browse", command=self.set_directory_dialog)
        self.path_entry_label = ttk.Label(self.entry_frame, text="\tCombatLogs folder: ")
        self.privacy_label = ttk.Label(self.privacy_frame,
                                       text="\tConnect to server for player identification: ")
        self.privacy_var = tk.BooleanVar()
        self.privacy_select_true = ttk.Radiobutton(self.privacy_frame, variable=self.privacy_var, value=True,
                                                   text="Yes")
        self.privacy_select_false = ttk.Radiobutton(self.privacy_frame, variable=self.privacy_var, value=False,
                                                    text="No")
        # SHARING SETTINGS
        self.sharing_label = ttk.Label(self.frame.interior, text="Share settings", justify=tk.LEFT,
                                       font=("Calibri", 12))
        self.server_label = ttk.Label(self.server_frame, text="\tServer for sharing: ")
        self.server_address_entry = ttk.Entry(self.server_frame, width=35)
        self.server_colon_label = ttk.Label(self.server_frame, text=":")
        self.server_port_entry = ttk.Entry(self.server_frame, width=8)
        self.auto_upload_label = ttk.Label(self.upload_frame, text="\tAuto-upload CombatLogs to the server:\t\t")
        self.auto_upload_var = tk.BooleanVar()
        self.auto_upload_false = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=False,
                                                 text="No")
        self.auto_upload_true = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=True,
                                                text="Yes")
        # REAL-TIME SETTINGS
        # TODO Add more colors for the overlay
        # TODO Add events view possibility to the overlay
        self.realtime_settings_label = ttk.Label(self.realtime_frame, text="Real-time parsing settings",
                                                 font=("Calibri", 12))
        self.overlay_enable_label = ttk.Label(self.realtime_frame,
                                              text="\tEnable overlay for real-time parsing: ")
        self.overlay_enable_radio_var = tk.BooleanVar()
        self.overlay_enable_radio_yes = ttk.Radiobutton(self.realtime_frame,
                                                        variable=self.overlay_enable_radio_var,
                                                        value=True, text="Yes")
        self.overlay_enable_radio_no = ttk.Radiobutton(self.realtime_frame,
                                                       variable=self.overlay_enable_radio_var,
                                                       value=False, text="No")
        self.overlay_opacity_label = ttk.Label(self.realtime_frame, text="\tOverlay opacity (between 0 and 1):")
        self.overlay_opacity_input = ttk.Entry(self.realtime_frame, width=4)
        self.overlay_size_label = ttk.Label(self.realtime_frame, text="\tOverlay window size: ")
        self.overlay_size_var = tk.StringVar()
        self.overlay_size_radio_big = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_size_var,
                                                      value="big", text="Big")
        self.overlay_size_radio_small = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_size_var,
                                                        value="small", text="Small")
        self.overlay_position_label = ttk.Label(self.realtime_frame, text="\tPosition of the in-game overlay:")
        self.overlay_position_var = tk.StringVar()
        self.overlay_position_var.set(variables.settings_obj.pos)
        self.overlay_position_radio_tl = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="TL", text="Top left")
        self.overlay_position_radio_bl = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="BL", text="Bottom left")
        self.overlay_position_radio_tr = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="TR", text="Top right")
        self.overlay_position_radio_br = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="BR", text="Bottom right")
        self.overlay_position_radio_ut = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="UT", text="Under targeting computer")
        self.overlay_position_radio_uc = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="UC", text="Under chat box")
        self.overlay_position_radio_nq = ttk.Radiobutton(self.realtime_frame,
                                                         variable=self.overlay_position_var,
                                                         value="NQ", text="Left from quickbar")
        self.overlay_color_options = ["White", "Yellow", "Green", "Blue", "Red"]
        self.overlay_bg_color_radios = []
        self.overlay_bg_color = tk.StringVar()
        self.overlay_tx_color_radios = []
        self.overlay_tx_color = tk.StringVar()
        self.overlay_tr_color_radios = []
        self.overlay_tr_color = tk.StringVar()
        for color in self.overlay_color_options:
            self.overlay_bg_color_radios.append(
                ttk.Radiobutton(self.realtime_frame, variable=self.overlay_bg_color,
                                value=color.lower(), text=color, width=6))
            self.overlay_tx_color_radios.append(
                ttk.Radiobutton(self.realtime_frame, variable=self.overlay_tx_color,
                                value=color.lower(), text=color, width=6))
            self.overlay_tr_color_radios.append(
                ttk.Radiobutton(self.realtime_frame, variable=self.overlay_tr_color,
                                value=color.lower(), text=color, width=6))
        self.overlay_bg_label = ttk.Label(self.realtime_frame, text="\tOverlay background color: ")
        self.overlay_tx_label = ttk.Label(self.realtime_frame, text="\tOverlay text color: ")
        self.overlay_tr_label = ttk.Label(self.realtime_frame, text="\tOverlay transparent color: ")
        self.overlay_font_label = ttk.Label(self.realtime_frame, text="\tOverlay font: ")
        self.overlay_font_options = ["Calibri", "Arial", "Consolas"]
        self.overlay_font_radios = []
        self.overlay_font = tk.StringVar()
        for font in self.overlay_font_options:
            self.overlay_font_radios.append(ttk.Radiobutton(self.realtime_frame, variable=self.overlay_font,
                                                            value=font, text=font))
        self.overlay_text_size_label = ttk.Label(self.realtime_frame, text="\tOverlay text size: ")
        self.overlay_text_size_entry = ttk.Entry(self.realtime_frame, width=5)
        self.overlay_when_gsf_label = ttk.Label(self.realtime_frame,
                                                text="\tOnly display overlay in a GSF match: ")
        self.overlay_when_gsf = tk.BooleanVar()
        self.overlay_when_gsf_true = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_when_gsf,
                                                     text="Yes", value=True)
        self.overlay_when_gsf_false = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_when_gsf,
                                                      text="No", value=False)
        self.realtime_timeout_label = ttk.Label(self.realtime_frame, text="\tRealtime parsing timeout: ")
        self.realtime_timeout = tk.StringVar()
        self.realtime_timeout_entry = ttk.Entry(self.realtime_frame, textvariable=self.realtime_timeout, width=10)
        self.realtime_timeout_help_button = ttk.Button(self.realtime_frame, text="Help",
                                                       command=self.show_timeout_help)
        self.realtime_timeout_help_label = ttk.Label(self.realtime_frame, text="Only change this if you are "
                                                                               "experiencing performance issues!")
        self.realtime_event_overlay_label = ttk.Label(self.realtime_frame, text="\tShow events overlay: ")
        self.realtime_event_overlay_var = tk.BooleanVar()
        self.realtime_event_overlay_true = ttk.Radiobutton(self.realtime_frame, text="Yes",
                                                           variable=self.realtime_event_overlay_var, value=True)
        self.realtime_event_overlay_false = ttk.Radiobutton(self.realtime_frame, text="No",
                                                            variable=self.realtime_event_overlay_var, value=False)
        self.screenparsing_label = ttk.Label(self.realtime_frame, text="\tEnable screen parsing: ")
        self.screenparsing_var = tk.BooleanVar()
        self.screenparsing_true = ttk.Radiobutton(self.realtime_frame, text="Yes", variable=self.screenparsing_var,
                                                  value=True)
        self.screenparsing_false = ttk.Radiobutton(self.realtime_frame, text="No", variable=self.screenparsing_var,
                                                   value=False)
        self.screenparsing_overlay_label = ttk.Label(self.realtime_frame, text="\tShow overlay for screen parsing: ")
        self.screenparsing_overlay_var = tk.BooleanVar()
        self.screenparsing_overlay_true = ttk.Radiobutton(self.realtime_frame, text="Yes",
                                                          variable=self.screenparsing_overlay_var, value=True)
        self.screenparsing_overlay_false = ttk.Radiobutton(self.realtime_frame, text="No",
                                                           variable=self.screenparsing_overlay_var, value=False)
        # MISC
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.save_settings_button = ttk.Button(self.save_frame, text="  Save  ", command=self.save_settings)
        self.discard_settings_button = ttk.Button(self.save_frame, text="Discard", command=self.discard_settings)
        self.default_settings_button = ttk.Button(self.save_frame, text="Defaults", command=self.default_settings)
        self.license_button = ttk.Button(self.license_frame, text="License", command=self.show_license)
        self.privacy_button = ttk.Button(self.license_frame, text="Privacy statement for server",
                                         command=self.show_privacy)
        self.version_label = ttk.Label(self.license_frame, text="Version 2.0")
        self.update_label_var = tk.StringVar()
        self.update_label = ttk.Label(self.license_frame, textvariable=self.update_label_var)
        self.copyright_label = ttk.Label(self.license_frame,
                                         text="Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania",
                                         justify=tk.LEFT)
        self.thanks_label = ttk.Label(self.license_frame,
                                      text="Special thanks to Nightmaregale for bèta testing",
                                      justify=tk.LEFT)
        self.update_settings()

    @staticmethod
    def show_timeout_help():
        tkinter.messagebox.showinfo("Help", "This is the setting for the sleep timeout for realtime parsing. "
                                            "Lowering this value will allow faster detection of change, but "
                                            "it will also require more processing power and IO usage. Increasing "
                                            "this value will reduce processing power requirements and IO usage. "
                                            "Please do not change this value unless you are experiencing performance "
                                            "issues that you can relate to the usage of the GSF Parser on a low-end "
                                            "system.")

    def set_custom_event_colors(self):
        """
        Opens a Toplevel to show the settings for the colors of the events
        view. See toplevel.event_colors for more information.
        :return: None
        """
        self.color_toplevel = EventColors(variables.main_window)
        self.color_toplevel.grid_widgets()
        self.color_toplevel.focus_set()

    def set_directory_dialog(self):
        """
        Open a tkFileDialog to ask the user for the directory of the CombatLogs
        so the user does not have to enter the full path manually.
        :return: None
        """
        directory = tkinter.filedialog.askdirectory(initialdir=self.path_var.get(), mustexist=True,
                                                    parent=self.main_window, title="GSF Parser: Choosing directory")
        if directory == "":
            return
        self.path_var.set(directory)

    def grid_widgets(self):
        """
        Put all the widgets created in the __init__ function in their respective
        places.
        :return: None
        """
        # GUI SETTINGS
        self.gui_label.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E, pady=5)
        self.gui_frame.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        # self.color_label.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        set_column = 0
        # for radio in self.color_options:
        #     set_column += 1
        #     radio.grid(column=set_column, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        # self.custom_color_entry.grid(column=set_column + 1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.logo_color_label.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        set_column = 0
        for radio in self.logo_color_options:
            set_column += 1
            radio.grid(column=set_column, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_colors_label.grid(column=0, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_colors_basic.grid(column=2, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_colors_none.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_colors_adv.grid(column=3, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_scheme_label.grid(column=0, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_scheme_default.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_scheme_pastel.grid(column=2, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_scheme_custom.grid(column=3, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.event_scheme_custom_button.grid(column=4, row=3, sticky=tk.N + tk.S + tk.W + tk.E,
                                             padx=5)
        self.date_format_label.grid(column=0, row=4, sticky=tk.W)
        self.date_format_ymd.grid(column=1, row=4, sticky=tk.W)
        self.date_format_ydm.grid(column=2, row=4, sticky=tk.W)
        self.faction_label.grid(column=0, row=5, sticky=tk.N + tk.S + tk.W + tk.E)
        set_column = 0
        for radio in self.faction_options:
            set_column += 1
            radio.grid(column=set_column, row=5, sticky=tk.N + tk.S + tk.W + tk.E)
        # PARSING SETTINGS
        self.parsing_label.grid(column=0, row=2, sticky=tk.W, pady=5)
        self.path_entry_label.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)
        self.path_entry_button.grid(column=2, row=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=3)
        self.path_entry.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.entry_frame.grid(column=0, row=3, sticky=tk.N + tk.S + tk.W)
        # self.privacy_label.grid(column=0, row=0, sticky=tk.W)
        # self.privacy_select_true.grid(column=1, row=0, sticky=tk.W)
        # self.privacy_select_false.grid(column=2, row=0, sticky=tk.W)
        # self.privacy_frame.grid(column=0, row=4, sticky=tk.N + tk.S + tk.W + tk.E)
        # SHARING SETTINGS
        # self.sharing_label.grid(column=0, row=5, sticky=tk.W, pady=5)
        # self.server_label.grid(column=0, row=0, sticky=tk.W)
        # self.server_address_entry.grid(column=1, row=0)
        # self.server_colon_label.grid(column=2, row=0)
        # self.server_port_entry.grid(column=3, row=0)
        # self.server_frame.grid(column=0, row=6, sticky=tk.N + tk.S + tk.W + tk.E)
        # self.auto_upload_label.grid(column=0, row=0)
        # self.auto_upload_true.grid(column=1, row=0)
        # self.auto_upload_false.grid(column=2, row=0)
        # self.upload_frame.grid(column=0, row=7, sticky=tk.N + tk.S + tk.W + tk.E)
        # REALTIME SETTINGS
        self.overlay_enable_label.grid(column=0, row=1, sticky=tk.W)
        self.overlay_enable_radio_yes.grid(column=1, row=1, sticky=tk.W)
        self.overlay_enable_radio_no.grid(column=2, row=1, sticky=tk.W)
        self.overlay_opacity_label.grid(column=0, row=2, sticky=tk.W)
        self.overlay_opacity_input.grid(column=1, row=2, sticky=tk.W)
        self.realtime_settings_label.grid(column=0, row=0, sticky=tk.W, pady=5)
        self.overlay_size_label.grid(column=0, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_size_radio_big.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_size_radio_small.grid(column=2, row=3, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_position_label.grid(column=0, row=4, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_position_radio_tl.grid(column=1, row=4, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_position_radio_bl.grid(column=2, row=4, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_position_radio_tr.grid(column=3, row=4, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_position_radio_br.grid(column=4, row=4, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_position_radio_ut.grid(column=1, row=5, sticky=tk.N + tk.S + tk.W + tk.E, columnspan=2)
        self.overlay_position_radio_uc.grid(column=5, row=4, sticky=tk.N + tk.S + tk.W)
        self.overlay_position_radio_nq.grid(column=4, row=5, sticky=tk.N + tk.S + tk.W, columnspan=2)
        self.realtime_frame.grid(column=0, row=8, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_tx_label.grid(column=0, row=6, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_bg_label.grid(column=0, row=7, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_tr_label.grid(column=0, row=8, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_font_label.grid(column=0, row=9, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_text_size_label.grid(column=0, row=10, sticky=tk.N + tk.S + tk.W + tk.E)
        self.overlay_text_size_entry.grid(column=1, row=10, sticky=tk.N + tk.S + tk.W + tk.E)
        set_column = 1
        for radio in self.overlay_tx_color_radios:
            radio.grid(column=set_column, row=6, sticky=tk.N + tk.S + tk.W + tk.E)
            set_column += 1
        set_column = 1
        for radio in self.overlay_bg_color_radios:
            radio.grid(column=set_column, row=7, sticky=tk.N + tk.S + tk.W + tk.E)
            set_column += 1
        set_column = 1
        for radio in self.overlay_tr_color_radios:
            radio.grid(column=set_column, row=8, sticky=tk.N + tk.S + tk.W + tk.E)
            set_column += 1
        set_column = 1
        for radio in self.overlay_font_radios:
            radio.grid(column=set_column, row=9, sticky=tk.N + tk.S + tk.W + tk.E)
            set_column += 1
        self.overlay_when_gsf_label.grid(column=0, row=11)
        self.overlay_when_gsf_true.grid(column=1, row=11, sticky=tk.W)
        self.overlay_when_gsf_false.grid(column=2, row=11, sticky=tk.W)
        self.realtime_timeout_label.grid(column=0, row=12, sticky=tk.W)
        self.realtime_timeout_entry.grid(column=1, row=12, sticky=tk.W)
        self.realtime_timeout_help_button.grid(column=2, row=12, sticky=tk.W)
        self.realtime_timeout_help_label.grid(column=3, row=12, sticky=tk.W, columnspan=5,
                                              padx=5)
        self.realtime_event_overlay_label.grid(column=0, row=13, sticky=tk.W)
        self.realtime_event_overlay_true.grid(column=1, row=13, sticky=tk.W)
        self.realtime_event_overlay_false.grid(column=2, row=13, sticky=tk.W)
        self.screenparsing_label.grid(column=0, row=14, sticky=tk.W)
        self.screenparsing_true.grid(column=1, row=14, sticky=tk.W)
        self.screenparsing_false.grid(column=2, row=14, sticky=tk.W)
        self.screenparsing_overlay_label.grid(column=0, row=15, sticky=tk.W)
        self.screenparsing_overlay_true.grid(column=1, row=15, sticky=tk.W)
        self.screenparsing_overlay_false.grid(column=2, row=15, sticky=tk.W)
        # MISC
        self.save_settings_button.grid(column=0, row=1, padx=2)
        self.discard_settings_button.grid(column=1, row=1, padx=2)
        self.default_settings_button.grid(column=2, row=1, padx=2)
        self.save_frame.grid(column=0, row=1, sticky=tk.W)
        self.license_button.grid(column=1, row=2, sticky=tk.W, padx=5)
        # self.privacy_button.grid(column=2, row=2, sticky=tk.W, padx=5)
        self.copyright_label.grid(column=0, row=2, sticky=tk.W)
        self.update_label.grid(column=0, row=2, sticky=tk.W)
        self.thanks_label.grid(column=0, row=3, sticky=tk.W)
        self.separator.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E, pady=10)
        self.license_frame.grid(column=0, row=2, sticky=tk.N + tk.S + tk.W + tk.E, pady=5)
        self.save_frame.grid(column=0, row=0)
        # FINAL FRAME
        self.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.top_frame.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W)
        self.separator.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E, pady=10)
        self.bottom_frame.grid(column=0, row=2, sticky=tk.N + tk.S + tk.W)

    def update_settings(self):
        """
        Read the settings from the settigns_obj in the variables
        module and update the settings shown in the GUI accordingly.
        :return: None
        """
        self.path_var.set(variables.settings_obj.cl_path)
        self.privacy_var.set(bool(variables.settings_obj.auto_ident))
        self.server_address_entry.delete(0, tk.END)
        self.server_address_entry.insert(0, str(variables.settings_obj.server_address))
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, int(variables.settings_obj.server_port))
        self.auto_upload_var.set(bool(variables.settings_obj.auto_upl))
        self.overlay_enable_radio_var.set(bool(variables.settings_obj.overlay))
        self.overlay_opacity_input.delete(0, tk.END)
        self.overlay_opacity_input.insert(0, variables.settings_obj.opacity)
        self.overlay_size_var.set(variables.settings_obj.size)
        self.overlay_position_var.set(variables.settings_obj.pos)
        self.logo_color.set(variables.settings_obj.logo_color)
        self.color.set(variables.settings_obj.color)
        self.overlay_bg_color.set(variables.settings_obj.overlay_bg_color)
        self.overlay_tx_color.set(variables.settings_obj.overlay_tx_color)
        self.overlay_tr_color.set(variables.settings_obj.overlay_tr_color)
        self.overlay_font.set(variables.settings_obj.overlay_tx_font)
        self.overlay_text_size_entry.delete(0, tk.END)
        self.overlay_text_size_entry.insert(0, variables.settings_obj.overlay_tx_size)
        self.overlay_when_gsf.set(variables.settings_obj.overlay_when_gsf)
        self.event_colors.set(variables.settings_obj.event_colors)
        self.event_scheme.set(variables.settings_obj.event_scheme)
        variables.color_scheme.set_scheme(variables.settings_obj.event_scheme)
        self.date_format.set(variables.settings_obj.date_format)
        self.realtime_timeout.set(variables.settings_obj.timeout)
        self.faction.set(variables.settings_obj.faction)
        self.realtime_event_overlay_var.set(variables.settings_obj.events_overlay)
        self.screenparsing_var.set(variables.settings_obj.screenparsing)
        self.screenparsing_overlay_var.set(variables.settings_obj.screenparsing_overlay)

    def save_settings(self):
        """
        Save the settings found in the widgets of the settings to the
        settings_obj in the variables module
        Some settings are checked before the writing occurs
        :return: None
        """
        print("[DEBUG] Save_settings called!")
        if str(
                self.color.get()) == variables.settings_obj.color and self.logo_color.get() == variables.settings_obj.logo_color:
            reboot = False
        else:
            reboot = True
        print(self.color.get())
        if "custom" in self.color.get():
            hex_color = re.search(r"^#(?:[0-9a-fA-F]{1,2}){3}$", self.custom_color_entry.get())
            print(hex_color)
            if not hex_color:
                tkinter.messagebox.showerror("Error",
                                             "The custom color you entered is not valid. It must be a hex color code.")
                return
            color = self.custom_color_entry.get()
        else:
            color = self.color.get()
        if self.overlay_when_gsf.get() and not variables.settings_obj.overlay_when_gsf:
            help_string = ("""This setting makes the overlay only appear inside GSF matches. Please note that the """
                           """overlay will only appear after the first GSF ability is executed, so the overlay """
                           """may appear to display a little late, but this is normal behaviour.""")
            tkinter.messagebox.showinfo("Notice", help_string.replace("\n", "").replace("  ", ""))
        variables.settings_obj.write_set(cl_path=str(self.path_var.get()),
                                         auto_ident=str(self.privacy_var.get()),
                                         server_address=str(self.server_address_entry.get()),
                                         server_port=str(self.server_port_entry.get()),
                                         auto_upl=str(self.auto_upload_var),
                                         overlay=str(self.overlay_enable_radio_var.get()),
                                         opacity=str(self.overlay_opacity_input.get()),
                                         size=str(self.overlay_size_var.get()),
                                         pos=str(self.overlay_position_var.get()),
                                         color=color,
                                         logo_color=self.logo_color.get(),
                                         bg_color=self.overlay_bg_color.get(),
                                         tr_color=self.overlay_tr_color.get(),
                                         tx_color=self.overlay_tx_color.get(),
                                         tx_font=self.overlay_font.get(),
                                         tx_size=self.overlay_text_size_entry.get(),
                                         overlay_when_gsf=self.overlay_when_gsf.get(),
                                         timeout=self.realtime_timeout.get(),
                                         event_colors=self.event_colors.get(),
                                         event_scheme=self.event_scheme.get(),
                                         date_format=self.date_format.get(),
                                         faction=self.faction.get(),
                                         events_overlay=self.realtime_event_overlay_var.get(),
                                         screenparsing=self.screenparsing_var.get(),
                                         screenparsing_overlay=self.screenparsing_overlay_var.get())
        self.update_settings()
        self.main_window.file_select_frame.add_files()
        if reboot:
            self.main_window.update_style()
        variables.color_scheme.set_scheme(self.event_scheme.get())

    def discard_settings(self):
        """
        Discard the changes to the settings by reloading the settings
        from the settings_obj
        :return: None
        """
        self.update_settings()

    def default_settings(self):
        """
        Write the default settings to the settings_obj found in the
        settings.defaults class and then update the settings shown
        :return: None
        """
        variables.settings_obj.write_def()
        self.update_settings()

    @staticmethod
    def show_license():
        """
        Show that this software is available under GNU GPLv3
        :return: None
        """
        tkinter.messagebox.showinfo("License",
                                    "This program is licensed under the General Public License Version 3, by GNU. See "
                                    "LICENSE in the installation directory for more details")

    def show_privacy(self):
        """
        A function that is not actually working yet, as the GSF-Server is
        not yet available, but this will show the privacy statement of the
        selected GSF-Server in a Toplevel
        :return: None
        """
        if not variables.client_obj.INIT:
            tkinter.messagebox.showerror("Error", "The connection to the server was not initialized correctly.")
            return
        Privacy(self.main_window)
