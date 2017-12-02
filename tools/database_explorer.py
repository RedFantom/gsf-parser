# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
# Own modules
from parsing.filehandler import FileHandler


class DatabaseExplorer(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.wm_title("GSF Parser: Database Explorer")
        self.data = FileHandler.get_data_dictionary()
        self.tree = ttk.Treeview(self, height=15)
        self.tree.config(show=("headings", "tree"), columns=())
        self.tree.heading("#0", text="List")
        self.tree.column("#0", width=400)
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscrollcommand=self.scroll.set)
        self.refresh_button = ttk.Button(self, text="Refresh", command=self.update_tree)
        self.bind("<F5>", self.update_tree)
        self.update_tree()
        self.grid_widgets()

    def grid_widgets(self):
        self.tree.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)
        self.scroll.grid(row=1, column=2, sticky="ns", padx=(0, 5), pady=5)
        self.refresh_button.grid(row=2, column=1, columnspan=2, sticky="nswe", padx=5, pady=(0, 5))

    def update_tree(self, *args):
        self.tree.delete(*self.tree.get_children(""))
        self.data = FileHandler.get_data_dictionary()
        for file, data_file in self.data.items():
            if file == "" or file is None:
                continue
            self.tree.insert("", tk.END, iid=file, text=file)
            for match, data_match in data_file.items():
                if match is None:
                    continue
                match_string = match.strftime("%H:%M:%S")
                self.tree.insert(file, tk.END, iid="{}+{}".format(file, match_string), text=match_string)
                for spawn, data_spawn in data_match.items():
                    if spawn is None:
                        continue
                    spawn_string = spawn.strftime("%H:%M:%S")
                    self.tree.insert("{}+{}".format(file, match_string), tk.END,
                                     iid="{}+{}+{}".format(file, match_string, spawn_string),
                                     text=spawn_string)
                    for data_type, special_data in data_spawn.items():
                        if data_type is None:
                            continue
                        self.tree.insert("{}+{}+{}".format(file, match_string, spawn_string), tk.END,
                                         iid="{}+{}+{}+{}".format(file, match_string, spawn_string, data_type),
                                         text=data_type)
                        for moment in sorted(special_data.keys()):
                            if moment is None:
                                continue
                            data_collected = special_data[moment]
                            parent = self.tree.insert("{}+{}+{}+{}".format(file, match_string, spawn_string, data_type),
                                                      tk.END,
                                                      text=moment.strftime("%H:%S"))
                            self.tree.insert(parent, tk.END, text=str(data_collected))
        return


if __name__ == '__main__':
    DatabaseExplorer().mainloop()
