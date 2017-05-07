# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import os
import configparser
from tools import settings, utilities


class SettingsImporter(object):
    """
    Class capable of importing settings from settings files for all versions of
    the GSF Parser and putting them in a dictionary in order to allow the user
    to import already set settings.
    """

    def __init__(self):
        self.first_install = False
        self.conf = configparser.RawConfigParser()
        self.directory = utilities.get_temp_directory()
        self.file_name = self.directory + "\\GSF Parser\\settings.ini"
        try:
            os.makedirs(self.directory, True)
        except OSError:
            self.first_install = True
        if "settings.ini" not in os.listdir(self.directory):
            self.first_install = True
        if self.first_install:
            return
        self.conf.read(self.file_name)
        self.import_set()

    def import_set(self):
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
        try:
            self.conf.add_section("misc")
        except configparser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("parsing")
        except configparser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("sharing")
        except configparser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("realtime")
        except configparser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("gui")
        except configparser.DuplicateSectionError:
            pass
        try:
            self.version = self.conf.get("misc", "version")
        except configparser.NoOptionError:
            self.first_install = True
            return
        try:
            self.cl_path = self.conf.get("parsing", "cl_path")
        except configparser.NoOptionError:
            self.cl_path = settings.Defaults.cl_path
        try:
            if self.conf.get("parsing", "auto_ident") == "True":
                self.auto_ident = True
            else:
                self.auto_ident = False
        except configparser.NoOptionError:
            self.auto_ident = settings.Defaults.auto_ident
        try:
            self.server_address = self.conf.get("sharing", "server_address")
        except configparser.NoOptionError:
            self.server_address = settings.Defaults.server_address
        try:
            self.server_port = int(self.conf.get("sharing", "server_port"))
        except configparser.NoOptionError:
            self.server_port = settings.Defaults.server_port
        try:
            if self.conf.get("sharing", "auto_upl") == "True":
                self.auto_upl = True
            else:
                self.auto_upl = False
        except configparser.NoOptionError:
            self.auto_upl = settings.Defaults.auto_upl
        try:
            if self.conf.get("realtime", "overlay") == "True":
                self.overlay = True
            else:
                self.overlay = False
        except configparser.NoOptionError:
            self.overlay = settings.Defaults.overlay
        try:
            self.overlay_bg_color = self.conf.get("realtime", "overlay_bg_color")
        except configparser.NoOptionError:
            self.overlay_bg_color = settings.Defaults.overlay_bg_color
        try:
            self.overlay_tr_color = self.conf.get("realtime", "overlay_tr_color")
        except configparser.NoOptionError:
            self.overlay_tr_color = settings.Defaults.overlay_tr_color
        try:
            self.overlay_tx_color = self.conf.get("realtime", "overlay_tx_color")
        except configparser.NoOptionError:
            self.overlay_tx_color = settings.Defaults.overlay_tx_color
        try:
            self.opacity = float(self.conf.get("realtime", "opacity"))
        except configparser.NoOptionError:
            self.opacity = settings.Defaults.opacity
        except TypeError:
            self.opacity = settings.Defaults.opacity
        try:
            self.size = self.conf.get("realtime", "size")
        except configparser.NoOptionError:
            self.size = settings.Defaults.size
        try:
            self.pos = self.conf.get("realtime", "pos")
        except configparser.NoOptionError:
            self.pos = settings.Defaults.pos
        try:
            self.color = self.conf.get("gui", "color")
        except configparser.NoOptionError:
            self.color = settings.Defaults.color
        try:
            self.event_colors = self.conf.get("gui", "event_colors")
        except configparser.NoOptionError:
            self.event_colors = settings.Defaults.event_colors
        try:
            self.event_scheme = self.conf.get("gui", "event_scheme")
        except configparser.NoOptionError:
            self.event_scheme = settings.Defaults.event_scheme
        try:
            self.logo_color = self.conf.get("gui", "logo_color")
        except configparser.NoOptionError:
            self.logo_color = settings.Defaults.logo_color
        try:
            self.overlay_tx_font = self.conf.get("realtime", "overlay_tx_font")
        except configparser.NoOptionError:
            self.overlay_tx_font = settings.Defaults.overlay_tx_font
        try:
            self.overlay_tx_size = self.conf.get("realtime", "overlay_tx_size")
        except configparser.NoOptionError:
            self.overlay_tx_size = settings.Defaults.overlay_tx_size
        try:
            if self.conf.get("realtime", "overlay_when_gsf") == "True":
                self.overlay_when_gsf = True
            else:
                self.overlay_when_gsf = False
        except configparser.NoOptionError:
            self.overlay_when_gsf = settings.Defaults.overlay_when_gsf
