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
from collections import OrderedDict


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
        self.custom_color_entry = ttk.Entry(self.gui_frame, width=15)
        self.color_choices = {
            "Darkgreen": "Darkgreen",
            "Darkblue": "Darkblue",
            "Darkred": "Darkred",
            "Black": "Black",
            "Custom": "Custom: ",
            "Default": "#236ab2"
        }
        self.color_choices_tuple = ("Default", "Default", "Custom", "Darkblue", "Darkgreen", "Darkred", "Black")
        self.color_dropdown = ttk.OptionMenu(self.gui_frame, self.color, *self.color_choices_tuple)
        self.color.set(variables.settings_obj["gui"]["color"])
        self.logo_color_label = ttk.Label(self.gui_frame, text="\tParser logo color: ")
        self.logo_color = tk.StringVar()
        self.logo_color.set(variables.settings_obj["gui"]["logo_color"])
        self.logo_color_dropdown = ttk.OptionMenu(self.gui_frame, self.logo_color, *("Default", "Green", "Blue", "Red"))

        self.event_colors_label = ttk.Label(self.gui_frame, text="\tEvent colors: ")
        self.event_colors = tk.StringVar()
        self.event_colors_none = ttk.Radiobutton(self.gui_frame, text="None", variable=self.event_colors,
                                                 value="none", width=15)
        self.event_colors_basic = ttk.Radiobutton(self.gui_frame, text="Basic", variable=self.event_colors,
                                                  value="basic", width=15)
        self.event_colors_adv = ttk.Radiobutton(self.gui_frame, text="Advanced", variable=self.event_colors,
                                                value="advanced", width=15)

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
        self.faction.set(variables.settings_obj["gui"]["faction"])
        for faction in self.faction_choices:
            self.faction_options.append(ttk.Radiobutton(self.gui_frame, value=str(faction).lower(), text=faction,
                                                        variable=self.faction, width=8))
        self.auto_update = tk.BooleanVar()
        self.auto_update_checkbox = ttk.Checkbutton(self.gui_frame, variable=self.auto_update,
                                                    text="Automatically check for updates on startup")

        self.debug_window = tk.BooleanVar()
        self.debug_window_checkbox = ttk.Checkbutton(self.gui_frame, text="Show window with debug output",
                                                     variable=self.debug_window)

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
        self.realtime_settings_label = ttk.Label(self.realtime_frame, text="Real-time parsing settings",
                                                 font=("Calibri", 12))
        self.overlay_enable_label = ttk.Label(self.realtime_frame,
                                              text="\tEnable overlay for real-time parsing: ")
        self.overlay_enable_radio_var = tk.BooleanVar()
        self.overlay_enable_radio_yes = ttk.Radiobutton(self.realtime_frame,
                                                        variable=self.overlay_enable_radio_var,
                                                        value=True, text="Yes", width=10)
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
        self.overlay_position_var.set(variables.settings_obj["realtime"]["pos"])
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
        self.overlay_color_options = ("Default", "White", "Yellow", "Green", "Blue", "Red")
        self.overlay_bg_color = tk.StringVar()
        self.overlay_tx_color = tk.StringVar()
        self.overlay_tr_color = tk.StringVar()

        self.overlay_bg_dropdown = ttk.OptionMenu(self.realtime_frame, self.overlay_bg_color,
                                                  *self.overlay_color_options)
        self.overlay_tx_dropdown = ttk.OptionMenu(self.realtime_frame, self.overlay_tx_color,
                                                  *self.overlay_color_options)
        self.overlay_tr_dropdown = ttk.OptionMenu(self.realtime_frame, self.overlay_tr_color,
                                                  *self.overlay_color_options)

        self.overlay_bg_label = ttk.Label(self.realtime_frame, text="\tOverlay background color: ")
        self.overlay_tx_label = ttk.Label(self.realtime_frame, text="\tOverlay text color: ")
        self.overlay_tr_label = ttk.Label(self.realtime_frame, text="\tOverlay transparent color: ")

        self.overlay_font_label = ttk.Label(self.realtime_frame, text="\tOverlay font: ")
        self.overlay_font_options = ("Default", "Calibri", "Arial", "Consolas")
        self.overlay_font = tk.StringVar()
        self.overlay_font_dropdown = ttk.OptionMenu(self.realtime_frame, self.overlay_font, *self.overlay_font_options)

        self.overlay_text_size_label = ttk.Label(self.realtime_frame, text="\tOverlay text size: ")
        self.overlay_text_size_entry = ttk.Entry(self.realtime_frame, width=10)
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
        # Screen parsing settings
        self.screenparsing_frame = ttk.Frame(self.frame.interior)
        self.screenparsing_setoff_label = ttk.Label(self.screenparsing_frame, text="\t")
        self.screenparsing_header_label = ttk.Label(self.frame.interior, text="Screen parsing", justify=tk.LEFT,
                                                    font=("Calibri", 12))
        self.screenparsing_var = tk.BooleanVar()
        self.screenparsing_checkbox = ttk.Checkbutton(self.screenparsing_frame, text="Enable screen parsing",
                                                      variable=self.screenparsing_var)
        self.screenparsing_overlay_var = tk.BooleanVar()
        self.screenparsing_overlay_checkbox = ttk.Checkbutton(self.screenparsing_frame,
                                                              text="Enable screen parsing overlay",
                                                              variable=self.screenparsing_overlay_var)
        self.screenparsing_features_label = ttk.Label(self.screenparsing_frame,
                                                      text="Features enabled for screen parsing:")
        self.screenparsing_features = ["Enemy name and ship type", "Tracking penalty", "Ship health",
                                       "Power management"]
        self.screenparsing_checkboxes = OrderedDict()
        self.screenparsing_variables = {}
        for feature in self.screenparsing_features:
            self.screenparsing_variables[feature] = tk.BooleanVar()
            self.screenparsing_checkboxes[feature] = ttk.Checkbutton(self.screenparsing_frame, text=feature,
                                                                     variable=self.screenparsing_variables[feature])
        self.screenparsing_overlay_geometry = tk.BooleanVar()
        self.screenparsing_overlay_geometry_checkbox = ttk.Checkbutton(self.screenparsing_frame,
                                                                       text="Move screen parsing overlay with cursor",
                                                                       variable=self.screenparsing_overlay_geometry)
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
                                      text="Special thanks to Nightmaregale for bèta testing and to Jedipedia for "
                                           "providing clean map textures of the TDM maps",
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

    @staticmethod
    def set_custom_event_colors():
        """
        Opens a Toplevel to show the settings for the colors of the events
        view. See toplevel.event_colors for more information.
        :return: None
        """
        color_toplevel = EventColors(variables.main_window)
        color_toplevel.grid_widgets()
        color_toplevel.focus_set()

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
        self.gui_label.grid(column=0, row=0, sticky="nswe", pady=5)
        self.gui_frame.grid(column=0, row=1, sticky="nswe")
        self.color_label.grid(column=0, row=0, sticky="w")
        self.color_dropdown.grid(column=1, row=0, sticky="nswe", padx=5)
        self.custom_color_entry.grid(column=2, row=0, sticky="nswe", padx=5)
        self.logo_color_label.grid(column=0, row=1, sticky="nswe")
        self.logo_color_dropdown.grid(column=1, row=1, sticky="nswe", padx=5)
        self.event_colors_label.grid(column=0, row=2, sticky="nswe")
        self.event_colors_basic.grid(column=2, row=2, sticky="nswe")
        self.event_colors_none.grid(column=1, row=2, sticky="nswe")
        self.event_colors_adv.grid(column=3, row=2, sticky="nswe")
        self.event_scheme_label.grid(column=0, row=3, sticky="nswe")
        self.event_scheme_default.grid(column=1, row=3, sticky="nswe")
        self.event_scheme_pastel.grid(column=2, row=3, sticky="nswe")
        self.event_scheme_custom.grid(column=3, row=3, sticky="nswe")
        self.event_scheme_custom_button.grid(column=4, row=3, sticky="nswe",
                                             padx=5)
        self.date_format_label.grid(column=0, row=4, sticky="w")
        self.date_format_ymd.grid(column=1, row=4, sticky="w")
        self.date_format_ydm.grid(column=2, row=4, sticky="w")
        self.faction_label.grid(column=0, row=5, sticky="nswe")
        set_column = 0
        for radio in self.faction_options:
            set_column += 1
            radio.grid(column=set_column, row=5, sticky="nswe")
        self.auto_update_checkbox.grid(column=0, row=6, columnspan=2, padx=(55, 0))
        self.debug_window_checkbox.grid(column=0, row=7, columnspan=2, padx=(55, 0), sticky="w")
        # PARSING SETTINGS
        self.parsing_label.grid(column=0, row=2, sticky="w", pady=5)
        self.path_entry_label.grid(column=0, row=0, sticky="nswe", padx=5)
        self.path_entry_button.grid(column=2, row=0, sticky="nswe", padx=3)
        self.path_entry.grid(column=1, row=0, sticky="nswe")
        self.entry_frame.grid(column=0, row=3, sticky="nsw")
        # self.privacy_label.grid(column=0, row=0, sticky="w")
        # self.privacy_select_true.grid(column=1, row=0, sticky="w")
        # self.privacy_select_false.grid(column=2, row=0, sticky="w")
        # self.privacy_frame.grid(column=0, row=4, sticky="nswe")
        # SHARING SETTINGS
        # self.sharing_label.grid(column=0, row=5, sticky="w", pady=5)
        # self.server_label.grid(column=0, row=0, sticky="w")
        # self.server_address_entry.grid(column=1, row=0)
        # self.server_colon_label.grid(column=2, row=0)
        # self.server_port_entry.grid(column=3, row=0)
        # self.server_frame.grid(column=0, row=6, sticky="nswe")
        # self.auto_upload_label.grid(column=0, row=0)
        # self.auto_upload_true.grid(column=1, row=0)
        # self.auto_upload_false.grid(column=2, row=0)
        # self.upload_frame.grid(column=0, row=7, sticky="nswe")
        # REALTIME SETTINGS
        self.overlay_enable_label.grid(column=0, row=1, sticky="w")
        self.overlay_enable_radio_yes.grid(column=1, row=1, sticky="w")
        self.overlay_enable_radio_no.grid(column=2, row=1, sticky="w")
        self.overlay_opacity_label.grid(column=0, row=2, sticky="w")
        self.overlay_opacity_input.grid(column=1, row=2, sticky="w")
        self.realtime_settings_label.grid(column=0, row=0, sticky="w", pady=5)

        self.overlay_size_label.grid(column=0, row=3, sticky="nswe")
        self.overlay_size_radio_big.grid(column=1, row=3, sticky="nswe")
        self.overlay_size_radio_small.grid(column=2, row=3, sticky="nswe")
        self.overlay_position_label.grid(column=0, row=4, sticky="nswe")
        self.overlay_position_radio_tl.grid(column=1, row=4, sticky="nswe")
        self.overlay_position_radio_bl.grid(column=2, row=4, sticky="nswe")
        self.overlay_position_radio_tr.grid(column=3, row=4, sticky="nswe")
        self.overlay_position_radio_br.grid(column=4, row=4, sticky="nswe")
        self.overlay_position_radio_ut.grid(column=1, row=5, sticky="nswe", columnspan=2)
        self.overlay_position_radio_uc.grid(column=5, row=4, sticky="nsw")
        self.overlay_position_radio_nq.grid(column=4, row=5, sticky="nsw", columnspan=2)

        self.realtime_frame.grid(column=0, row=8, sticky="nswe")
        self.overlay_tx_label.grid(column=0, row=6, sticky="nswe")
        self.overlay_bg_label.grid(column=0, row=7, sticky="nswe")
        self.overlay_tr_label.grid(column=0, row=8, sticky="nswe")
        self.overlay_tx_dropdown.grid(column=1, row=6, sticky="nswe")
        self.overlay_bg_dropdown.grid(column=1, row=7, sticky="nswe")
        self.overlay_tr_dropdown.grid(column=1, row=8, sticky="nswe")

        self.overlay_font_label.grid(column=0, row=9, sticky="nswe")
        self.overlay_text_size_label.grid(column=0, row=10, sticky="nswe")
        self.overlay_text_size_entry.grid(column=1, row=10, sticky="nswe")
        self.overlay_font_dropdown.grid(column=1, row=9, sticky="nswe")

        self.overlay_when_gsf_label.grid(column=0, row=11)
        self.overlay_when_gsf_true.grid(column=1, row=11, sticky="w")
        self.overlay_when_gsf_false.grid(column=2, row=11, sticky="w")
        # self.realtime_timeout_label.grid(column=0, row=12, sticky="w")
        # self.realtime_timeout_entry.grid(column=1, row=12, sticky="w")
        # self.realtime_timeout_help_button.grid(column=2, row=12, sticky="w")
        # self.realtime_timeout_help_label.grid(column=3, row=12, sticky="w", columnspan=5,
        #                                      padx=5)
        # self.realtime_event_overlay_label.grid(column=0, row=13, sticky="w")
        # self.realtime_event_overlay_true.grid(column=1, row=13, sticky="w")
        # self.realtime_event_overlay_false.grid(column=2, row=13, sticky="w")
        # Screen parsing
        self.screenparsing_header_label.grid(column=0, row=9, sticky="w")
        self.screenparsing_frame.grid(column=0, row=10, sticky="nswe")
        self.screenparsing_checkbox.grid(column=0, row=0, sticky="w", padx=(55, 0), pady=5)
        self.screenparsing_features_label.grid(column=0, row=1, sticky="w", padx=(55, 0), pady=(0, 5))
        set_row = 3
        for feature in self.screenparsing_features:
            self.screenparsing_checkboxes[feature].grid(column=0, row=set_row, sticky="w", padx=(75, 0), pady=(0, 5))
            set_row += 1
        self.screenparsing_overlay_checkbox.grid(column=0, row=10, sticky="w", padx=(55, 0), pady=(0, 5))
        self.screenparsing_overlay_geometry_checkbox.grid(column=0, row=11, sticky="w", padx=(55, 0), pady=(0, 5))

        # MISC
        self.save_settings_button.grid(column=0, row=1, padx=2)
        self.discard_settings_button.grid(column=1, row=1, padx=2)
        self.default_settings_button.grid(column=2, row=1, padx=2)
        self.save_frame.grid(column=0, row=1, sticky="w")
        self.license_button.grid(column=1, row=2, sticky="w", padx=5)
        # self.privacy_button.grid(column=2, row=2, sticky="w", padx=5)
        self.copyright_label.grid(column=0, row=2, sticky="w")
        self.update_label.grid(column=0, row=2, sticky="w")
        self.thanks_label.grid(column=0, row=3, sticky="w", columnspan=2)
        self.separator.grid(column=0, row=0, sticky="nswe", pady=10)
        self.license_frame.grid(column=0, row=2, sticky="nswe", pady=5)
        self.save_frame.grid(column=0, row=0)
        # FINAL FRAME
        self.grid(column=0, row=0, sticky="nswe")
        self.top_frame.grid(column=0, row=0, sticky="nsw")
        self.separator.grid(column=0, row=1, sticky="nswe", pady=10)
        self.bottom_frame.grid(column=0, row=2, sticky="nsw")

    def update_settings(self):
        """
        Read the settings from the settigns_obj in the variables
        module and update the settings shown in the GUI accordingly.
        :return: None
        """
        self.auto_update.set(variables.settings_obj["misc"]["autoupdate"])
        if "#" not in variables.settings_obj["gui"]["color"]:
            self.color.set(variables.settings_obj["gui"]["color"])
        else:
            print("Set color: {0}, default color {1}".format(variables.settings_obj["gui"]["color"],
                                                             variables.settings_obj.defaults["gui"]["color"]))
            if variables.settings_obj["gui"]["color"] is variables.settings_obj.defaults["gui"]["color"]:
                self.color.set("Default")
                self.custom_color_entry.delete(0, tk.END)
                self.custom_color_entry.insert(0, variables.settings_obj["gui"]["color"])
            else:
                self.color.set("Custom")
                self.custom_color_entry.delete(0, tk.END)
                self.custom_color_entry.insert(0, variables.settings_obj["gui"]["color"])
        self.logo_color.set(variables.settings_obj["gui"]["logo_color"])
        self.event_colors.set(variables.settings_obj["gui"]["event_colors"])
        self.event_scheme.set(variables.settings_obj["gui"]["event_scheme"])
        self.date_format.set(variables.settings_obj["gui"]["date_format"])
        self.faction.set(variables.settings_obj["gui"]["faction"])
        self.path_var.set(variables.settings_obj["parsing"]["cl_path"])
        self.privacy_var.set(variables.settings_obj["parsing"]["auto_ident"])
        self.server_address_entry.delete(0, tk.END)
        self.server_address_entry.insert(0, variables.settings_obj["sharing"]["server_address"])
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, variables.settings_obj["sharing"]["server_port"])
        self.auto_upload_var.set(variables.settings_obj["sharing"]["auto_upl"])
        self.overlay_enable_radio_var.set(variables.settings_obj["realtime"]["overlay"])
        self.overlay_opacity_input.delete(0, tk.END)
        self.overlay_opacity_input.insert(0, variables.settings_obj["realtime"]["opacity"])
        self.overlay_size_var.set(variables.settings_obj["realtime"]["size"])
        self.overlay_position_var.set(variables.settings_obj["realtime"]["pos"])
        self.overlay_bg_color.set(variables.settings_obj["realtime"]["overlay_bg_color"])
        self.overlay_tr_color.set(variables.settings_obj["realtime"]["overlay_tr_color"])
        self.overlay_tx_color.set(variables.settings_obj["realtime"]["overlay_tx_color"])
        self.overlay_font.set(variables.settings_obj["realtime"]["overlay_tx_font"])
        self.overlay_text_size_entry.delete(0, tk.END)
        self.overlay_text_size_entry.insert(0, variables.settings_obj["realtime"]["overlay_tx_size"])
        self.overlay_when_gsf.set(variables.settings_obj["realtime"]["overlay_when_gsf"])
        self.realtime_timeout.set(variables.settings_obj["realtime"]["timeout"])
        self.realtime_event_overlay_var.set(variables.settings_obj["realtime"]["events_overlay"])
        self.screenparsing_var.set(variables.settings_obj["realtime"]["screenparsing"])
        self.screenparsing_overlay_var.set(variables.settings_obj["realtime"]["screenparsing_overlay"])
        self.screenparsing_overlay_geometry.set(
            variables.settings_obj["realtime"]["screenparsing_overlay_geometry"])
        for key, value in self.screenparsing_variables.items():
            if key in variables.settings_obj["realtime"]["screenparsing_features"]:
                value.set(True)
            else:
                value.set(False)
        self.debug_window.set(variables.settings_obj["gui"]["debug"])
        return

    def save_settings(self):
        """
        Save the settings found in the widgets of the settings to the
        settings_obj in the variables module
        Some settings are checked before the writing occurs
        :return: None
        """
        print("[DEBUG] Save_settings called!")
        if str(self.color.get()) == variables.settings_obj["gui"]["color"] and \
                        self.logo_color.get() == variables.settings_obj["gui"]["logo_color"]:
            reboot = False
        else:
            reboot = True
        print(self.color.get())
        if "custom" in self.color.get().lower():
            hex_color = re.search(r"^#(?:[0-9a-fA-F]{1,2}){3}$", self.custom_color_entry.get())
            print(hex_color)
            if not hex_color:
                tkinter.messagebox.showerror("Error",
                                             "The custom color you entered is not valid. It must be a hex color code.")
                return
            color = self.custom_color_entry.get()
        else:
            color = self.color_choices[self.color.get()]
        if self.overlay_when_gsf.get() and not variables.settings_obj["realtime"]["overlay_when_gsf"]:
            help_string = ("""This setting makes the overlay only appear inside GSF matches. Please note that the """
                           """overlay will only appear after the first GSF ability is executed, so the overlay """
                           """may appear to display a little late, but this is normal behaviour.""")
            tkinter.messagebox.showinfo("Notice", help_string.replace("\n", "").replace("  ", ""))
        dictionary = {
            "misc": {
                "version": "v3.0.0",
                "autoupdate": self.auto_update.get()
            },
            "gui": {
                "color": color,
                "logo_color": self.logo_color.get(),
                "event_colors": self.event_colors.get(),
                "event_scheme": self.event_scheme.get(),
                "date_format": self.date_format.get(),
                "faction": self.faction.get(),
                "debug": self.debug_window.get()
            },
            "parsing": {
                "cl_path": self.path_var.get(),
                "auto_ident": self.privacy_var.get()
            },
            "sharing": {
                "server_address": self.server_address_entry.get(),
                "server_port": int(self.server_port_entry.get()),
                "auto_upl": self.auto_upload_var.get()
            },
            "realtime": {
                "overlay": self.overlay_enable_radio_var.get(),
                "opacity": float(self.overlay_opacity_input.get()),
                "size": self.overlay_size_var.get(),
                "pos": self.overlay_position_var.get(),
                "overlay_bg_color": self.overlay_bg_color.get(),
                "overlay_tr_color": self.overlay_tr_color.get(),
                "overlay_tx_color": self.overlay_tx_color.get(),
                "overlay_tx_font": self.overlay_font.get(),
                "overlay_tx_size": int(self.overlay_text_size_entry.get()),
                "overlay_when_gsf": self.overlay_when_gsf.get(),
                "timeout": float(self.realtime_timeout.get()),
                "events_overlay": self.realtime_event_overlay_var.get(),
                "screenparsing": self.screenparsing_var.get(),
                "screenparsing_overlay": self.screenparsing_overlay_var.get(),
                "screenparsing_features": [key for key, value in self.screenparsing_variables.items() if
                                           value.get() is True],
                "screenparsing_overlay_geometry": self.screenparsing_overlay_geometry.get()

            }
        }
        variables.settings_obj.write_settings(dictionary)
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
        variables.settings_obj.write_defaults()
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
