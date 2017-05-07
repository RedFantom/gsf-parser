# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import ttk
import Tkinter as tk


class SharingFrame(ttk.Frame):
    """
    A Frame to contain widgets to allow uploading of CombatLogs to the server
    and viewing leaderboards that keep track of individual player performance
    on different fronts. A connection to the server is required, and as the
    GSF Server is not done yet, this Frame is still empty.
    """

    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)
        self.label = ttk.Label(self, font=("Calibri", 40),
                               text="Coming soon!", justify=tk.CENTER)
        self.label.grid(sticky=tk.N + tk.S + tk.W + tk.E, padx=250, pady=150)
