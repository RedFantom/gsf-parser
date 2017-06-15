# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import configparser
from tools import settings
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import variables
import os


class SettingsImporter(tk.Toplevel):
    """
    Class capable of importing settings from settings files for all versions of
    the GSF Parser and putting them in a dictionary in order to allow the user
    to import already set settings.
    """

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.wm_title("Settings Importer")
        self.resizable(False, False)
        self.import_button = ttk.Button(self, text="Import", command=self.import_settings_file, width=20)
        self.export_button = ttk.Button(self, text="Export", command=self.export_settings_file, width=20)
        self.import_button.grid(column=0, row=0, padx=5, pady=5)
        self.export_button.grid(column=0, row=1, padx=5, pady=5)

    @staticmethod
    def export_settings_file():
        file_name = filedialog.asksaveasfilename(filetypes=[("Settings file", ".ini")])
        with open(file_name, "w") as file_obj:
            variables.settings_obj.conf.write(file_obj)

    @staticmethod
    def import_settings_file():
        """
        Import all settings that can be read from the old settings file. If the
        setting cannot be read, use the default value for the setting from the
        settings.defaults class.
        If a certain setting is not in the specified configuration file,
        a ConfigParser.NoOptionError is raised.
        If a certain section is not in the specified configuration file,
        a ConfigParser.NoSectionError is raised.
        If the user is attempting to add a section to a configuration file while
        this section already exists, the ConfigParser.DuplicateSectionError is
        raised.
        """
        file_name = filedialog.askopenfilename()
        config = configparser.RawConfigParser()
        config.read(file_name)
        try:
            config.add_section("misc")
        except configparser.DuplicateSectionError:
            pass
        try:
            config.add_section("parsing")
        except configparser.DuplicateSectionError:
            pass
        try:
            config.add_section("sharing")
        except configparser.DuplicateSectionError:
            pass
        try:
            config.add_section("realtime")
        except configparser.DuplicateSectionError:
            pass
        try:
            config.add_section("gui")
        except configparser.DuplicateSectionError:
            pass
        version = "v3.0.0"
        try:
            autoupdate = config.get("misc", "autoupdate")
        except configparser.NoOptionError:
            autoupdate = settings.Defaults.autoupdate
        try:
            cl_path = config.get("parsing", "cl_path")
        except configparser.NoOptionError:
            cl_path = settings.Defaults.cl_path
        try:
            if config.get("parsing", "auto_ident") == "True":
                auto_ident = True
            else:
                auto_ident = False
        except configparser.NoOptionError:
            auto_ident = settings.Defaults.auto_ident
        try:
            server_address = config.get("sharing", "server_address")
        except configparser.NoOptionError:
            server_address = settings.Defaults.server_address
        try:
            server_port = int(config.get("sharing", "server_port"))
        except configparser.NoOptionError:
            server_port = settings.Defaults.server_port
        try:
            if config.get("sharing", "auto_upl") == "True":
                auto_upl = True
            else:
                auto_upl = False
        except configparser.NoOptionError:
            auto_upl = settings.Defaults.auto_upl
        try:
            if config.get("realtime", "overlay") == "True":
                overlay = True
            else:
                overlay = False
        except configparser.NoOptionError:
            overlay = settings.Defaults.overlay
        try:
            opacity = float(config.get("realtime", "opacity"))
        except configparser.NoOptionError:
            opacity = settings.Defaults.opacity
        except TypeError:
            opacity = settings.Defaults.opacity
        try:
            size = config.get("realtime", "size")
        except configparser.NoOptionError:
            size = settings.Defaults.size
        try:
            pos = config.get("realtime", "pos")
        except configparser.NoOptionError:
            pos = settings.Defaults.pos
        try:
            overlay_bg_color = config.get("realtime", "overlay_bg_color")
        except configparser.NoOptionError:
            overlay_bg_color = settings.Defaults.overlay_bg_color
        try:
            overlay_tr_color = config.get("realtime", "overlay_tr_color")
        except configparser.NoOptionError:
            overlay_tr_color = settings.Defaults.overlay_tr_color
        try:
            overlay_tx_color = config.get("realtime", "overlay_tx_color")
        except configparser.NoOptionError:
            overlay_tx_color = settings.Defaults.overlay_tx_color
        try:
            color = config.get("gui", "color")
        except configparser.NoOptionError:
            color = settings.Defaults.color
        try:
            event_colors = config.get("gui", "event_colors")
        except configparser.NoOptionError:
            event_colors = settings.Defaults.event_colors
        try:
            event_scheme = config.get("gui", "event_scheme")
        except configparser.NoOptionError:
            event_scheme = settings.Defaults.event_scheme
        try:
            logo_color = config.get("gui", "logo_color")
        except configparser.NoOptionError:
            logo_color = settings.Defaults.logo_color
        try:
            faction = config.get("gui", "faction")
        except configparser.NoOptionError:
            faction = settings.Defaults.faction
        try:
            date_format = config.get("gui", "date_format")
        except configparser.NoOptionError:
            date_format = settings.Defaults.date_format
        try:
            overlay_tx_font = config.get("realtime", "overlay_tx_font")
        except configparser.NoOptionError:
            overlay_tx_font = settings.Defaults.overlay_tx_font
        try:
            overlay_tx_size = config.get("realtime", "overlay_tx_size")
        except configparser.NoOptionError:
            overlay_tx_size = settings.Defaults.overlay_tx_size
        try:
            if config.get("realtime", "overlay_when_gsf") == "True":
                overlay_when_gsf = True
            else:
                overlay_when_gsf = False
        except configparser.NoOptionError:
            overlay_when_gsf = settings.Defaults.overlay_when_gsf
        try:
            timeout = float(config.get("realtime", "timeout"))
        except configparser.NoOptionError or ValueError:
            timeout = settings.Defaults.timeout
        try:
            if config.get("realtime", "events_overlay") == "True":
                events_overlay = True
            elif config.get("realtime", "events_overlay") == "False":
                events_overlay = False
            else:
                events_overlay = settings.Defaults.events_overlay
        except configparser.NoOptionError:
            events_overlay = settings.Defaults.events_overlay
        try:
            if config.get("realtime", "screenparsing") == "True":
                screenparsing = True
            elif config.get("realtime", "screenparsing") == "False":
                screenparsing = False
            else:
                screenparsing = settings.Defaults.screenparsing
        except configparser.NoOptionError:
            screenparsing = settings.Defaults.screenparsing
        try:
            if config.get("realtime", "screenparsing_overlay") == "True":
                screenparsing_overlay = True
            elif config.get("realtime", "screenparsing_overlay") == "False":
                screenparsing_overlay = False
            else:
                screenparsing_overlay = settings.Defaults.screenparsing_overlay
        except configparser.NoOptionError:
            screenparsing_overlay = settings.Defaults.screenparsing_overlay
        try:
            screenparsing_features = config.get("realtime", "screenparsing_features")
        except configparser.NoOptionError:
            screenparsing_features = settings.Defaults.screenparsing_features
        variables.settings_obj.write_settings({
            "misc": {
                "version": version,
                "autoupdate": autoupdate
            },
            "gui": {
                "color": color,
                "logo_color": logo_color,
                "event_colors": event_colors,
                "event_scheme": event_scheme,
                "date_format": date_format,
                "faction": faction
            },
            "parsing": {
                "cl_path": cl_path,
                "auto_ident": auto_ident
            },
            "sharing": {
                "server_address": server_address,
                "server_port": server_port
            },
            "realtime": {
                "overlay": overlay,
                "opacity": opacity,
                "size": size,
                "pos": pos,
                "overlay_bg_color": overlay_bg_color,
                "overlay_tr_color": overlay_tr_color,
                "overlay_tx_color": overlay_tr_color,
                "overlay_tx_font": overlay_tx_font,
                "overlay_tx_size": overlay_tx_size,
                "overlay_when_gsf": overlay_when_gsf,
                "timeout": timeout,
                "events_overlay": events_overlay,
                "screenparsing": screenparsing,
                "screenparsing_overlay": screenparsing_overlay,
                "screenparsing_features": screenparsing_features
            }
        })
