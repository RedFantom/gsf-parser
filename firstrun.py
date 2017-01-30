# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import toplevels
import settings
import tempfile
import os
import sys
import widgets
try:
    import mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import tkMessageBox
import ConfigParser

class Oob_window(tk.Tk):
    """
    This class is a child class of tk.Tk and provides a kind of setup wizard for
    the first time a new version of the parser is run. It provides screenshots
    to explain the functions of the GSF Parser and shows options to change the
    settings used for the initial settings file, providing a smooth user
    experience for each new version of the GSF Parser.

    First runs a test on the imported settings file (using settings_importer) to
    determine whether it is required to show the OOB wizard. If not, then the
    __init__ function passes control back to the main.py file.
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self.style = ttk.Style()
        try:
            self.tk.call('package', 'require', 'tile-themes')
            self.style.theme_use("plastik")
        except:
            pass
        self.next_button = ttk.Button(self, text = "Next",
                                      command = self.next_button_cb)
        self.prev_button = ttk.Button(self, text = "Previous",
                                      command = self.prev_button_cb)
        self.comp_button = ttk.Button(self, text = "Finish",
                                      command = self.comp_button_cb)
        self.cancel_button = ttk.Button(self, text = "Cancel",
                                        command = self.cancel_button_cb)

    def next_button_cb(self):
        """
        Show the next frame in the list of the frames to show and make the other
        frame disappear.
        """
        pass

    def prev_button_cb(self):
        """
        Go back to the previous frame in the list of frames to show and make the
        new frame disappear.
        """
        pass

    def comp_button_cb(self):
        """
        Read the settings the user has entered, make sure they are saved into
        the settings file and then exit the OOB wizard to pass control back to
        main.py
        """
        pass

    def cancel_button_cb(self):
        """
        Cancel the OOB wizard without saving anything, but ask the user for
        confirmation first.
        """
        pass

class welcome_frame(ttk.Frame):
    """
    This class provides the first frame that is shown when opening the OOB
    wizard. This frame contains a welcome text, the logo of the GSF Parser and
    the credits.
    """

    def __init__(self):
        ttk.Frame.__init__(self)

class gui_settings_frame(ttk.Frame):
    """
    This is the second frame, providing explanation for all the settings there
    are to set for the GUI and allowing the user to change them.
    """

class fileparsing_frame(ttk.Frame):
    """
    This is the third frame to show in the OOB wizard, explaining the features
    of file parsing and how it works and showing a screenshot to show an
    example of the interface. Also explains the Graphs frame.
    """

    def __init__(self):
        ttk.Frame.__init__(self)

class fileparsing_settings_frame(ttk.Frame):
    """
    This fourth frame shows and explains all settings there are to set for the
    file parsing and allows the user to change them where necessary.
    """

    def __init__(self):
        ttk.Frame.__init__(self)

class realtime_frame(ttk.Frame):
    """
    This is the fifth frame, explaining the features of real-time parsing and
    the interface that comes with it.
    """

    def __init__(self):
        ttk.Frame.__init__(self)

class realtime_settings_frame(ttk.Frame):
    """
    This is the sixth frame shown, explaining all settings for real-time parsing
    and allowing the user to change them.
    """

    def __init__(self):
        ttk.Frame.__init__(self)

class sharing_frame(ttk.Frame):
    """
    This is the seventh frame, explaining how the sharing of the GSF Parser
    works and it also shows the settings available so the user can change them
    if he or she wants to.
    """

    def __init__(self):
        ttk.Frame.__init__(self)

class complete_frame(ttk.Frame):
    """
    The eight and last frame of the OOB wizard giving the complete message and
    showing the user the complete button while setting the next button to
    unclickable.
    """

class settings_importer(Object):
    """
    Class capable of importing settings from settings files for all versions of
    the GSF Parser and putting them in a dictionary in order to allow the user
    to import already set settings.
    """

    def __init__(self):
        self.first_install = False
        self.conf = ConfigParser.RawConfigParser()
        self.directory = directory.replace("\\temp", "") + "\\GSF Parser"
        self.file_name = tempfile.gettempdir().\
                         replace("\\temp", "") + "\\GSF Parser\\settings.ini"
        try:
            os.makedirs(self.directory, True)
        except WindowsError:
            self.first_install = True
        if "settings.ini" not in os.listdir(self.directory):
            self.first_install = True
        if self.first_install:
            return
        self.conf.read(self.file_name)
        self.import_set()

    def import_set(self):
        # If this setting cannot be found in the settings file, then continue as
        # if this was a new installation.
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
