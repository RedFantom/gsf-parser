"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import sqlite3 as sql
import threading
import queue
import time
import logging
import os
import network.queries as queries


class DatabaseHandler(threading.Thread):
    """
    Class to handle all database interactions of the clients
    Queries and commands are taken from the Queue object and
    executed. Error-handling is extensive.
    Also uses a Shelf object in order to store DPS per build
    (to be implemented in the GSF Parser and PROTOCOL)
    """

    servers = {
        "SF": "US",
        "SA": "US",
        "TH": "EU",
        "DM": "EU",
        "TL": "EU"
    }

    def __init__(self, db_name="parser.db", logfile="database_%s.log" % time.strftime("%Y-%m-%d")):
        """
        :param db_name: Name for the database file
        """
        threading.Thread.__init__(self)
        self.db_done = False
        self.log_file = logging.getLogger(__name__)
        handler = logging.FileHandler(os.path.join("var", "log", "sharing", logfile))
        self.log_file.addHandler(handler)
        self.log_file.addFilter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)"))
        self.db_queue = queue.Queue()
        self.exit_queue = queue.Queue()
        self.db_name = db_name
        self.database = None
        self.cursor = None

    def log(self, line):
        """Log a line to the log file"""
        self.log_file.info(line)

    def __exit__(self):
        self.close()

    def close(self):
        """
        Close the databases and wrap up
        :return:
        """
        self.exit_queue.put(True)
        self.log("Database closed.")
        print("[DEBUG] Database object has cleaned up.")
        self.log("Database thread closed.")
        return 0

    def setup(self):
        """
        Upon execution of start(), the database is prepared with the
        default first queries found in queries.py
        """
        self.command_handler(queries.create_tb_server)
        self.command_handler(queries.create_tb_combatlogs)
        self.command_handler(queries.create_tb_id)
        self.command_handler(queries.create_tb_alt)
        self.command_handler(queries.create_tb_bombers)
        self.command_handler(queries.create_tb_killedby)
        self.command_handler(queries.combatlog_first_command)
        self.command_handler(queries.alt_first_command)
        for key, value in self.servers.items():
            self.command_handler(queries.insert_server % (key, value))

    def run(self):
        """
        Main loop to run and check for commands in the Queue objects
        Execute queries and commands and return the results if necessary
        Alternates one command for the Shelf and one command for the
        database.
        """
        if not self.db_done:
            self.database = sql.connect(self.db_name)
            self.cursor = self.database.cursor()
            self.setup()
            self.db_done = True
        print("[DatabaseHandler] DatabaseHandler starting activities.")
        while self.exit_queue.empty():
            if self.db_queue.qsize() > 0:
                print("[DatabaseHandler] Received a command in the Queue.")
                # return_queue is a Queue object, to_exec is a string (query or command),
                # query is a boolean which is True if to_exec is a query
                return_queue, to_exec, query = self.db_queue.get()
                self.log("The following command was received: %s" % to_exec)
                self.log("The command is a query: %s" % query)
                if query:
                    print("[DatabaseHandler] Received command is a query.")
                    data = self.query_handler(to_exec)
                    self.log("The following data was returned by the query: %s" % data)
                    if data == -1:
                        print("[DatabaseHandler] Encountered an error while executing the query.")
                        return_queue.put((False, to_exec, query))
                        self.log("The data == -1, thus an error occurred. Returning that in the queue.")
                    else:
                        new_data = []
                        for item in data:
                            new_data.append(str(item[0]))
                        if len(new_data) == 0:
                            return_queue.put(None)
                        self.log("Generated data from this list: %s" % new_data)
                        print("[DatabaseHandler] Data retrieved from database:", new_data)
                        return_queue.put(new_data)
                        self.log("Request completed successfully.")
                        print("[DatabaseHandler] Query completed.")
                else:
                    print("[DatabaseHandler] Executing command.")
                    return_code = self.command_handler(to_exec)
                    self.log("The return code of the command_handler for this command was: %s" % return_code)
                    print("[DatabaseHandler] Result:", return_code)
                    if return_code == -1:
                        return_queue.put((False, to_exec, query))
                        self.log("Command execution failure.")
                        print("[DatabaseHandler] Command execution failed.")
                    else:
                        return_queue.put((True, to_exec, query))
                        self.log("Command completed successfully.")
                        print("[DatabaseHandler] Command executed successfully.")
                self.log("Command/Query done, moving on")
            else:
                time.sleep(0.1)
        self.cursor.close()
        self.database.close()

    def query_handler(self, query):
        """
        Execute a query on the database and return the data that is selected
        All possible errors for sqlite3 can be caught and logged
        """
        # Execute the query on the database
        try:
            self.cursor.execute(query)
            data = self.cursor.fetchall()
        except sql.Error as e:
            self.log("An Error occurred: %s" % e)
            return -1
        self.log("Query was executed successfully: %s" % query)
        return data

    def command_handler(self, command):
        """
        Execute a command on the database
        If the command fails, log it and rollback the changes made
        to the database in the process of executing the command
        else, commit the changes and return to mainloop
        """
        try:
            self.cursor.execute(command)
        except sql.Error as e:
            self.log("An Error occurred: %s" % e)
            self.database.rollback()
            return -1
        self.database.commit()
        self.log("Command was executed successfully: %s" % command)
        return 0

    def put_command_in_queue(self, return_queue, command, query=False):
        self.db_queue.put((return_queue, command, query))
