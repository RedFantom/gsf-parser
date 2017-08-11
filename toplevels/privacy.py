# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
# Own modules
import variables


class Privacy(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        privacy = variables.client_obj.get_privacy()
        privacy_listbox = tk.Listbox(self, height=10, width=30)
        privacy_listbox.pack(side=tk.LEFT)
        privacy_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=privacy_listbox.yview)
        privacy_listbox.config(yscrollcommand=privacy_scroll.set)
        if privacy == -1:
            self.destroy()
            return
        try:
            privacy_list = list(privacy)
        except:
            tkinter.messagebox.showerror("Error", "Data in privacy statement received is not valid.")
            return
        index = 0
        for line in privacy_list:
            privacy_listbox.insert(0, line)
            index += 1
