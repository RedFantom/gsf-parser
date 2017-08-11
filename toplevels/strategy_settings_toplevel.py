# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import _pickle as pickle
from ttkwidgets.frames import ScrolledFrame
# Own modules
from parsing.strategies import StrategyDatabase
from server.strategy_server import Server
from tools.admin import run_as_admin, is_user_admin
from tools.strategy_client import Client
import variables


class SettingsToplevel(tk.Toplevel):
    """
    Toplevel that contains options to export Strategies, whole StrategyDatabases, or start up a server/connect to one
    for real-time Strategy sharing.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the toplevel with all its widgets and menus
        """
        self._callback = kwargs.pop("callback", None)
        self._disconnectcallback = kwargs.pop("disconnect_callback", None)
        self.frame = kwargs.pop("master")
        self.list = self.frame.list
        self.new_strategy = self.frame.list.new_strategy
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
        self.client_name_entry = ttk.Entry(self.client_section, width=15)
        self.client_role = tk.StringVar()
        self.client_role_dropdown = ttk.OptionMenu(self.client_section, self.client_role,
                                                   *("Choose role", "Master", "Client"))
        self.client_role.set("Client")
        self.client_header = ttk.Label(self.client_section, text="Client settings", justify=tk.LEFT,
                                       font=("default", 11))
        self.client_address_entry = ttk.Entry(self.client_section, width=15)
        self.client_port_entry = ttk.Entry(self.client_section, width=6)
        self.client_button = ttk.Button(self.client_section, text="Connect to server", width=15,
                                        command=self.connect_client)
        self.client = None
        self.server = None
        self.resizable(False, False)
        self.grid_widgets()

    def grid_widgets(self):
        """
        The usual function to put all the widgets in the correct place
        """
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
        self.client_name_entry.grid(row=2, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5), columnspan=2)
        self.client_role_dropdown.grid(row=2, column=3, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_address_entry.grid(row=3, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_port_entry.grid(row=3, column=2, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_button.grid(row=3, column=3, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.client_address_entry.insert(tk.END, "address")
        self.client_port_entry.insert(tk.END, "port")
        self.client_name_entry.insert(tk.END, "username")

    def start_server(self):
        """
        Start a new Strategy Server. User must be an admin user to start a server (as the binding to an address
        requires privileges to create a port in the Windows Firewall).
        """
        if not is_user_admin():
            self.destroy()
            variables.main_window.destroy()
            run_as_admin()
            exit()
        try:
            self.server = Server(self.server_address_entry.get(), int(self.server_port_entry.get()))
        except RuntimeError:
            messagebox.showerror("Error", "Starting the server failed due to a RuntimeError, which probably means that "
                                          "binding to the port and host name failed. If you did not expect this, "
                                          "please file a bug report in the GitHub repository and include any debug "
                                          "output.")
            return
        except ValueError:
            messagebox.showerror("Error", "The host and/or port values you have entered are not valid. Currently, only "
                                          "IP addresses or a blank value (binds to all available) are allowed as "
                                          "host value, and only ports lower than 9999 are allowed.")
            return

        self.protocol("WM_DELETE_WINDOW", self.destroy_redirect)
        self.server.start()
        self.server_button.config(text="Stop server", command=self.stop_server)
        self.client_address_entry.delete(0, tk.END)
        self.client_address_entry.insert(tk.END, self.server_address_entry.get())
        self.client_port_entry.delete(0, tk.END)
        self.client_port_entry.insert(tk.END, self.server_port_entry.get())
        self.client_role.set("Master")
        self.server_port_entry.config(state=tk.DISABLED)
        self.server_address_entry.config(state=tk.DISABLED)

    def stop_server(self):
        """
        Stop a running Strategy Server. Resets all widgets that were altered.
        """
        for _ in range(5):
            self.server.exit_queue.put(True)
        closing = ClosingToplevel()
        while self.server.is_alive():
            closing.update()
        closing.destroy()
        self.server_button.config(text="Start server", command=self.start_server)
        self.server_address_entry.config(state=tk.NORMAL)
        self.server_port_entry.config(state=tk.NORMAL)
        self.server = None
        if not self.client:
            self.protocol("WM_DELETE_WINDOW", self.destroy)

    def connect_client(self):
        """
        Create a new connection to a client
        """
        self.client = Client(self.client_address_entry.get(), int(self.client_port_entry.get()),
                             self.client_name_entry.get(), self.client_role.get(), self.list, self.login_callback,
                             self.frame.insert_callback, self.disconnect_client)
        if self.client.role.lower() == "client":
            print("Setting map to be readonly")
            self.frame.map.set_readonly(True)
            if self.frame.in_map:
                self.frame.in_map.set_readonly(True)
        else:
            print("Role is not 'client', but {0}, so not setting readonly".format(self.client.role.lower()))
        return

    def login_callback(self, success):
        """
        Callback for a newly created Client object to call to indicate whether logging into the server was successful.
        :param success: False if not successful, True if successful
        :return: None
        """
        if success:
            self.client_button.config(text="Disconnect", command=self.disconnect_client)
        else:
            self.client_button.config(text="Retry connection")
            return
        self.protocol("WM_DELETE_WINDOW", self.destroy_redirect)
        self.after(200, self.call_master_login_callback)
        self.client_name_entry.config(state=tk.DISABLED)
        self.client_role_dropdown.config(state=tk.DISABLED)
        self.client_address_entry.config(state=tk.DISABLED)
        self.client_port_entry.config(state=tk.DISABLED)

    def call_master_login_callback(self):
        """
        A delayed callback so the Client object is fully setup before it is passed back to the master StrategiesFrame
        for further processing (StrategiesFrame passes the object on to its child widgets).
        """
        if self.client is not None and self.client.logged_in:
            self.frame.client_connected(self.client)

    def disconnect_client(self):
        """
        Callback to close the active Strategy Client and reset the widgets to their normal state
        """
        if not self.client:
            return
        if self.client.logged_in:
            self.client.close()
        if not self.server:
            self.protocol("WM_DESTROY_WINDOW", self.destroy)
        self.client_button.config(text="Connect", command=self.connect_client)
        self.client_name_entry.config(state=tk.NORMAL)
        self.client_role_dropdown.config(state=tk.NORMAL)
        self.client_address_entry.config(state=tk.NORMAL)
        self.client_port_entry.config(state=tk.NORMAL)
        self.client = None
        if callable(self._disconnectcallback):
            self._disconnectcallback()

    def destroy_redirect(self):
        """
        Function to prevent the destruction of the SettingsToplevel while either a Server or Client is running.
        """
        messagebox.showinfo("Info", "You cannot close this window while you are connected to a strategy server or "
                                    "running one.")
        self.lift()

    def open_strategy(self):
        """
        Callback of the filemenu to import a Strategy into the database from a pickle file
        """
        file_name = filedialog.askopenfilename(filetypes=[("GSF Strategy", ".str")], defaultextension=".str",
                                               title="GSF Strategy Manager: Open a strategy")
        if file_name == "" or file_name is None:
            return
        with open(file_name, "rb") as fi:
            strategy = pickle.load(fi)
        self.list.db[strategy.name] = strategy
        self.list.update_tree()

    def save_strategy(self):
        """
        Alt for save_strategy_as. #TODO: Implement this as its own function
        """
        self.save_strategy_as()

    def save_strategy_as(self):
        """
        Save the strategy to a pickle file so it can be imported in another copy of the GSF Parser
        """
        file_name = filedialog.asksaveasfilename(filetypes=[("GSF Strategy", ".str")], defaultextension=".str",
                                                 title="GSF Strategy Manager: Save a strategy")
        if file_name == "" or file_name is None:
            return
        strategy = self.list.db[self.list.selected_strategy]
        with open(file_name, "wb") as fo:
            pickle.dump(strategy, fo)

    def save_strategy_database(self):
        """
        Alt for the StrategyDatabase.save_database function of the instance
        """
        self.list.db.save_database()

    def _import(self):
        """
        Callback for the menu to import a whole new StrategyDatabase. The new database is merged in, and does not remove
        current Strategies, though it does update them if they have the same name. The database is imported from a
        pickle.
        """
        file_name = filedialog.askopenfilename(filetypes=[".db"], defaultextension=".db",
                                               title="GSF Strategy Manger: Import a database")
        if file_name == "" or file_name is None:
            return
        self.list.db.merge_database(StrategyDatabase(file_name=file_name))
        self.list.update_tree()

    def _export(self):
        """
        Callback for the menu to export the whole StrategyDatabase of the instance to a pickle file in a custom location
        so it can be imported in another copy of the GSF Parser.
        """
        file_name = filedialog.asksaveasfilename(filetypes=[".db"], defaultextension=".db",
                                                 title="GSF Strategy Manager: Export the database")
        if file_name == "" or file_name is None:
            return
        self.list.db.save_database_as(file_name)

    def destroy(self):
        self.frame.settings = None
        tk.Toplevel.destroy(self)


class ClosingToplevel(tk.Toplevel):
    """
    Simple Toplevel to indicate that the user has to wait while the Server is stopping its activities.
    """
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="indeterminate", length=300)
        self.bar.grid(pady=5)
        self.bar.start(10)
        self.title("Closing server...")
