"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import sys
import os
from collections import OrderedDict
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from ttkwidgets.frames import Balloon
# Project Modules
from network.discord import DiscordClient
from parsing.vision import timer_boxes
from toplevels.event_colors import EventColors
from utils.utilities import get_screen_resolution
from variables import settings, colors
from widgets import VerticalScrollFrame


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
        self.pa_frame = ttk.Frame(self.frame.interior)
        self.rt_frame = ttk.Frame(self.frame.interior)
        self.sc_frame = ttk.Frame(self.frame.interior)
        self.sh_frame = ttk.Frame(self.frame.interior)
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
        Balloon(
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
        Sharing settings
        """
        self.sh_label = ttk.Label(
            self.frame.interior, text="Discord Sharing", font=("default", 13, "bold"), justify=tk.LEFT)
        self.sh_enable = tk.BooleanVar()
        self.sh_enable_checkbox = ttk.Checkbutton(
            self.sh_frame, text="Enable Discord Sharing", variable=self.sh_enable)
        self.sh_tag = tk.StringVar()
        self.sh_tag_label = ttk.Label(self.sh_frame, text="Discord Tag:")
        self.sh_tag_entry = ttk.Entry(
            self.sh_frame, textvariable=self.sh_tag, width=20)
        self.sh_auth = tk.StringVar()
        self.sh_auth_label = ttk.Label(self.sh_frame, text="Authentication code:")
        self.sh_auth_entry = ttk.Entry(
            self.sh_frame, textvariable=self.sh_auth, width=8)
        self.sh_host = tk.StringVar()
        self.sh_address_label = ttk.Label(self.sh_frame, text="Server:")
        self.sh_host_entry = ttk.Entry(
            self.sh_frame, textvariable=self.sh_host, width=35)
        self.sh_port = tk.StringVar()
        self.sh_port_entry = ttk.Entry(
            self.sh_frame, textvariable=self.sh_port, width=8)

        """
        Parsing settings
        """
        self.pa_label = ttk.Label(
            self.frame.interior, text="Parsing", font=("default", 13, "bold"), justify=tk.LEFT)
        # CombatLogs path
        self.pa_path = tk.StringVar()
        self.pa_path_label = ttk.Label(self.pa_frame, text="CombatLogs folder:", justify=tk.LEFT)
        self.pa_path_entry = ttk.Entry(
            self.pa_frame, width=80 if sys.platform != "linux" else 60, textvariable=self.pa_path)
        self.pa_path_entry.bind("<Key>", self.save_settings_delayed)
        self.pa_path_button = ttk.Button(self.pa_frame, text="Browse", command=self.set_directory_dialog)

        """
        RealTime settings
        """
        self.rt_label = ttk.Label(
            self.frame.interior, text="Real-time Parsing", font=("default", 13, "bold"), justify=tk.LEFT)
        # Enable real-time overlay
        self.rt_overlay_enabled = tk.BooleanVar()
        self.rt_overlay_enabled_checkbox = ttk.Checkbutton(
            self.rt_frame, text="Enable overlay for real-time parsing", variable=self.rt_overlay_enabled,
            command=self.save_settings)
        # Overlay text color
        self.rt_overlay_text_color = tk.StringVar()
        self.rt_overlay_text_color_label = ttk.Label(
            self.rt_frame, text="Overlay text color:", justify=tk.LEFT)
        self.rt_overlay_text_color_dropdown = ttk.OptionMenu(
            self.rt_frame, self.rt_overlay_text_color, *("Yellow", "Green", "Blue", "Red", "Black"),
            command=self.save_settings)
        # Overlay position
        self.rt_overlay_position_frame = ttk.Frame(self.rt_frame)
        self.rt_overlay_position_label = ttk.Label(self.rt_overlay_position_frame, text="Overlay position:")
        self.rt_overlay_position_x_label = ttk.Label(self.rt_overlay_position_frame, text="X Coordinate:")
        self.rt_overlay_position_x = ttk.Entry(self.rt_overlay_position_frame, width=4)
        self.rt_overlay_position_y_label = ttk.Label(self.rt_overlay_position_frame, text="Y Coordinate:")
        self.rt_overlay_position_y = ttk.Entry(self.rt_overlay_position_frame, width=4)
        help_text = "The overlay's position is set as a pair of coordinates, in pixels, measured from the top left " \
                    "corner of the screen."
        for widget in [self.rt_overlay_position_x_label, self.rt_overlay_position_y_label,
                       self.rt_overlay_position_y, self.rt_overlay_position_x]:
            Balloon(widget, text=help_text, width=350)
        self.rt_overlay_position_y.bind("<Key>", self.save_settings_delayed)
        self.rt_overlay_position_x.bind("<Key>", self.save_settings_delayed)
        # Disable overlay when not in match
        self.rt_overlay_disable = tk.BooleanVar()
        self.rt_overlay_disable_checkbox = ttk.Checkbutton(
            self.rt_frame, text="Hide overlay when not in a GSF match", variable=self.rt_overlay_disable,
            command=self.save_settings)
        # Experimental overlay
        self.rt_overlay_experimental = tk.BooleanVar()
        self.rt_overlay_experimental_checkbox = ttk.Checkbutton(
            self.rt_frame, text="Enable experimental high-performance overlay",
            variable=self.rt_overlay_experimental)
        # EventOverlay
        self.rt_event_overlay = tk.BooleanVar()
        self.rt_event_overlay_checkbox = ttk.Checkbutton(
            self.rt_frame, text="Enable EventOverlay (bèta)", variable=self.rt_event_overlay,
            command=self.save_settings)
        Balloon(
            self.rt_event_overlay_checkbox,
            text="The EventOverlay shows the last few events in the CombatLog in a certain set of categories. This "
                 "feature can be useful for streamers to indicate the enemy weapons or other non-obvious events.")
        # EventOverlay position
        self.rt_event_position_frame = ttk.Frame(self.rt_frame)
        self.rt_event_position_label = ttk.Label(
            self.rt_event_position_frame, text="EventOverlay position:")
        self.rt_event_position_x_label = ttk.Label(self.rt_event_position_frame, text="X Coordinate:")
        self.rt_event_position_x = ttk.Entry(self.rt_event_position_frame, width=4)
        self.rt_event_position_y_label = ttk.Label(self.rt_event_position_frame, text="Y Coordinate:")
        self.rt_event_position_y = ttk.Entry(self.rt_event_position_frame, width=4)
        self.rt_event_position_y.bind("<Key>", self.save_settings_delayed)
        self.rt_event_position_x.bind("<Key>", self.save_settings_delayed)
        # RealTimeParser Sleep
        self.rt_sleep = tk.BooleanVar()
        self.rt_sleep_checkbox = ttk.Checkbutton(
            self.rt_frame, text="RealTimeParser sleep", variable=self.rt_sleep)
        Balloon(self.rt_sleep_checkbox,
                text="Raises the latency of the RealTimeParser event detection by limiting the parser to two parsing "
                     "cycles per second but reduces CPU and IO usage significantly.")
        # RGB Lighting Effects
        self.rt_rgb = tk.BooleanVar()
        self.rt_rgb_checkbox = ttk.Checkbutton(
            self.rt_frame, text="Enable RGB Keyboard Lighting Effects (bèta)",
            variable=self.rt_rgb)
        Balloon(self.rt_rgb_checkbox, text="Not all keyboards are supported. Support depends on the "
                                           "rgbkeyboards package, which may contain bugs and thus"
                                           "cause errors.")

        """
        Screen parsing settings
        """
        self.sc_label = ttk.Label(
            self.frame.interior, text="Screen Parsing", font=("default", 13, "bold"), justify=tk.LEFT)
        # Screen parsing enabled
        self.sc_enabled = tk.BooleanVar()
        self.sc_checkbox = ttk.Checkbutton(
            self.sc_frame, text="Enable screen parsing", variable=self.sc_enabled, command=self.save_settings)
        # Screen parsing overlay
        self.sc_overlay = tk.BooleanVar()
        self.sc_overlay_checkbox = ttk.Checkbutton(
            self.sc_frame, text="Enable screen parsing overlay", variable=self.sc_overlay,
            command=self.save_settings)
        # Screen parsing features
        self.sc_features_label = ttk.Label(self.sc_frame, text="Features enabled for screen parsing:")
        self.sc_features = [
            "Tracking penalty", "Ship health", "Mouse and Keyboard", "Spawn Timer",
            "MiniMap Location", "Map and match type", "Match score", "Pointer Parsing"
        ]
        beta = ["MiniMap Location", "Spawn Timer", "Map and match type", "Match score", "Pointer Parsing"]
        self.sc_checkboxes = OrderedDict()
        self.sc_variables = {}
        for feature in self.sc_features:
            self.sc_variables[feature] = tk.BooleanVar()
            text = feature if feature not in beta else "{} (bèta)".format(feature)
            self.sc_checkboxes[feature] = ttk.Checkbutton(
                self.sc_frame, text=text, variable=self.sc_variables[feature], command=self.save_settings)
        # Dynamic Window Location Support
        self.sc_dynamic_window = tk.BooleanVar()
        self.sc_dynamic_window_checkbox = ttk.Checkbutton(
            self.sc_frame, text="Enable Dynamic SWTOR Window Location Support (bèta)", command=self.save_settings,
            variable=self.sc_dynamic_window)
        Balloon(
            self.sc_dynamic_window_checkbox,
            text="Dynamic SWTOR Window Location Support enables routines that makes GUI Parsing and thus Screen "
                 "Parsing work when SWTOR runs in Windowed mode. This introduces additional overhead, as the location "
                 "of the SWTOR window is determined every Screen Parsing cycle.")

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
        color_toplevel = EventColors(self.main_window)
        color_toplevel.grid_widgets()
        color_toplevel.focus_set()
        self.wait_window(color_toplevel)
        self.focus_set()

    def set_directory_dialog(self):
        """
        Open a tkFileDialog to ask the user for the directory of the CombatLogs
        so the user does not have to enter the full path manually.
        """
        directory = filedialog.askdirectory(
            initialdir=self.pa_path.get(), mustexist=True, parent=self.main_window,
            title="GSF Parser: Choosing directory")
        if directory is None or directory == "" or not os.path.exists(directory):
            return
        self.pa_path.set(directory)

    def grid_widgets(self):
        """Configure widgets in grid geometry manager"""
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
        self.pa_label.grid(row=2, column=0, **padding_header, **sticky_default)
        self.pa_frame.grid(row=3, column=0, **padding_frame, **sticky_default)
        # CombatLogs path
        self.pa_path_label.grid(row=0, column=0, **padding_label, **sticky_default)
        self.pa_path_entry.grid(row=0, column=1, **padding_default, **sticky_default)
        self.pa_path_button.grid(row=0, column=2, **padding_default, **sticky_button)

        """
        Sharing settings
        """
        self.sh_label.grid(row=4, column=0, **padding_header, **sticky_default)
        self.sh_frame.grid(row=5, column=0, **padding_frame, **sticky_default)
        self.sh_enable_checkbox.grid(row=1, column=0, **padding_label, **sticky_default)
        self.sh_tag_label.grid(row=2, column=0, **padding_label, **sticky_default)
        self.sh_tag_entry.grid(row=2, column=1, **padding_default, **sticky_default)
        self.sh_auth_label.grid(row=3, column=0, **padding_label, **sticky_default)
        self.sh_auth_entry.grid(row=3, column=1, **padding_default, **sticky_default)
        self.sh_address_label.grid(row=5, column=0, **padding_label, **sticky_default)
        self.sh_host_entry.grid(row=5, column=1, **padding_default, **sticky_default)
        self.sh_port_entry.grid(row=5, column=2, **padding_default, **sticky_default)

        self.sh_host_entry.bind("<Key>", self.save_settings_delayed)
        self.sh_port_entry.bind("<Key>", self.save_settings_delayed)
        self.sh_auth_entry.bind("<Key>", self.save_settings_delayed)
        self.sh_tag_entry.bind("<Key>", self.save_settings_delayed)

        """
        RealTime settings
        """
        # General
        self.rt_label.grid(row=6, column=0, **padding_header, **sticky_default)
        self.rt_frame.grid(row=7, column=0, **padding_frame, **sticky_default)
        # Enable real-time overlay
        self.rt_overlay_enabled_checkbox.grid(row=0, column=0, **padding_label, **sticky_button, **checkbox)
        # Overlay text color
        self.rt_overlay_text_color_label.grid(row=1, column=0, **padding_label, **sticky_default)
        self.rt_overlay_text_color_dropdown.grid(row=1, column=1, **padding_default, **sticky_button)
        # Overlay position
        self.rt_overlay_position_frame.grid(row=2, column=0, columnspan=4, **padding_label, **sticky_default)
        self.rt_overlay_position_label.grid(row=0, column=0, padx=0, pady=(0, 5), **sticky_default)
        self.rt_overlay_position_x_label.grid(row=1, column=0, **padding_label, **sticky_default)
        self.rt_overlay_position_x.grid(row=1, column=1, **padding_default, **sticky_default)
        self.rt_overlay_position_y_label.grid(row=2, column=0, **padding_label, **sticky_default)
        self.rt_overlay_position_y.grid(row=2, column=1, **padding_default, **sticky_default)
        # Disable overlay when not in match
        self.rt_overlay_disable_checkbox.grid(row=3, column=0, **padding_label, **sticky_default, **checkbox)
        # Experimental Win32 Overlay
        self.rt_overlay_experimental_checkbox.grid(row=4, column=0, **padding_label, **sticky_default, **checkbox)
        # EventOverlay
        self.rt_event_overlay_checkbox.grid(row=5, column=0, **padding_label, **sticky_default, **checkbox)
        # EventOverlay Position
        self.rt_event_position_frame.grid(row=6, column=0, columnspan=4, **padding_label, **sticky_default)
        self.rt_event_position_label.grid(row=0, column=0, padx=0, pady=(0, 5), **sticky_default)
        self.rt_event_position_x_label.grid(row=1, column=0, **padding_label, **sticky_default)
        self.rt_event_position_x.grid(row=1, column=1, **padding_default, **sticky_default)
        self.rt_event_position_y_label.grid(row=2, column=0, **padding_label, **sticky_default)
        self.rt_event_position_y.grid(row=2, column=1, **padding_default, **sticky_default)
        # RealTimeParser sleep
        self.rt_sleep_checkbox.grid(row=7, column=0, **padding_label, **sticky_button)
        # RGB Effects
        self.rt_rgb_checkbox.grid(row=8, column=0, **padding_label, **sticky_button)
        """
        Screen parsing settings
        """
        # General
        self.sc_label.grid(row=8, column=0, **padding_header, **sticky_default)
        self.sc_frame.grid(row=9, column=0, **padding_frame, **sticky_default)
        # Screen parsing enabled
        self.sc_checkbox.grid(row=0, column=0, **padding_label, **sticky_default, **checkbox)
        # Screen parsing features
        self.sc_features_label.grid(row=2, column=0, **padding_label, **sticky_default)
        row = 3
        for feature in self.sc_checkboxes.values():
            feature.grid(row=row, column=0, padx=(80, 5), pady=(0, 5), **sticky_default)
            row += 1
        # Screen parsing overlay
        self.sc_overlay_checkbox.grid(row=row, column=0, **padding_label, **sticky_default, **checkbox)
        # Screen Dynamic Window Location
        self.sc_dynamic_window_checkbox.grid(row=row+1, column=0, **padding_label, **sticky_default, **checkbox)

    def update_settings(self):
        """
        Read the settings from the settings_obj in the variables
        module and update the settings shown in the GUI accordingly.
        """
        """
        GUI settings
        """
        self.gui_check_updates.set(settings["misc"]["autoupdate"])
        self.gui_event_colors_type.set(settings["gui"]["event_colors"])
        self.gui_event_colors_scheme.set(settings["gui"]["event_scheme"].capitalize())
        self.gui_faction.set(settings["gui"]["faction"].capitalize())
        self.gui_debug_window.set(settings["gui"]["debug"])
        """
        Parsing Settings
        """
        self.pa_path.set(settings["parsing"]["path"])
        """
        Sharing Settings
        """
        self.sh_enable.set(settings["sharing"]["enabled"])
        self.sh_tag.set(settings["sharing"]["discord"])
        self.sh_auth.set(settings["sharing"]["auth"])
        self.sh_host.set(settings["sharing"]["host"])
        self.sh_port.set(settings["sharing"]["port"])
        """
        Real-time Settings
        """
        self.rt_overlay_enabled.set(settings["realtime"]["overlay"])
        self.rt_overlay_disable.set(settings["realtime"]["overlay_when_gsf"])
        # Overlay position
        self.rt_overlay_position_x.delete(0, tk.END)
        self.rt_overlay_position_y.delete(0, tk.END)
        x, y = settings["realtime"]["overlay_position"].split("y")
        self.rt_overlay_position_x.insert(tk.END, x[1:])
        self.rt_overlay_position_y.insert(tk.END, y)
        self.rt_overlay_text_color.set(settings["realtime"]["overlay_text"].capitalize())
        # EventOverlay
        self.rt_event_overlay.set(settings["realtime"]["event_overlay"])
        self.rt_event_position_x.delete(0, tk.END)
        self.rt_event_position_y.delete(0, tk.END)
        x, y = settings["realtime"]["event_location"].split("y")
        self.rt_event_position_x.insert(tk.END, x[1:])
        self.rt_event_position_y.insert(tk.END, y)
        self.rt_sleep.set(settings["realtime"]["sleep"])
        self.rt_rgb.set(settings["realtime"]["rgb"])
        """
        Screen Parsing settings
        """
        self.sc_enabled.set(settings["screen"]["enabled"])
        self.sc_overlay.set(settings["screen"]["overlay"])
        for feature in self.sc_features:
            self.sc_variables[feature].set(feature in settings["screen"]["features"])
        self.sc_dynamic_window.set(settings["screen"]["window"])
        """
        Widget states
        """
        if get_screen_resolution() not in timer_boxes:
            self.sc_checkboxes["Spawn Timer"].configure(state=tk.DISABLED)
            Balloon(
                self.sc_checkboxes["Spawn Timer"],
                text="Your monitor resolution is not supported by this feature. If you would like "
                     "for your resolution to be supported, please send RedFantom a screenshot of the "
                     "unaltered user interface shown before the start of a match.")
        if sys.platform == "linux":
            self.rt_overlay_experimental.set(False)
            self.rt_overlay_experimental_checkbox.config(state=tk.DISABLED)
            Balloon(self.rt_overlay_experimental_checkbox,
                    text="This feature is only available on Windows due to API differences.")
        return

    def save_settings(self, *args):
        """
        Save the settings found in the widgets of the settings to the
        settings_obj in the variables module
        Some settings are checked before the writing occurs
        """
        if self.check_settings() is False:
            self.update_settings()
            return
        print("[MainWindow] Saving settings")
        dictionary = {
            "misc": {
                "version": settings["misc"]["version"],
                "autoupdate": self.gui_check_updates.get()
            },
            "gui": {
                "event_colors": self.gui_event_colors_type.get(),
                "event_scheme": self.gui_event_colors_scheme.get(),
                "faction": self.gui_faction.get(),
                "debug": self.gui_debug_window.get()
            },
            "parsing": {
                "path": self.pa_path.get(),
            },
            "realtime": {
                "overlay": self.rt_overlay_enabled.get(),
                "overlay_position": "x{}y{}".format(
                    self.rt_overlay_position_x.get(), self.rt_overlay_position_y.get()),
                "overlay_when_gsf": self.rt_overlay_disable.get(),
                "overlay_text": self.rt_overlay_text_color.get(),
                "overlay_experimental": self.rt_overlay_experimental.get(),
                "event_overlay": self.rt_event_overlay.get(),
                "event_location": "x{}y{}".format(
                    self.rt_event_position_x.get(), self.rt_event_position_y.get()),
                "realtime": self.rt_sleep.get(),
                "rgb": self.rt_rgb.get()
            },
            "screen": {
                "enabled": self.sc_enabled.get(),
                "overlay": self.sc_overlay.get(),
                "features": [key for key, value in self.sc_variables.items() if value.get() is True],
                "window": self.sc_dynamic_window.get()
            },
            "sharing": {
                "enabled": self.sh_enable.get(),
                "host": self.sh_host.get(),
                "port": int(self.sh_port.get()),
                "discord": self.sh_tag.get(),
                "auth": self.sh_auth.get()
            }
        }
        settings.write_settings(dictionary)
        self.update_settings()
        colors.set_scheme(self.gui_event_colors_scheme.get())
        self.after_id = None

    def save_settings_delayed(self, *args):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        self.after_id = self.after(2000, self.save_settings)

    def check_settings(self):
        """Check if the settings entered by the user are valid."""
        # Parsing path
        if not os.path.exists(self.pa_path.get()):
            messagebox.showerror("Error", "The CombatLogs folder path entered is not valid.")
            return False
        # Overlay position
        x = self.rt_overlay_position_x.get()
        y = self.rt_overlay_position_y.get()
        if not x.isdigit() or not y.isdigit():
            messagebox.showerror("Error", "The coordinates entered for the real-time overlay are not valid.")
            return False
        # EventOverlay Position
        x, y = self.rt_event_position_x.get(), self.rt_event_position_y.get()
        if not x.isdigit() or not y.isdigit():
            messagebox.showerror("Error", "The coordinates entered for the EventOverlay are not valid.")
            return False
        # Sharing settings
        if not self.sh_port.get().isdigit():
            messagebox.showerror("Error", "The port number entered for Discord Sharing is invalid.")
        if not DiscordClient.validate_tag(self.sh_tag.get()) and not self.sh_tag.get() == "":
            messagebox.showerror("Error", "Invalid Discord tag entered. The only accepted format is:\n\n"
                                          "@Name#0000")
            return False
        if len(self.sh_auth.get()) > 0 and not self.sh_auth.get().isdigit():
            messagebox.showerror("Error", "Invalid Discord Sharing authentication code entered.")
            return False
        return True
