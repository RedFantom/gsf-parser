# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import mtTkinter as tk
import ttk
import tkMessageBox
# Own modules
import vars
import overlay

class settings_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ### LAY-OUT ###
        # TODO Change the settings frame to a canvas in order to make it scrollable
        ttk.Frame.__init__(self, root_frame)
        self.gui_frame = ttk.Frame(root_frame)
        self.entry_frame = ttk.Frame(root_frame)
        self.privacy_frame = ttk.Frame(root_frame)
        self.server_frame = ttk.Frame(root_frame)
        self.upload_frame = ttk.Frame(root_frame)
        self.realtime_frame = ttk.Frame(root_frame)
        self.save_frame = ttk.Frame(root_frame)
        self.license_frame = ttk.Frame(root_frame)
        self.main_window = main_window
        ### GUI SETTINGS ###
        # TODO Add more GUI settings including colours
        self.gui_label = ttk.Label(root_frame, text = "GUI settings", justify=tk.LEFT)
        self.style_label = ttk.Label(self.gui_frame, text = "\tParser style: ")
        self.style_options = []
        self.style = tk.StringVar()
        self.style.set(main_window.style.theme_use())
        for style in main_window.styles:
            self.style_options.append(ttk.Radiobutton(self.gui_frame, value = str(style), text = style, variable = self.style))
        ### PARSING SETTINGS ###
        self.parsing_label = ttk.Label(root_frame, text = "Parsing settings", justify=tk.LEFT)
        self.path_entry = ttk.Entry(self.entry_frame, width=75)
        self.path_entry_label = ttk.Label(self.entry_frame, text = "\tCombatLogs folder:")
        self.privacy_label = ttk.Label(self.privacy_frame, text = "\tConnect to server for player identification:")
        self.privacy_var = tk.BooleanVar()
        self.privacy_select_true = ttk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = True, text = "Yes")
        self.privacy_select_false = ttk.Radiobutton(self.privacy_frame, variable = self.privacy_var, value = False, text = "No")
        ### SHARING SETTINGS ###
        self.sharing_label = ttk.Label(root_frame, text = "Share settings", justify=tk.LEFT)
        self.server_label = ttk.Label(self.server_frame, text = "\tServer for sharing: ")
        self.server_address_entry = ttk.Entry(self.server_frame, width=35)
        self.server_colon_label = ttk.Label(self.server_frame, text = ":")
        self.server_port_entry = ttk.Entry(self.server_frame, width=8)
        self.auto_upload_label = ttk.Label(self.upload_frame, text="\tAuto-upload CombatLogs to the server:\t\t")
        self.auto_upload_var = tk.BooleanVar()
        self.auto_upload_false = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=False, text="No")
        self.auto_upload_true = ttk.Radiobutton(self.upload_frame, variable=self.auto_upload_var, value=True, text="Yes")
        ### REAL-TIME SETTINGS ###
        # TODO Add more colours for the overlay
        # TODO Add events view possibility to the overlay
        self.realtime_settings_label = ttk.Label(self.realtime_frame, text = "Real-time parsing settings")
        self.overlay_enable_label = ttk.Label(self.realtime_frame, text = "\tEnable overlay for real-time parsing: ")
        self.overlay_enable_radio_var = tk.BooleanVar()
        self.overlay_enable_radio_yes = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_enable_radio_var, value=True, text="Yes")
        self.overlay_enable_radio_no = ttk.Radiobutton(self.realtime_frame, variable=self.overlay_enable_radio_var, value=False, text="No")
        self.overlay_opacity_label = ttk.Label(self.realtime_frame, text = "\tOverlay opacity (between 0 and 1):")
        self.overlay_opacity_input = ttk.Entry(self.realtime_frame, width = 3)
        self.overlay_size_label = ttk.Label(self.realtime_frame, text = "\tOverlay window size: ")
        self.overlay_size_var = tk.StringVar()
        self.overlay_size_radio_big = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_size_var, value = "big", text = "Big")
        self.overlay_size_radio_small = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_size_var, value = "small", text = "Small")
        self.overlay_position_label = ttk.Label(self.realtime_frame, text = "\tPosition of the in-game overlay:")
        self.overlay_position_var = tk.StringVar()
        self.overlay_position_var.set(vars.set_obj.pos)
        self.overlay_position_radio_tl = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "TL", text =  "Top left")
        self.overlay_position_radio_bl = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "BL", text = "Bottom left")
        self.overlay_position_radio_tr = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "TR", text = "Top right")
        self.overlay_position_radio_br = ttk.Radiobutton(self.realtime_frame, variable = self.overlay_position_var, value = "BR", text = "Bottom right")
        ### MISC ###
        self.separator = ttk.Separator(root_frame, orient=tk.HORIZONTAL)
        self.save_settings_button = ttk.Button(self.save_frame, text="  Save  ", command=self.save_settings)
        self.discard_settings_button = ttk.Button(self.save_frame, text="Discard", command=self.discard_settings)
        self.default_settings_button = ttk.Button(self.save_frame, text="Defaults", command = self.default_settings)
        self.license_button = ttk.Button(self.license_frame, text="License", command=self.show_license)
        self.privacy_button = ttk.Button(self.license_frame, text = "Privacy statement for server", command=self.show_privacy)
        self.version_label = ttk.Label(self.license_frame, text="Version 2.0")
        self.update_label_var = tk.StringVar()
        self.update_label = ttk.Label(self.license_frame, textvariable=self.update_label_var)
        self.copyright_label = ttk.Label(self.license_frame, text = "Copyright (C) 2016 by RedFantom and Daethyra", justify=tk.LEFT)
        self.thanks_label = ttk.Label(self.license_frame, text = "Special thanks to Nightmaregale for bèta testing", justify=tk.LEFT)
        self.update_settings()

    def grid_widgets(self):
        ### GUI SETTINGS ###
        self.gui_label.grid(column = 0, row=0, sticky=tk.W)
        self.gui_frame.grid(column = 0, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        self.style_label.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        set_column = 0
        for radio in self.style_options:
            set_column += 1
            radio.grid(column=set_column, row=0,sticky=tk.N+tk.S+tk.W+tk.E)
        ### PARSING SETTINGS ###
        self.parsing_label.grid(column=0, row=2, sticky=tk.W)
        self.path_entry_label.grid(column=0, row=0, sticky=tk.W)
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
        self.overlay_size_label.grid(column = 0, row = 3, sticky = tk.W)
        self.overlay_size_radio_big.grid(column = 1, row = 3, sticky = tk.W)
        self.overlay_size_radio_small.grid(column = 2, row = 3, sticky = tk.W)
        self.overlay_position_label.grid(column = 0, row = 4, sticky = tk.W)
        self.overlay_position_radio_tl.grid(column = 1, row = 4, sticky = tk.W)
        self.overlay_position_radio_bl.grid(column = 2, row = 4, sticky = tk.W)
        self.overlay_position_radio_tr.grid(column = 3, row = 4, sticky = tk.W)
        self.overlay_position_radio_br.grid(column = 4, row = 4, sticky = tk.W)
        self.realtime_frame.grid(column = 0, row = 8, sticky=tk.N+tk.S+tk.W+tk.E)
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

    def update_settings(self):
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, vars.set_obj.cl_path)
        self.privacy_var.set(bool(vars.set_obj.auto_ident))
        self.server_address_entry.delete(0, tk.END)
        self.server_address_entry.insert(0, str(vars.set_obj.server_address))
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, int(vars.set_obj.server_port))
        self.auto_upload_var.set(bool(vars.set_obj.auto_upl))
        self.overlay_enable_radio_var.set(bool(vars.set_obj.overlay))
        self.overlay_opacity_input.delete(0, tk.END)
        self.overlay_opacity_input.insert(0, vars.set_obj.opacity)
        self.overlay_size_var.set(vars.set_obj.size)
        self.overlay_position_var.set(vars.set_obj.pos)

    def save_settings(self):
        print "[DEBUG] Save_settings called!"
        if str(self.style.get()) == vars.set_obj.style:
            reboot = False
        else:
            reboot = True
        vars.set_obj.write_set(cl_path=str(self.path_entry.get()), auto_ident=str(self.privacy_var.get()),
                               server_address=str(self.server_address_entry.get()), server_port=str(self.server_port_entry.get()),
                               auto_upl=str(self.auto_upload_var.get()), overlay=str(self.overlay_enable_radio_var.get()),
                               opacity=str(self.overlay_opacity_input.get()), size=str(self.overlay_size_var.get()), pos=str(self.overlay_position_var.get()),
                               style=str(self.style.get()))
        print self.style.get()
        self.update_settings()
        self.main_window.file_select_frame.add_files()
        if reboot:
            self.main_window.update_style()

    def discard_settings(self):
        self.update_settings()

    def default_settings(self):
        vars.set_obj.write_def()
        self.update_settings()

    @staticmethod
    def show_license():
        tkMessageBox.showinfo("License", "This program is licensed under the General Public License Version 3, by GNU. See LICENSE in the installation directory for more details")

    def show_privacy(self):
        if not vars.client_obj.INIT:
            tkMessageBox.showerror("The connection to the server was not initialized correctly.")
        overlay.privacy(self.main_window)
