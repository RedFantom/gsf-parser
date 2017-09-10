# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview, SnapToplevel
# Own modules
from parsing.strategies import StrategyDatabase
from tools.strategy_client import Client


class StrategyShareToplevel(SnapToplevel):
    """
    Toplevel to display a list of strategies with checkboxes to allow selecting which should be shared.
    """
    def __init__(self, master, client, database, strategy_frame, **kwargs):
        if not isinstance(database, StrategyDatabase) or not isinstance(client, Client):
            raise ValueError()
        self._client = client
        self._database = database
        self._frame = strategy_frame
        SnapToplevel.__init__(self, master, **kwargs)
        self.tree = CheckboxTreeview(master=self)
        for strategy in sorted(self._database.keys()):
            self.tree.insert("", tk.END, iid=strategy, text=strategy)
        self.tree.column("#0", width=115)
        self.tree.heading("#0", text="Strategy")
        self.tree.config(show=("headings", "tree"))
        self.grid_widgets()

    def grid_widgets(self):
        self.tree.grid()


