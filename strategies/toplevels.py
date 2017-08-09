# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from strategies.strategies import StrategyDatabase, Strategy
from tkinter import messagebox, filedialog
from ttkwidgets.frames import ScrolledFrame
import _pickle as pickle
from strategies.map import Map


class AddStrategy(tk.Toplevel):
    maps = {
        "Kuat Mesas DOM": ("dom", "km"),
        "Lost Shipyards DOM": ("dom", "ls"),
        "Denon Exosphere DOM": ("dom", "de"),
        "Kuat Mesas TDM": ("tdm", "km"),
        "Lost Shipyards TDM": ("tdm", "ls")
    }

    def __init__(self, *args, **kwargs):
        self.db = kwargs.pop("db", StrategyDatabase())
        self.callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        self.title("GSF Strategy Planner: Add Strategy")
        self.name_entry = ttk.Entry(self, width=28, font=("default", 11))
        self.name_entry.insert(0, "Strategy name...")
        self.name_entry.bind("<Button-1>", self.entry_callback)
        self.map = tk.StringVar()
        self.map_dropdown = ttk.OptionMenu(self, self.map, *("Select a map",
                                                             "Kuat Mesas DOM",
                                                             "Lost Shipyards DOM",
                                                             "Denon Exosphere DOM",
                                                             "Kuat Mesas TDM",
                                                             "Lost Shipyards TDM"))
        print(self.map_dropdown["style"])
        self.add_button = ttk.Button(self, text="Add", command=self.add)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.grid_widgets()

    def grid_widgets(self):
        self.name_entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.map_dropdown.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=5, pady=(0, 5))
        self.add_button.grid(row=2, column=0, sticky="nswe", padx=5, pady=(0, 5))
        self.cancel_button.grid(row=2, column=1, sticky="nswe", padx=(0, 5), pady=(0, 5))

    def entry_callback(self, event):
        if self.name_entry.get() == "Strategy name...":
            self.name_entry.delete(0, tk.END)
        return

    def add(self):
        name = self.name_entry.get()
        print("Saving strategy {0}...".format(name))
        if name in self.db:
            messagebox.showinfo("Info", "Please select a name that is not yet in use.")
            return
        if self.map.get() not in self.maps:
            messagebox.showinfo("Info", "Please select a map.")
            return
        self.db[name] = Strategy(name, self.maps[self.map.get()])
        self.db.save_database()
        if callable(self.callback):
            self.callback()
        self.destroy()


