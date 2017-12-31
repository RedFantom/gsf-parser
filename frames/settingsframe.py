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
import sys
import os
import variables
from widgets import VerticalScrollFrame, HoverInfo
from toplevels.colors import EventColors
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
        self.after_id = None
        self.main_window = main_window
        ttk.Frame.__init__(self, root_frame)
        """
        Parent Widgets
        """
        self.frame = VerticalScrollFrame(self, canvasheight=295, canvaswidth=self.main_window.width - 30)
        self.gui_frame = ttk.Frame(self.frame.interior)
        self.parsing_frame = ttk.Frame(self.frame.interior)
        self.realtime_frame = ttk.Frame(self.frame.interior)
        self.screen_frame = ttk.Frame(self.frame.interior)
        self.credits_frame = ttk.Frame(self)

        """
        UI Settings
        """
        self.gui_label = ttk.Label(
            self.frame.interior, text="User Interface", justify=tk.LEFT, font=("default", 13, "bold"))
        # Event color type
        self.gui_event_colors_type = tk.BooleanVar()
        self.gui_event_colors_checkbox = ttk.Checkbutton(
            self.gui_frame, text="Use Advanced Event Color Scheme", variable=self.gui_event_colors_type,
            command=self.save_settings)
        HoverInfo(
            self.gui_event_colors_checkbox,
            text="The Advanced Color Scheme offers more colors to distinguish between more different types of events.")
        # Event color scheme
        self.gui_event_colors_scheme = tk.StringVar()
        self.gui_event_colors_label = ttk.Label(self.gui_frame, text="Event Color Scheme:", justify=tk.LEFT)
        self.gui_event_colors_dropdown = ttk.OptionMenu(
            self.gui_frame, self.gui_event_colors_scheme, *("Choose", "Bright", "Pastel", "Custom"),
            command=self.save_settings)
        self.gui_event_colors_button = ttk.Button(
            self.gui_frame, text="Edit Custom", command=self.set_custom_event_colors)
        # Faction images
        self.gui_faction = tk.StringVar()
        self.gui_faction_label = ttk.Label(self.gui_frame, text="Faction: ", justify=tk.LEFT)
        self.gui_faction_dropdown = ttk.OptionMenu(
            self.gui_frame, self.gui_faction, *("Choose", "Empire", "Republic"), command=self.save_settings)
        # Check for updates
        self.gui_check_updates = tk.BooleanVar()
        self.gui_check_updates_checkbox = ttk.Checkbutton(
            self.gui_frame, text="Automatically check for updates on start-up", variable=self.gui_check_updates,
            command=self.save_settings)
        # Debug Window
        self.gui_debug_window = tk.BooleanVar()
        self.gui_debug_window_checkbox = ttk.Checkbutton(
            self.gui_frame, text="Show window with debug output", variable=self.gui_debug_window,
            command=self.save_settings)

        """
        Parsing settings
        """
        self.parsing_label = ttk.Label(
            self.frame.interior, text="Parsing", font=("default", 13, "bold"), justify=tk.LEFT)
        # CombatLogs path
        self.parsing_path = tk.StringVar()
        self.parsing_path_label = ttk.Label(self.parsing_frame, text="CombatLogs folder:", justify=tk.LEFT)
        self.parsing_path_entry = ttk.Entry(
            self.parsing_frame, width=80 if sys.platform != "linux" else 60, textvariable=self.parsing_path)
        self.parsing_path_entry.bind("<Key>", self.save_settings_delayed)
        self.parsing_path_button = ttk.Button(self.parsing_frame, text="Browse", command=self.set_directory_dialog)

        """
        RealTime settings
        """
        self.realtime_label = ttk.Label(
            self.frame.interior, text="Real-time Parsing", font=("default", 13, "bold"), justify=tk.LEFT)
        # Enable real-time overlay
        self.realtime_overlay_enabled = tk.BooleanVar()
        self.realtime_overlay_enabled_checkbox = ttk.Checkbutton(
            self.realtime_frame, text="Enable overlay for real-time parsing", variable=self.realtime_overlay_enabled,
            command=self.save_settings)
        # Overlay text color
        self.realtime_overlay_text_color = tk.StringVar()
        self.realtime_overlay_text_color_label = ttk.Label(
            self.realtime_frame, text="Overlay text color:", justify=tk.LEFT)
        self.realtime_overlay_text_color_dropdown = ttk.OptionMenu(
            self.realtime_frame, self.realtime_overlay_text_color, *("Yellow", "Green", "Blue", "Red", "Black"),
            command=self.save_settings)
        # Overlay position
        self.realtime_overlay_position_frame = ttk.Frame(self.realtime_frame)
        self.realtime_overlay_position_label = ttk.Label(self.realtime_overlay_position_frame, text="Overlay position:")
        self.realtime_overlay_position_x_label = ttk.Label(self.realtime_overlay_position_frame, text="X Coordinate:")
        self.realtime_overlay_position_x = ttk.Entry(self.realtime_overlay_position_frame, width=4)
        self.realtime_overlay_position_y_label = ttk.Label(self.realtime_overlay_position_frame, text="Y Coordinate:")
        self.realtime_overlay_position_y = ttk.Entry(self.realtime_overlay_position_frame, width=4)
        help_text = "The overlay's position is set as a pair of coordinates, in pixels, measured from the top left " \
                    "corner of the screen."
        for widget in [self.realtime_overlay_position_x_label, self.realtime_overlay_position_y_label,
                       self.realtime_overlay_position_y, self.realtime_overlay_position_x]:
            HoverInfo(widget, text=help_text)
        self.realtime_overlay_position_y.bind("<Key>", self.save_settings_delayed)
        self.realtime_overlay_position_x.bind("<Key>", self.save_settings_delayed)
        # Disable overlay when not in match
        self.realtime_overlay_disable = tk.BooleanVar()
        self.realtime_overlay_disable_checkbox = ttk.Checkbutton(
            self.realtime_frame, text="Hide overlay when not in a GSF match", variable=self.realtime_overlay_disable,
            command=self.save_settings)

        """
        Screen parsing settings
        """
        self.screen_label = ttk.Label(
            self.frame.interior, text="Screen Parsing", font=("default", 13, "bold"), justify=tk.LEFT)
        # Screen parsing enabled
        self.screen_enabled = tk.BooleanVar()
        self.screen_checkbox = ttk.Checkbutton(
            self.screen_frame, text="Enable screen parsing", variable=self.screen_enabled, command=self.save_settings)
        # Screen parsing overlay
        self.screen_overlay = tk.BooleanVar()
        self.screen_overlay_checkbox = ttk.Checkbutton(
            self.screen_frame, text="Enable screen parsing overlay", variable=self.screen_overlay,
            command=self.save_settings)
        # Screen parsing features
        self.screen_features_label = ttk.Label(self.screen_frame, text="Features enabled for screen parsing:")
        self.screen_features = ["Tracking penalty", "Ship health", "Power management", "Mouse and Keyboard"]
        self.screen_checkboxes = OrderedDict()
        self.screen_variables = {}
        for feature in self.screen_features:
            self.screen_variables[feature] = tk.BooleanVar()
            self.screen_checkboxes[feature] = ttk.Checkbutton(
                self.screen_frame, text=feature, variable=self.screen_variables[feature], command=self.save_settings)

        """
        Miscellaneous
        """
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.credits_label = ttk.Label(
            self.credits_frame,
            text="Copyright (C) 2016-2018 RedFantom, Daethyra and Sprigellania\n"
                 "Available under the GNU GPLv3 License\n\n"
                 "Special thanks to everyone who has provided feedback, and to JediPedia for the the clean GSF map "
                 "textures.")
        self.update_settings()

    def set_custom_event_colors(self):
        """
        Opens a Toplevel to show the settings for the colors of the events view.
        """
        color_toplevel = EventColors(variables.main_window)
        color_toplevel.grid_widgets()
        color_toplevel.focus_set()
        self.wait_window(color_toplevel)
        self.focus_set()

    def set_directory_dialog(self):
        """
        Open a tkFileDialog to ask the user for the directory of the CombatLogs
        so the user does not have to enter the full path manually.
        """
        directory = tkinter.filedialog.askdirectory(
            initialdir=self.parsing_path.get(), mustexist=True, parent=self.main_window,
            title="GSF Parser: Choosing directory")
        if directory is None or directory == "" or not os.path.exists(directory):
            return
        self.parsing_path.set(directory)

    def grid_widgets(self):
        """
        Put all the widgets created in the __init__ function in their respective places.
        """
        padding_default = {"padx": 5, "pady": (0, 5)}
        padding_label = {"padx": (40, 5), "pady": (0, 5)}
        padding_header = {"padx": 5, "pady": (10, 5)}
        padding_frame = {"padx": 5, "pady": 5}
        sticky_default = {"sticky": "nsw"}
        sticky_button = {"sticky": "nswe"}
        checkbox = {"columnspan": 2}
        """
        Parent widgets
        """
        self.frame.grid(row=0, column=0, **padding_frame)
        self.separator.grid(row=1, column=0, **padding_default, sticky="we")
        self.credits_frame.grid(row=2, column=0, **padding_default, **sticky_default)
        self.credits_label.grid(row=0, column=0, **padding_default, **sticky_default)
        """
        UI settings
        """
        # General
        self.gui_label.grid(row=0, column=0, **padding_header, **sticky_default)
        self.gui_frame.grid(row=1, column=0, **padding_frame, **sticky_default)
        # Event color type
        self.gui_event_colors_checkbox.grid(row=0, column=0, **padding_label, **sticky_default, **checkbox)
        # Event color scheme
        self.gui_event_colors_label.grid(row=1, column=0, **padding_label, **sticky_default)
        self.gui_event_colors_dropdown.grid(row=1, column=1, **padding_default, **sticky_button)
        self.gui_event_colors_button.grid(row=1, column=2, **padding_default, **sticky_button)
        # Faction Images
        self.gui_faction_label.grid(row=2, column=0, **padding_label, **sticky_default)
        self.gui_faction_dropdown.grid(row=2, column=1, **padding_default, **sticky_button)
        # Updates
        self.gui_check_updates_checkbox.grid(row=3, column=0, **padding_label, **sticky_default, **checkbox)
        # Debug Window
        self.gui_debug_window_checkbox.grid(row=4, column=0, **padding_label, **sticky_default, **checkbox)
        """
        Parsing settings
        """
        # General
        self.parsing_label.grid(row=2, column=0, **padding_header, **sticky_default)
        self.parsing_frame.grid(row=3, column=0, **padding_frame, **sticky_default)
        # CombatLogs path
        self.parsing_path_label.grid(row=0, column=0, **padding_label, **sticky_default)
        self.parsing_path_entry.grid(row=0, column=1, **padding_default, **sticky_default)
        self.parsing_path_button.grid(row=0, column=2, **padding_default, **sticky_button)
        """
        RealTime settings
        """
        # General
        self.realtime_label.grid(row=4, column=0, **padding_header, **sticky_default)
        self.realtime_frame.grid(row=5, column=0, **padding_frame, **sticky_default)
        # Enable real-time overlay
        self.realtime_overlay_enabled_checkbox.grid(row=0, column=0, **padding_label, **sticky_button, **checkbox)
        # Overlay text color
        self.realtime_overlay_text_color_label.grid(row=1, column=0, **padding_label, **sticky_default)
        self.realtime_overlay_text_color_dropdown.grid(row=1, column=1, **padding_default, **sticky_button)
        # Overlay position
        self.realtime_overlay_position_frame.grid(row=2, column=0, columnspan=4, **padding_label, **sticky_default)
        self.realtime_overlay_position_label.grid(row=0, column=0, padx=0, pady=(0, 5), **sticky_default)
        self.realtime_overlay_position_x_label.grid(row=1, column=0, **padding_label, **sticky_default)
        self.realtime_overlay_position_x.grid(row=1, column=1, **padding_default, **sticky_default)
        self.realtime_overlay_position_y_label.grid(row=2, column=0, **padding_label, **sticky_default)
        self.realtime_overlay_position_y.grid(row=2, column=1, **padding_default, **sticky_default)
        # Disable overlay when not in match
        self.realtime_overlay_disable_checkbox.grid(row=3, column=0, **padding_label, **sticky_default, **checkbox)

        """
        Screen parsing settings
        """
        # General
        self.screen_label.grid(row=6, column=0, **padding_header, **sticky_default)
        self.screen_frame.grid(row=7, column=0, **padding_frame, **sticky_default)
        # Screen parsing enabled
        self.screen_checkbox.grid(row=0, column=0, **padding_label, **sticky_default, **checkbox)
        # Screen parsing overlay
        self.screen_overlay_checkbox.grid(row=1, column=0, **padding_label, **sticky_default, **checkbox)
        # Screen parsing features
        self.screen_features_label.grid(row=2, column=0, **padding_label, **sticky_default)
        set_row = 3
        for feature in self.screen_checkboxes.values():
            feature.grid(row=set_row, column=0, padx=(80, 5), pady=(0, 5), **sticky_default)
            set_row += 1

    def update_settings(self):
        """
        Read the settings from the settings_obj in the variables
        module and update the settings shown in the GUI accordingly.
        """
        pass

    def save_settings(self, *args):
        """
        Save the settings found in the widgets of the settings to the
        settings_obj in the variables module
        Some settings are checked before the writing occurs
        """
        print("[MainWindow] Saving settings")
        dictionary = {
            "misc": {
                "version": variables.settings["misc"]["version"],
                "autoupdate": self.gui_check_updates.get()
            },
            "gui": {
                "event_colors": self.gui_event_colors_type.get(),
                "event_scheme": self.gui_event_colors_scheme.get(),
                "faction": self.gui_faction.get(),
                "debug": self.gui_debug_window.get()
            },
            "parsing": {
                "path": self.parsing_path.get(),
            },
            "realtime": {
                "overlay": self.realtime_overlay_enabled.get(),
                "pos": "{}+{}".format(self.realtime_overlay_position_x.get(), self.realtime_overlay_position_x.get()),
                "overlay_when_gsf": self.realtime_overlay_disable.get(),
                "screenparsing": self.screen_enabled.get(),
                "screenparsing_overlay": self.screen_overlay.get(),
                "screenparsing_features": [key for key, value in self.screen_variables.items() if value.get() is True],
            }
        }
        variables.settings.write_settings(dictionary)
        self.update_settings()
        self.main_window.file_select_frame.add_files()
        variables.colors.set_scheme(self.gui_event_colors_scheme.get())
        self.after_id = None

    def save_settings_delayed(self, *args):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        self.after_id = self.after(2000, self.save_settings)

    def discard_settings(self):
        """
        Discard the changes to the settings by reloading the settings
        from the settings_obj
        """
        self.update_settings()

    def default_settings(self):
        """
        Write the default settings to the settings_obj found in the
        settings.defaults class and then update the settings shown
        """
        variables.settings.write_defaults()
        self.update_settings()

    @staticmethod
    def show_license():
        """
        Show that this software is available under GNU GPLv3
        """
        tkinter.messagebox.showinfo("License",
                                    "This program is licensed under the General Public License Version 3, by GNU. See "
                                    "LICENSE in the installation directory for more details")
