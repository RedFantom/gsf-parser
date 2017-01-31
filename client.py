# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

import socket
import variables
import toplevels
import tkMessageBox
import hashlib
import threading
import ssl
import time

class client_conn:
    """
    A class that connects to a remote server as specified in the settings_obj
    of the module variables.py in order to get data related to parsing
    Operates following the protocol as described in PROTOCOL
    Has support for a splash screen from the module overlay
    """
    # TODO Add functionality to get leaderboards
    def __init__(self):
        self.connecting = True
        self.INIT = False

    def init_conn(self, silent=True):
        """
        Set up the connection to server and do the required error handling when
        this fails. Also tries to wrap the connection in an SSL layer.

        If the response of the server is BANNED, the client is banned for some reason
        and will be unable to connect until the server is rebooted, which may take a
        long time >:|
        :param silent: when True, no splash screen is created for connecting
        :return:
        """
        self.INIT = False
        self.closing = False
        if not silent:
            print "[DEBUG] Creating conn_splash"
            self.splash = toplevels.conn_splash(window=variables.main_window)
        self.conn_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (variables.set_obj.server_address, variables.set_obj.server_port)
        self.TIME_OUT = 4
        self.conn_obj.settimeout(self.TIME_OUT)
        self.address = (variables.set_obj.server_address, variables.set_obj.server_port)
        self.conn = self.wrap_conn_obj(self.conn_obj)
        try:
            self.conn.connect(self.address)
        except ssl.SSLError as e:
            print "[DEBUG] %s" % e
            tkMessageBox.showerror("Error", "An encryption error occurred while connecting to the server.")
            self.connecting = False
            if not silent:
                self.splash.destroy()
            return
        except socket.timeout:
            tkMessageBox.showerror("Error", "A time-out occured while connecting to the server.")
            self.connecting = False
            if not silent:
                self.splash.destroy()
            return
        except socket.error:
            tkMessageBox.showerror("Error", "The server closed the connection.")
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            self.connecting = False
            return
        except:
            tkMessageBox.showerror("Error", "An error occurred while connecting to the server.")
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        if self.send("INIT") == -1:
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        self.BUFF = 16
        message = self.recv(self.BUFF)
        if message == -1:
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        elif message == "INIT":
            self.INIT = True
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        elif message == "MAINTENANCE":
            self.maintenance()
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        elif message == "UNAVAILABLE":
            self.unavailable()
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        elif message == "BANNED":
            self.banned()
            self.connecting = False
            if not silent:
                self.splash.FLAG = True
                self.splash.destroy()
            return
        else:
            self.unexpected()
            self.close()
        self.connecting = False
        if not silent:
            self.splash.FLAG = True
            self.splash.destroy()
        return

    def get_killed(self, ID, serv, player):
        """
        Takes parameters and sends them to server, returns the id
        of the killer.
        :param ID: The ID number/hash (to be decided) of the victim
        :param serv: The server of the victim
        :param player: The altname of the victim
        :return:
        """
        if not self.INIT:
            self.notinit()
            return
        if self.send("KILLEDBY") == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "READY":
            self.unexpected()
            return
        if self.send("SERVER=%s" % serv): return
        if self.send(hashlib.sha512(ID)) == -1: return
        message = self.recv(self.BUFF)
        if message != "KILLEDBY":
            self.unexpected()
            return
        recv_hash = self.recv(512)
        for key, value in player.iteritems():
            if hashlib.sha512(key) == recv_hash:
                return True
        return False

    def get_name(self, ID, serv, fact):
        """
        Perform a lookup of a name of a certain id on the remote server
        and return the name found, or a special code if none is found for
        the id number
        :param ID: ID number of the person too lookup
        :param serv: the server of the player
        :param fact: the faction of the player
        :return:
        """
        if not self.INIT:
            self.notinit()
            return
        if self.send("NEWCOM") == -1: return
        if self.send("LOOKUP") == -1: return
        if self.send("SERVER=%s" % serv) == -1: return
        if self.send("FACT=%s" % fact) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "READY":
            self.unexpected()
            return
        if self.send(hashlib.sha512(ID)) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        if self.send("RECV") == -1: return
        return message

    def logstr(self, file_name, serv, fact, player_name):
        """
        Send a Combatlog file to the server if it is not already
        present on the server.
        :param file_name: the file to send
        :param serv: the server
        :param fact: the faction
        :param player_name: the altname of the player
        :return:
        """
        if not self.INIT:
            self.notinit()
            return
        if self.send("NEWCOM") == -1: return
        if self.send("LOGSTR") == -1: return
        if self.send("SERVER=%s" % serv) == -1: return
        if self.send("FACTION=%s" % fact) == -1 : return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "READY":
            self.unexpected()
            return
        with open(file_name, "r") as file_obj:
            lines = file_obj.readlines()
        if self.send("LEN=%s" % len(lines)) == -1: return
        if self.send(hashlib.sha512(lines)) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message == "DUPLICATE":
            self.duplicate()
            return
        elif message != "ACK": return
        for line in lines:
            if self.send(line) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "RECV":
            self.unexpected()
            return
        return 0

    def name_send(self, name, ID, serv, fact):
        """
        Send a name and the belonging id to the server for storage
        :param name: altname
        :param ID: id number
        :param serv: server
        :param fact: faction
        :return:
        """
        if not self.INIT:
            self.notinit()
            return
        if self.send("NAME") == -1: return
        if self.send("SERVER=%s" % serv) == -1: return
        if self.send("FACT=%s" % fact) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "READY":
            self.unexpected()
            return
        if self.send(name) == -1: return
        if self.send(hashlib.sha512(ID)) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "ACK":
            self.unexpected()
            return
        return 0

    def kill_send(self, ID_self, ID_kill, serv, fact):
        """
        Store a killer-victim combination on the server
        for later retrievel by the get_killed() function
        :param ID_self: victim id
        :param ID_kill: killer id
        :param serv: server
        :param fact: faction
        :return:
        """
        if not self.INIT:
            self.notinit()
            return
        if self.send("KILLEDBYS") == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "READY":
            self.unexpected()
            return
        if self.send("SERVER=%s" % serv) == -1: return
        if self.send("FACT=%s" % fact) == -1: return
        if self.send(hashlib.sha512(ID_self)) == -1: return
        if self.send(hashlib.sha512(ID_kill)) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "ACK":
            self.unexpected()
            return
        return 0

    def send_fb(self, fb):
        """
        Send feedback to the server for review by the server owner
        :param fb: A string of feedback
        :return:
        """
        if not self.INIT:
            self.notinit()
            return
        if self.send("FEEDBACK") == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "READY":
            self.unexpected()
            return
        if self.send(fb) == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "ACK":
            self.unexpected()
            return
        return 0

    def get_privacy(self):
        """
        Get the privacy statement of the server
        :return: privacy statement
        """
        if not self.INIT:
            self.notinit()
            return -1
        if self.send("PRIVACY") == -1: return -1
        message = self.recv(self.BUFF)
        if message == -1: return -1
        elements = message.split("=")
        try:
            length = int(elements[1])
        except:
            self.unexpected()
            return -1
        return self.recv(length)

    def retry(self):
        """
        Function to retry connecting to the server
        :return:
        """
        self.init_conn()

    def send(self, message):
        """
        Send a message to the server and do the error-handling
        :param message:
        :return:
        """
        try:
            self.conn.send(message)
        except socket.timeout:
            self.timeout()
            return -1
        except:
            self.failed()
            return -1
        return 0

    def recv(self, BUFF=128):
        """
        Receive a message from the server and do the error-handling
        :param BUFF:
        :return:
        """
        try:
            message = self.conn.recv(BUFF)
        except socket.timeout:
            self.timeout()
            return -1
        except:
            self.failed()
            return -1
        if message == "":
            self.empty()
            return -1
        elif message == "MAINTENANCE":
            self.maintenance()
            self.close()
            return -1
        elif message == "UNAVAILABLE":
            self.unavailable()
            self.close()
            return -1
        elif message == "DEPRECATED":
            self.deprecated()
            self.close()
            return -1
        elif message == "CLOSED" and not self.closing:
            self.unexpected()
            self.close()
            return -1
        return message

    def close(self):
        """
        Close the connection to the server by sending the signal
        and then close the objects
        :return:
        """
        self.closing = True
        if self.send("STOPCN") == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "CLOSED":
            self.unexpected()
            self.conn.close()
            self.conn_obj.close()
            return
        self.conn.close()
        self.conn_obj.close()
        return

    def __exit__(self):
        self.close()

    def __enter__(self):
        return self

    """
    Methods for displaying various error messages to the user.
    """
    @staticmethod
    def timeout():
        tkMessageBox.showerror("Error", "The connection timed out.")
        return

    @staticmethod
    def empty():
        tkMessageBox.showerror("Error", "The response of the server is empty.")
        return

    @staticmethod
    def unexpected():
        tkMessageBox.showerror("Error", "Did not get the expected response.")
        return

    @staticmethod
    def failed():
        tkMessageBox.showerror("Error", "Sending or receiving data from the server failed.")
        return

    @staticmethod
    def notinit():
        tkMessageBox.showerror("Error", "The connection was not initialized correctly.")
        return

    @staticmethod
    def maintenance():
        tkMessageBox.showinfo("Notice", "The server is in maintenance mode.")
        return

    @staticmethod
    def unavailable():
        tkMessageBox.showinfo("Notice", "The server is unavailable for an unknown reason.")
        return

    @staticmethod
    def deprecated():
        tkMessageBox.showinfo("Notice", "Cannot connect to the server, this parser is not up-to-date. Please update.")
        return

    @staticmethod
    def duplicate():
        tkMessageBox.showinfo("Notice", "This file is already present on the server.")
        return

    @staticmethod
    def banned():
        tkMessageBox.showerror("Error", "This IP-address is banned from this server.")
        return

    @staticmethod
    def wrap_conn_obj(sock):
        """
        Take a socket object and return it wrapped in a layer of SSL
        :param sock:
        :return: an SSL-wrapped socket
        """
        ssl.create_default_context()
        wrapped = ssl.wrap_socket(sock)
        return wrapped

