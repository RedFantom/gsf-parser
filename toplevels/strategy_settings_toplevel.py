# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import _pickle as pickle
import tkinter as tk
from ast import literal_eval
from tkinter import messagebox, filedialog
from widgets.snaptoplevel import SnapToplevel
from tkinter import ttk
import variables
from parsing.strategies import StrategyDatabase
from server.strategy_client import StrategyClient
from server.strategy_server import StrategyServer
from tools.admin import run_as_admin, is_user_admin
from toplevels.strategy_share_toplevel import StrategyShareToplevel
from widgets.verticalscrollframe import VerticalScrollFrame as ScrolledFrame


class SettingsToplevel(SnapToplevel):
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
        self._good_geometry = None
        self.destroyed = False
        SnapToplevel.__init__(self, variables.main_window, border=100, locked=True, resizable=True, wait=0, height=425,
                              width=355)

        self.update()
        self.title("GSF Strategy Planner: Settings")
        self.menu = tk.Menu(self)
        # Strategy menu
        self.strategy_menu = tk.Menu(self, tearoff=False)
        self.strategy_menu.add_command(label="New Strategy", command=self.new_strategy)
        self.strategy_menu.add_command(label="Import Strategy", command=self.open_strategy)
        self.strategy_menu.add_command(label="Export Strategy", command=self.save_strategy_as)
        self.menu.add_cascade(label="Strategy", menu=self.strategy_menu)
        # Database menu
        self.database_menu = tk.Menu(self, tearoff=False)
        self.database_menu.add_command(label="Import database", command=self._import)
        self.database_menu.add_command(label="Export database", command=self._export)
        self.menu.add_cascade(label="Database", menu=self.database_menu)
        self.config(menu=self.menu)

        self.scrolled_frame = ScrolledFrame(self, canvaswidth=345, canvasheight=415)
        self.server_client_frame = self.scrolled_frame.interior
        # Server settings section
        self.server_section = ttk.Frame(self.server_client_frame)
        self.server_header = ttk.Label(self.server_section, text="Server settings", justify=tk.LEFT,
                                       font=("default", 11))
        self.server_address_entry = ttk.Entry(self.server_section, width=17)
        self.server_port_entry = ttk.Entry(self.server_section, width=8)
        self.server_port_entry.bind("<Return>", self.start_server)
        self.server_button = ttk.Button(self.server_section, text="Start server", command=self.start_server, width=15)

        # Client settings section
        self.client_section = ttk.Frame(self.server_client_frame)
        self.client_name_entry = ttk.Entry(self.client_section, width=17)
        self.client_name_entry.bind("<Return>", self.connect_client)
        self.client_role = tk.StringVar()
        self.client_role_dropdown = ttk.OptionMenu(self.client_section, self.client_role,
                                                   *("Choose role", "Master", "Client"))
        self.client_role.set("Client")
        self.client_header = ttk.Label(self.client_section, text="Client settings", justify=tk.LEFT,
                                       font=("default", 11))
        self.client_address_entry = ttk.Entry(self.client_section, width=17)
        self.client_port_entry = ttk.Entry(self.client_section, width=8)
        self.client_port_entry.bind("<Return>", self.connect_client)
        self.client_button = ttk.Button(self.client_section, text="Connect to server", width=15,
                                        command=self.connect_client)

        # Server master widgets
        self.server_master_frame = ttk.Frame(self.server_client_frame, width=280)
        self.server_master_header = ttk.Label(self.server_master_frame, text="Server Master settings",
                                              font=("default", 11))
        self.server_master_clients_treeview = ttk.Treeview(self.server_master_frame)
        self.server_master_client_scrollbar = ttk.Scrollbar(self.server_master_frame,
                                                            command=self.server_master_clients_treeview.yview)
        self.server_master_clients_treeview.config(yscrollcommand=self.server_master_client_scrollbar.set)
        self.server_master_clients_treeview.config(columns=("allowshare", "allowedit"))
        self.server_master_clients_treeview["show"] = ("tree", "headings")
        self.server_master_clients_treeview.column("#0", width=115)
        self.server_master_clients_treeview.config(height=4)
        self.server_master_clients_treeview.column("allowshare", width=85)
        self.server_master_clients_treeview.column("allowedit", width=85)
        self.server_master_clients_treeview.heading("allowshare", text="Allow share")
        self.server_master_clients_treeview.heading("#0", text="Client name")
        self.server_master_clients_treeview.heading("allowedit", text="Allow edit")
        self.server_master_clients_treeview.bind("<Button-1>", self._select)
        self.server_master_clients_treeview.bind("<Double-1>", self._select)
        self.server_master_clients_treeview.tag_configure("master", background="#2bff83")

        self.server_master_allow_share_button = ttk.Button(self.server_master_frame,
                                                           text="Allow sharing of Strategies",
                                                           command=self._allow_share, state=tk.DISABLED)
        self.server_master_allow_edit_button = ttk.Button(self.server_master_frame,
                                                          text="Allow editing of Strategies",
                                                          command=self._allow_edit, state=tk.DISABLED)
        self.server_master_make_master_button = ttk.Button(self.server_master_frame,
                                                           text="Make new master Client",
                                                           command=self._make_master, state=tk.DISABLED)
        self.server_master_kick_button = ttk.Button(self.server_master_frame, text="Kick from server",
                                                    command=self._kick, state=tk.DISABLED)
        self.server_master_ban_button = ttk.Button(self.server_master_frame, text="Ban from server",
                                                   command=self._ban, state=tk.DISABLED)
        # List with references to all master control widgets
        self.master_control_widgets = [
            self.server_master_kick_button,
            self.server_master_ban_button,
            self.server_master_allow_edit_button,
            self.server_master_allow_share_button,
            self.server_master_make_master_button
        ]

        self.client = None
        self.server = None
        self.share_toplevel = None
        # Dictionary to store the Treeview keys and player names
        self.client_names = {}
        # Dictionary to store  the client names as keys and permissions (allowshare, allowedit)
        self.client_permissions = {}
        # The name of the master client
        self.master_client = None
        # self.resizable(False, False)
        self.grid_widgets()

    def grid_widgets(self):
        """
        The usual function to put all the widgets in the correct place
        """
        self.scrolled_frame.grid(row=1, column=1, sticky="nswe")

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

        self.server_master_frame.grid(row=3, column=1, sticky="nswe")
        self.server_master_header.grid(row=0, column=1, sticky="nw", padx=10, pady=(0, 5))
        self.server_master_clients_treeview.grid(row=1, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_master_client_scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=(0, 5))
        self.server_master_allow_share_button.grid(row=2, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_master_allow_edit_button.grid(row=3, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_master_make_master_button.grid(row=4, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_master_kick_button.grid(row=5, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))
        self.server_master_ban_button.grid(row=6, column=1, sticky="nswe", padx=(5, 0), pady=(0, 5))

    @property
    def selected_client(self):
        selection = self.server_master_clients_treeview.selection()
        if selection == () or selection is None:
            return
        name = selection[0]
        if name not in self.client_names:
            raise ValueError("Name {} not in client names dictionary".format(name))
        return self.client_names[name]

    def _select(self, event):
        name = self.selected_client
        if name is None:
            return
        allowshare, allowedit = permissions = self.client_permissions[name]
        if allowshare is True:
            self.server_master_allow_share_button.config(text="Disallow sharing of Strategies")
        else:
            self.server_master_allow_share_button.config(text="Allow sharing of Strategies")
        if allowedit is True:
            self.server_master_allow_edit_button.config(text="Disallow editing of Strategies")
        else:
            self.server_master_allow_edit_button.config(text="Allow editing of Strategies")
        if name == self.client.name and self.client.role == "master":
            self.server_master_make_master_button.config(state=tk.DISABLED)
        else:
            self.server_master_make_master_button.config(state=tk.NORMAL)

    def _allow_share(self):
        player_name = self.selected_client
        if player_name == self.client.name and self.client.role == "master":
            # The master cannot disallow himself from sharing
            return
        allow = not self.client_permissions[player_name][0]
        self.client_permissions[player_name] = (allow, self.client_permissions[player_name][1])
        self.client.allow_share_player(player_name, allow)
        self.server_master_clients_treeview.item(self.reverse_name_dictionary[player_name],
                                                 values=self.client_permissions[player_name])

    def _allow_edit(self):
        player_name = self.selected_client
        if player_name == self.client.name and self.client.role == "master":
            # The master cannot disallow himself from editing
            return
        allow = not self.client_permissions[player_name][1]
        self.client_permissions[player_name] = (self.client_permissions[player_name][0], allow)
        self.client.allow_edit_player(player_name, allow)
        self.server_master_clients_treeview.item(self.reverse_name_dictionary[player_name],
                                                 values=self.client_permissions[player_name])

    def _make_master(self):
        player_name = self.selected_client
        if player_name is None:
            return
        self.client.new_master(player_name)
        reverse = self.reverse_name_dictionary
        if reverse[player_name] not in self.server_master_clients_treeview.get_children(""):
            return
        self.server_master_clients_treeview.item(reverse[self.client_name_entry.get()], tags=(),
                                                 values=("False", "False"))
        self.server_master_clients_treeview.item(reverse[player_name], tags=("master",), values=("Master", "Master"))
        self.lock_master_control_widgets()
        self.master_client = player_name

    def _kick(self):
        print("Kick client")
        player_name = self.selected_client
        if player_name is None:
            return
        self.client.kick_player(player_name)

    def _ban(self):
        print("Ban client")
        player_name = self.selected_client
        if player_name is None:
            return
        self.client.ban_player(player_name)

    def _login_callback(self, player_name, role):
        if player_name in self.client_permissions:
            return
        if role == "master":
            permissions = ("Master", "Master")
            tags = "master"
            self.master_client = player_name
        else:
            permissions = (False, False)
            tags = ()
        self.client_names[self.server_master_clients_treeview.insert("", tk.END, text=player_name,
                                                                     values=permissions, tags=tags,
                                                                     iid=player_name)] \
            = player_name
        self.client_permissions[player_name] = permissions

    def _logout_callback(self, player_name):
        reverse = self.reverse_name_dictionary
        if isinstance(player_name, list):
            _, player_name = player_name
        try:
            self.server_master_clients_treeview.delete(reverse[player_name])
        except tk.TclError:
            return
        if player_name == self.client.name:
            self.client = None
        self.client_permissions.pop(player_name)

    def new_master(self, name):
        """
        Callback for when a new master is selected for the Server
        """
        reverse = self.reverse_name_dictionary
        if name not in reverse:
            print("Name not found in client names/Treeview dictionary: {}".format(name))
            print("names/Treeview dictionary: {}".format(reverse))
            return
        self.server_master_clients_treeview.item(reverse[name], tags=("master",))
        if self.master_client is not None:
            self.server_master_clients_treeview.item(reverse[self.master_client], tags=(), values=("False", "False"))
        self.master_client = name

    def start_server(self, *args):
        """
        Start a new Strategy Server. User must be an admin user to start a server (as the binding to an address
        requires privileges to create a port in the Windows Firewall).
        """
        if not is_user_admin():
            # If the user is not an admin, making a hole in the firewall to receive connections is not possible
            # The program should re-run as admin, possibly with UAC elevation
            confirmation = messagebox.askyesno("Question", "Starting a server requires administrative privileges, "
                                                           "would you like to restart the GSF Parser as an "
                                                           "administrator?")
            if not confirmation:
                return
            self.destroy()
            variables.main_window.destroy()
            try:
                # Re-run as an administrator
                run_as_admin()
            except Exception as e:
                # If an error occurs, it is highly likely that the user has denied UAC elevation
                print(repr(e))
            exit()
        # Try to start the server
        try:
            self.server = StrategyServer(self.server_address_entry.get(), int(self.server_port_entry.get()))
        # Handle any errors the Server initialization may throw by showing a messagebox to the user
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
        # Make sure that if the user attempts to close the window, this command is redirected
        self.protocol("WM_DELETE_WINDOW", self.destroy_redirect)
        # Start the Server thread
        self.server.start()
        # Change the UI to match behaviour
        self.server_button.config(text="Stop server", command=self.stop_server)
        # Allow the starter of the server to easily connect to his own server by entering the server details into
        # The client connection data boxes after the server has started
        self.client_address_entry.delete(0, tk.END)
        if not self.server_address_entry.get() == "":
            self.client_address_entry.insert(tk.END, self.server_address_entry.get())
        else:
            self.client_address_entry.insert(tk.END, "127.0.0.1")
        self.client_port_entry.delete(0, tk.END)
        self.client_port_entry.insert(tk.END, self.server_port_entry.get())
        self.client_role.set("Master")
        self.server_port_entry.config(state=tk.DISABLED)
        self.server_address_entry.config(state=tk.DISABLED)
        self.client_name_entry.focus_set()

    def deminimize(self, event):
        """
        Callback for the <Map> event generated by Tkinter. Deminimizes the window if the Strategies tab is selected
        and the <Map> event is generated.
        """
        # Check if the window is destroyed first to prevent a TclError (bad window path name, you can't call
        # deiconify on a window that has been destroyed)
        if self.destroyed:
            return
        notebook_selected = variables.main_window.notebook.index(tk.CURRENT)
        if notebook_selected != 5:
            self.minimize(event)
            return
        tk.Toplevel.deiconify(self)

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

    def connect_client(self, *args):
        """
        Create a new connection to a client
        """
        self.client = StrategyClient(self.client_address_entry.get(), int(self.client_port_entry.get()),
                                     self.client_name_entry.get(), self.client_role.get(), self.list, self.login_callback,
                                     self.frame.insert_callback, self.disconnect_client)
        if self.client.role.lower() == "client":
            print("Setting map to be readonly")
            for map in self.frame.maps:
                map.set_readonly(True)
        else:
            print("Role is not 'client', but {0}, so not setting readonly".format(self.client.role.lower()))
        if self.client.role == "master":
            self.master_client = self.client.name
            self.unlock_master_control_widgets()
        return

    def update_edit(self, name, allowed):
        """
        Function called by the insert_callback of StrategiesFrame in order to update the editing right of a user
        in the Treeview
        """
        self.client_permissions[name] = (self.client_permissions[name][0], allowed)
        self.server_master_clients_treeview.item(self.reverse_name_dictionary[name],
                                                 values=self.client_permissions[name])

    def update_share(self, name, allowed):
        """
        Function called by the insert_callback of StrategiesFrame to update the sharing right of a user in the Treeview
        """
        if not isinstance(allowed, bool):
            allowed = literal_eval(allowed)
        self.client_permissions[name] = (allowed, self.client_permissions[name][1])
        self.server_master_clients_treeview.item(self.reverse_name_dictionary[name],
                                                 values=self.client_permissions[name])
        print("Updating allow_share for {} to {}".format(name, allowed))
        if name != self.client.name:
            return
        if allowed:
            print("Now opening share_toplevel")
            if self.share_toplevel:
                return
            self.share_toplevel = StrategyShareToplevel(self, self.client, self.frame.list.db, self.frame, width=270,
                                                        height=425, resizable=False)
        elif not allowed and self.share_toplevel is not None:
            self.share_toplevel.destroy()
            self.share_toplevel = None
        else:
            return

    def update_master(self):
        """
        Function for the Client to call when the user is granted Master control over the Server
        """
        self.server_master_clients_treeview.item(self.reverse_name_dictionary[self.master_client], tags=(),
                                                 values=("False", "False"))
        self.master_client = self.client.name
        self.server_master_clients_treeview.item(self.reverse_name_dictionary[self.master_client], tags=("master",),
                                                 values=("Master", "Master"))
        self.unlock_master_control_widgets()

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
            self.client = None
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
        self.server_master_clients_treeview.delete(*self.server_master_clients_treeview.get_children(""))
        self.lock_master_control_widgets()
        self.client = None
        if callable(self._disconnectcallback):
            self._disconnectcallback()
        self.client_permissions.clear()

    def destroy_redirect(self):
        """
        Function to prevent the destruction of the SettingsToplevel while either a Server or Client is running.
        """
        messagebox.showinfo("Info", "You cannot close this window while you are connected to a strategy server or "
                                    "running one.")
        self.lift()

    def destroy(self):
        if self.share_toplevel:
            self.share_toplevel.destroy()
            self.share_toplevel = None
        SnapToplevel.destroy(self)
        self.frame.settings = None
        self.destroyed = True

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

    def lock_master_control_widgets(self):
        """
        Function to lock all master control widgets by setting them to a DISABLED state
        """
        for widget in self.master_control_widgets:
            widget.config(state=tk.DISABLED)
        if self.share_toplevel:
            self.share_toplevel.destroy()
            self.share_toplevel = None
        return

    def unlock_master_control_widgets(self):
        """
        Function to unlock all master control widgets by setting them to a NORMAL state
        """
        for widget in self.master_control_widgets:
            widget.config(state=tk.NORMAL)
        self.share_toplevel = StrategyShareToplevel(self, self.client, self.frame.list.db, self.frame, width=270,
                                                    height=425)
        return

    @property
    def reverse_name_dictionary(self):
        return {value: key for key, value in self.client_names.items()}


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
