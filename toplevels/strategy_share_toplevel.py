# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        self.wm_title("GSF Parser: Strategy Sharing")
        # Configure the Treeview
        self.tree = CheckboxTreeview(master=self, height=16)
        self.tree.column("#0", width=200)
        self.tree.heading("#0", text="Strategy")
        self.tree.config(show=("headings", "tree"))
        self.scroll_bar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscrollcommand=self.scroll_bar.set)
        self.update_strategy_tree()
        self.share_button = ttk.Button(self, text="Share Strategies", command=self.share_strategies)
        self.grid_widgets()

    def grid_widgets(self):
        self.tree.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)
        self.scroll_bar.grid(row=1, column=2, sticky="ns", padx=(0, 5), pady=5)
        self.share_button.grid(row=2, column=1, columnspan=2, sticky="nswe", padx=5, pady=(0, 5))

    def share_strategies(self):
        for strategy in self.strategies_to_share:
            self._client.send_strategy(strategy)
        messagebox.showinfo("Info", "Selected Strategies sent.")

    def update_strategy_tree(self):
        self.tree.delete(*self.tree.get_children(""))
        for strategy in sorted(self._database.keys()):
            self.tree.insert("", tk.END, iid=strategy, text=strategy)

    @property
    def strategies_to_share(self):
        for strategy in self.tree.get_checked():
            yield self._database[strategy]
