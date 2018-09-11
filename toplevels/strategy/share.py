"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import sys
# UI Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkwidgets import CheckboxTreeview
# Project Modules
from widgets.general.snaptoplevel import SnapToplevel

Parent = SnapToplevel if sys.platform == "win32" else tk.Toplevel


class StrategyShareToplevel(Parent):
    """
    Toplevel to display a list of strategy with checkboxes to allow
    selecting which should be shared.
    """
    def __init__(self, master, client, database, strategy_frame, **kwargs):
        """
        :param master: master widget
        :param client: network.strategy.client.StrategyClient
        :param database: results.strategies.StrategyDataBase
        :param strategy_frame: frames.strategy.StrategyFrame
        :param kwargs: SnapToplevel keyword arguments
        """
        resizable = kwargs.pop("resizable", False)
        self._client = client
        self._database = database
        self._frame = strategy_frame
        Parent.__init__(self, master, **kwargs)
        self.wm_title("GSF Parser: Strategy Sharing")
        self.wm_resizable(resizable, resizable)
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
