# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import os
import ConfigParser
from tools import settings, utilities


class settings_importer(object):
    """
    Class capable of importing settings from settings files for all versions of
    the GSF Parser and putting them in a dictionary in order to allow the user
    to import already set settings.
    """

    def __init__(self):
        self.first_install = False
        self.conf = ConfigParser.RawConfigParser()
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
        except ConfigParser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("parsing")
        except ConfigParser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("sharing")
        except ConfigParser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("realtime")
        except ConfigParser.DuplicateSectionError:
            pass
        try:
            self.conf.add_section("gui")
        except ConfigParser.DuplicateSectionError:
            pass
        try:
            self.version = self.conf.get("misc", "version")
        except ConfigParser.NoOptionError:
            self.first_install = True
            return
        try:
            self.cl_path = self.conf.get("parsing", "cl_path")
        except ConfigParser.NoOptionError:
            self.cl_path = settings.defaults.cl_path
        try:
            if self.conf.get("parsing", "auto_ident") == "True":
                self.auto_ident = True
            else:
                self.auto_ident = False
        except ConfigParser.NoOptionError:
            self.auto_ident = settings.defaults.auto_ident
        try:
            self.server_address = self.conf.get("sharing", "server_address")
        except ConfigParser.NoOptionError:
            self.server_address = settings.defaults.server_address
        try:
            self.server_port = int(self.conf.get("sharing", "server_port"))
        except ConfigParser.NoOptionError:
            self.server_port = settings.defaults.server_port
        try:
            if self.conf.get("sharing", "auto_upl") == "True":
                self.auto_upl = True
            else:
                self.auto_upl = False
        except ConfigParser.NoOptionError:
            self.auto_upl = settings.defaults.auto_upl
        try:
            if self.conf.get("realtime", "overlay") == "True":
                self.overlay = True
            else:
                self.overlay = False
        except ConfigParser.NoOptionError:
            self.overlay = settings.defaults.overlay
        try:
            self.overlay_bg_color = self.conf.get("realtime", "overlay_bg_color")
        except ConfigParser.NoOptionError:
            self.overlay_bg_color = settings.defaults.overlay_bg_color
        try:
            self.overlay_tr_color = self.conf.get("realtime", "overlay_tr_color")
        except ConfigParser.NoOptionError:
            self.overlay_tr_color = settings.defaults.overlay_tr_color
        try:
            self.overlay_tx_color = self.conf.get("realtime", "overlay_tx_color")
        except ConfigParser.NoOptionError:
            self.overlay_tx_color = settings.defaults.overlay_tx_color
        try:
            self.opacity = float(self.conf.get("realtime", "opacity"))
        except ConfigParser.NoOptionError:
            self.opacity = settings.defaults.opacity
        except TypeError:
            self.opacity = settings.defaults.opacity
        try:
            self.size = self.conf.get("realtime", "size")
        except ConfigParser.NoOptionError:
            self.size = settings.defaults.size
        try:
            self.pos = self.conf.get("realtime", "pos")
        except ConfigParser.NoOptionError:
            self.pos = settings.defaults.pos
        try:
            self.color = self.conf.get("gui", "color")
        except ConfigParser.NoOptionError:
            self.color = settings.defaults.color
        try:
            self.event_colors = self.conf.get("gui", "event_colors")
        except ConfigParser.NoOptionError:
            self.event_colors = settings.defaults.event_colors
        try:
            self.event_scheme = self.conf.get("gui", "event_scheme")
        except ConfigParser.NoOptionError:
            self.event_scheme = settings.defaults.event_scheme
        try:
            self.logo_color = self.conf.get("gui", "logo_color")
        except ConfigParser.NoOptionError:
            self.logo_color = settings.defaults.logo_color
        try:
            self.overlay_tx_font = self.conf.get("realtime", "overlay_tx_font")
        except ConfigParser.NoOptionError:
            self.overlay_tx_font = settings.defaults.overlay_tx_font
        try:
            self.overlay_tx_size = self.conf.get("realtime", "overlay_tx_size")
        except ConfigParser.NoOptionError:
            self.overlay_tx_size = settings.defaults.overlay_tx_size
        try:
            if self.conf.get("realtime", "overlay_when_gsf") == "True":
                self.overlay_when_gsf = True
            else:
                self.overlay_when_gsf = False
        except ConfigParser.NoOptionError:
            self.overlay_when_gsf = settings.defaults.overlay_when_gsf