class AddPhase(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add new phase")
        self._entry = ttk.Entry(self, width=30)
        self._entry.bind("<Return>", self.add_phase)
        self._cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self._add_button = ttk.Button(self, text="Add", command=self.add_phase)
        self.grid_widgets()

    def grid_widgets(self):
        self._entry.grid(row=0, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self._cancel_button.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self._add_button.grid(row=1, column=1, sticky="nswe", padx=5, pady=5)

    def add_phase(self, *args):
        if callable(self._callback):
            self._callback(self._entry.get())
        self.destroy()


class SettingsToplevel(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop("callback", None)
        self.master = kwargs.pop("master")
        self.list = self.master.list
        self.new_strategy = self.master.new_strategy
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Settings")
        self.menu = tk.Menu(self)
        # File menu
        self.filemenu = tk.Menu(self, tearoff=False)
        self.filemenu.add_command(label="New", command=self.new_strategy)
        self.filemenu.add_command(label="Open", command=self.open_strategy)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save", command=self.save_strategy)
        self.filemenu.add_command(label="Save as", command=self.save_strategy_as)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        # Edit menu
        self.editmenu = tk.Menu(self, tearoff=False)
        self.editmenu.add_command(label="Export database", command=self._export)
        self.editmenu.add_command(label="Import database", command=self._import)
        self.menu.add_cascade(label="Edit", menu=self.editmenu)
        self.config(menu=self.menu)

        self.scrolled_frame = ScrolledFrame(self)
        self.interior = self.scrolled_frame.interior
        # Server settings section
        self.server_section = ttk.Frame(self.interior)
        self.server_header = ttk.Label(self.server_section, text="Server settings", justify=tk.LEFT,
                                       font=("default", 11))
        self.server_address_entry = ttk.Entry(self.server_section, width=15)
        self.server_port_entry = ttk.Entry(self.server_section, width=6)
        self.server_button = ttk.Button(self.server_section, text="Start server", command=self.start_server, width=15)

        # Client settings section
        self.client_section = ttk.Frame(self.interior)
        self.client_header = ttk.Label(self.client_section, text="Client settings", justify=tk.LEFT,
                                       font=("default", 11))
        self.client_address_entry = ttk.Entry(self.client_section, width=15)
        self.client_port_entry = ttk.Entry(self.client_section, width=6)
        self.client_button = ttk.Button(self.client_section, text="Connect to server", width=15,
                                        command=self.connect_client)

        self.grid_widgets()

    def grid_widgets(self):
        self.scrolled_frame.grid()
        self.server_section.grid(row=1, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_header.grid(row=1, column=1, sticky="nw", columnspan=3, padx=5, pady=(0, 5))
        self.server_address_entry.grid(row=2, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_port_entry.grid(row=2, column=2, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_address_entry.insert(tk.END, "address")
        self.server_port_entry.insert(tk.END, "port")
        self.server_button.grid(row=2, column=3, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_section.grid(row=2, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_header.grid(row=1, column=1, sticky="nw", padx=(5, 0), pady=(0, 5), columnspan=3)
        self.client_address_entry.grid(row=2, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_port_entry.grid(row=2, column=2, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_button.grid(row=2, column=3, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_address_entry.insert(tk.END, "address")
        self.client_port_entry.insert(tk.END, "port")

    def start_server(self):
        pass

    def connect_client(self):
        pass

    def open_strategy(self):
        file_name = filedialog.askopenfilename(filetypes=[".str", ".bin"], defaultextension=".str",
                                               title="GSF Strategy Manager: Open a strategy")
        if file_name == "" or file_name is None:
            return
        with open(file_name, "rb") as fi:
            strategy = pickle.load(fi)
        self.list.db[strategy["name"]] = strategy
        self.list.update_tree()

    def save_strategy(self):
        self.save_strategy_as()

    def save_strategy_as(self):
        file_name = filedialog.asksaveasfilename(filetypes=[".str", ".bin"], defaultextension=".str",
                                                 title="GSF Strategy Manager: Save a strategy")
        if file_name == "" or file_name is None:
            return
        strategy = self.list.db[self.list.selected_strategy]
        with open(file_name, "wb") as fo:
            pickle.dump(strategy, fo)

    def save_strategy_database(self):
        self.list.db.save_database()

    def _import(self):
        file_name = filedialog.askopenfilename(filetypes=[".db"], defaultextension=".db",
                                               title="GSF Strategy Manger: Import a database")
        if file_name == "" or file_name is None:
            return
        self.list.db.merge_database(StrategyDatabase(file_name=file_name))
        self.list.update_tree()

    def _export(self):
        file_name = filedialog.asksaveasfilename(filetypes=[".db"], defaultextension=".db",
                                                 title="GSF Strategy Manager: Export the database")
        if file_name == "" or file_name is None:
            return
        self.list.db.save_database_as(file_name)


class MapToplevel(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self.frame = kwargs.pop("frame")
        if not self.frame:
            raise ValueError("No parent frame passed as argument")
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.map = Map(self, moveitem_callback=self.move_item_phase,
                       additem_callback=self.add_item_to_phase, delitem_callback=self.del_item_phase,
                       canvaswidth=768, canvasheight=768)
        self.map.grid()
        self.frame.in_map = self.frame.map
        self.frame.in_map.set_readonly(True)
        self.frame.map = self.map
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)
        self.title("GSF Strategy Manager: Enlarged map")

    def move_item_phase(self, *args, **kwargs):
        self.frame.list.move_item_phase(*args, **kwargs)
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase])
        self.frame.list.tree.column("#0", width=150)
        self.frame.grid_widgets()

    def add_item_to_phase(self, *args, **kwargs):
        self.frame.list.add_item_to_phase(*args, **kwargs)
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase])
        self.frame.list.tree.column("#0", width=150)

    def del_item_phase(self, item, rectangle, text):
        print("Deleting item {0}".format(text))
        del self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase][text]
        self.frame.list.db.save_database()
        if self.frame.list.selected_phase is not None:
            self.frame.in_map.update_map(
                self.frame.list.db[self.frame.list.selected_strategy][self.frame.list.selected_phase])

    def close(self):
        self.frame.map = self.frame.in_map
        self.frame.map.set_readonly(False)
        self.frame.in_map = None
        self.destroy()
