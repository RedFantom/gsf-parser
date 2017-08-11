# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import os
import sys
# Own modules
from tools import utilities
import variables


class RealtimeOverlay(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.update_position()
        if sys.platform == "win32":
            try:
                with open(os.path.join(utilities.get_swtor_directory(), "swtor", "settings", "client_settings.ini"),
                          "r") as swtor:
                    if "D3DFullScreen = true" in swtor:
                        tkinter.messagebox.showerror("Error",
                                                     "The overlay cannot be shown with the current SWTOR settings. "
                                                     "Please set SWTOR to Fullscreen (windowed) in the Graphics "
                                                     "settings.")
            except IOError:
                tkinter.messagebox.showerror("Error",
                                             "The settings file for SWTOR cannot be found. Is SWTOR correctly "
                                             "installed?")
        print("[DEBUG] Setting overlay font to: ", (
            variables.settings_obj["realtime"]["overlay_tx_font"], variables.settings_obj["realtime"]["overlay_tx_size"]))
        if variables.settings_obj["realtime"]["size"] == "big":
            self.text_label = ttk.Label(self, text="Damage done:\nDamage taken:\nHealing "
                                                   "recv:\nSelfdamage:\nRecent enemies:\nSpawns:",
                                        justify=tk.LEFT, font=(variables.settings_obj["realtime"]["overlay_tx_font"],
                                                               int(variables.settings_obj["realtime"]["overlay_tx_size"])),
                                        foreground=variables.settings_obj["realtime"]["overlay_tx_color"],
                                        background=variables.settings_obj["realtime"]["overlay_bg_color"])
        elif variables.settings_obj["realtime"]["size"] == "small":
            self.text_label = ttk.Label(self, text="DD:\nDT:\nHR:\nSD:", justify=tk.LEFT,
                                        font=(variables.settings_obj["realtime"]["overlay_tx_font"],
                                              int(variables.settings_obj["realtime"]["overlay_tx_size"])),
                                        foreground=variables.settings_obj["realtime"]["overlay_tx_color"],
                                        background=variables.settings_obj["realtime"]["overlay_bg_color"])
        else:
            raise ValueError("Size setting not valid.")
        self.stats_var = tk.StringVar()
        self.stats_label = ttk.Label(self, textvariable=self.stats_var, justify=tk.RIGHT,
                                     font=(variables.settings_obj["realtime"]["overlay_tx_font"],
                                           int(variables.settings_obj["realtime"]["overlay_tx_size"])),
                                     foreground=variables.settings_obj["realtime"]["overlay_tx_color"],
                                     background=variables.settings_obj["realtime"]["overlay_bg_color"])
        self.text_label.pack(side=tk.LEFT)
        self.stats_label.pack(side=tk.RIGHT)
        self.configure(background=variables.settings_obj["realtime"]["overlay_bg_color"])
        self.wm_attributes("-transparentcolor", variables.settings_obj["realtime"]["overlay_tr_color"])
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", variables.settings_obj["realtime"]["opacity"])

    def update_position(self):
        if variables.settings_obj["realtime"]["size"] == "big":
            h_req = (int(variables.settings_obj["realtime"]["overlay_tx_size"]) * 1.6) * 6
            w_req = ((int(variables.settings_obj["realtime"]["overlay_tx_size"]) / 1.5) + 2) * (14 + 6)
        elif variables.settings_obj["realtime"]["size"] == "small":
            h_req = (int(variables.settings_obj["realtime"]["overlay_tx_size"]) * 1.6) * 4
            w_req = ((int(variables.settings_obj["realtime"]["overlay_tx_size"]) / 1.5) + 2) * (4 + 6)
        else:
            raise ValueError("Not a valid overlay size found.")
        if variables.settings_obj["realtime"]["pos"] == "TL":
            pos_c = "+0+0"
        elif variables.settings_obj["realtime"]["pos"] == "BL":
            pos_c = "+0+%s" % (int(variables.screen_h) - int(h_req))
        elif variables.settings_obj["realtime"]["pos"] == "TR":
            pos_c = "+%s+0" % (int(variables.screen_w) - int(w_req))
        elif variables.settings_obj["realtime"]["pos"] == "BR":
            pos_c = "+%s+%s" % (int(variables.screen_w) - int(w_req), int(variables.screen_h) - int(h_req))
        elif variables.settings_obj["realtime"]["pos"] == "UC":
            pos_c = "+0+%s" % int(0.25 * variables.screen_h)
        elif variables.settings_obj["realtime"]["pos"] == "NQ":
            pos_c = "+%s+%s" % (int(variables.screen_w * 0.25), int(variables.screen_h) - int(h_req))
        elif variables.settings_obj["realtime"]["pos"] == "UT":
            pos_c = "+%s+%s" % (int(variables.screen_w) - int(w_req),
                                variables.screen_h - int(0.75 * variables.screen_h))
        else:
            raise ValueError("vars.settings_obj.pos not valid")
        self.wm_geometry("%sx%s" % (int(w_req), int(h_req)) + pos_c)
        print("[DEBUG] Overlay position set to: ", "%sx%s" % (int(w_req), int(h_req)) + pos_c)