class realtime_conn(threading.Thread):
    """
    UNFINISHED!
    This class will run in the background, sending real-time data to the server
    and retrieving data as well.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.init_conn()
        self.lines_to_send = []
        self.names_to_get = []
        self.names_to_send = []

    def init_conn(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (variables.set_obj.server_address, variables.set_obj.server_port)
        try:
            self.conn.connect(self.address)
        except ssl.SSLError:
            tkMessageBox.showerror("Error", "An encryption error occurred while connecting to the server.")
            self.INIT=False
            return
        if self.send("INIT") == -1: return
        self.INIT = False
        self.BUFF = 16
        self.TIME_OUT = 4
        self.conn.settimeout(self.TIME_OUT)
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message == "INIT":
            self.INIT = True
            return
        elif message == "MAINTENANCE":
            self.maintenance()
            return
        elif message == "UNAVAILABLE":
            self.unavailable()
            return
        elif message == "BANNED":
            self.banned()
            return
        else:
            self.unexpected()
            self.close()

    def retry(self):
        self.init_conn()

    def send(self, message):
        try:
            self.conn.send(message)
        except socket.timeout:
            self.timeout()
            return -1
        except:
            self.failed()
            return -1
        return 0

    def recv(self, BUFF=128):
        try:
            message = self.conn.recv(BUFF)
        except socket.timeout:
            self.timeout()
            return -1
        except:
            self.failed()
            return -1
        if message == "":
            self.empty()
            return -1
        elif message == "MAINTENANCE":
            self.maintenance()
            self.close()
            return -1
        elif message == "UNAVAILABLE":
            self.unavailable()
            self.close()
            return -1
        elif message == "DEPRECATED":
            self.deprecated()
            self.close()
            return -1
        return message

    def close(self):
        if self.send("STOPCN") == -1: return
        message = self.recv(self.BUFF)
        if message == -1: return
        elif message != "CLOSED":
            self.unexpected()
            self.conn.close()
            return
        self.conn.close()
        return

    def __exit__(self):
        self.close()

    def __enter__(self):
        return self

    @staticmethod
    def timeout():
        tkMessageBox.showerror("Error", "The connection timed out.")
        return

    @staticmethod
    def empty():
        tkMessageBox.showerror("Error", "The response of the server is empty.")
        return

    @staticmethod
    def unexpected():
        tkMessageBox.showerror("Error", "Did not get the expected response.")
        return

    @staticmethod
    def failed():
        tkMessageBox.showerror("Error", "Sending or receiving data from the server failed.")
        return

    @staticmethod
    def notinit():
        tkMessageBox.showerrror("Error", "The connection was not initialized correctly.")
        return

    @staticmethod
    def maintenance():
        tkMessageBox.showinfo("Notice", "The server is in maintenance mode.")
        return

    @staticmethod
    def unavailable():
        tkMessageBox.showinfo("Notice", "The server is unavailable for an unknown reason.")
        return

    @staticmethod
    def deprecated():
        tkMessageBox.showinfo("Notice", "Cannot connect to the server, this parser is not up-to-date. Please update.")
        return

    @staticmethod
    def dupliate():
        tkMessageBox.showinfo("Notice", "This file is already present on the server.")
        return

    @staticmethod
    def banned():
        tkMessageBox.showerror("Error", "This IP-address is banned from this server.")
        return