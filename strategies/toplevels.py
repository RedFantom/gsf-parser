# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from strategies.strategies import StrategyDatabase, Strategy
from tkinter import messagebox
from ttkwidgets.frames import ScrolledFrame
from ttkwidgets.font import FontSelectFrame
from ttkwidgets.color import askcolor
from tkinter import filedialog
import _pickle as pickle


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


class AddItem(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        self.callback = kwargs.pop("callback", None)
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("GSF Strategy Planner: Add Item")
        self.attributes("-topmost", True)
        self.header_label = ttk.Label(self, text="Add a new item", font=("default", 12), justify=tk.LEFT)
        self.text_header = ttk.Label(self, text="Item text", font=("default", 11), justify=tk.LEFT)
        self.text = tk.StringVar()
        self.text_entry = ttk.Entry(self, textvariable=self.text)
        self.background_color = tk.StringVar()
        self.background_color.set("#ffffff")
        self.background_color_header = ttk.Label(self, text="Item background", font=("default", 11), justify=tk.LEFT)
        self.background_color_entry = tk.Entry(self, textvariable=self.background_color)
        self.background_color_button = ttk.Button(self, text="Choose color", command=self.update_color)
        self.font_header = ttk.Label(self, text="Item font", font=("default", 11), justify=tk.LEFT)
        self.font_select_frame = FontSelectFrame(self)
        self.add_button = ttk.Button(self, text="Add item", command=self.add_item)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.grid_widgets()

    def grid_widgets(self):
        # self.header_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.text_header.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.text_entry.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.background_color_header.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.background_color_entry.grid(row=6, column=0, sticky="nswe", padx=5, pady=5)
        self.background_color_button.grid(row=6, column=1, padx=5, pady=5)
        self.font_header.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.font_select_frame.grid(row=8, column=0, columnspan=3, sticky="nswe", padx=5, pady=5)
        self.add_button.grid(row=9, column=1, sticky="nswe", padx=5, pady=5)
        self.cancel_button.grid(row=9, column=0, sticky="nswe", padx=5, pady=5)

    def add_item(self):
        if callable(self.callback):
            if not self.font_select_frame._family:
                print("No font family selected.")
            font = self.font_select_frame.font if self.font_select_frame.font is not None else ("default", 12)
            if font == ("default", 12):
                print("Default font selected")
            self.callback(self.text.get(), font, color=self.background_color.get())
        self.destroy()

    def update_color(self):
        tuple, hex = askcolor()
        if not tuple or not hex:
            return
        self.background_color.set(hex)
        self.update_entry(tuple)

    def update_entry(self, color_tuple):
        red, green, blue = color_tuple
        self.background_color_entry.config(background=self.background_color.get(),
                                           foreground='#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186
                                           else "#ffffff")


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
