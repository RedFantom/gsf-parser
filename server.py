# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from server.sharing_server import SharingServer
from datetime import datetime
import argparse

"""
Setup a SharingServer with command-line arguments. Available arguments:
-a: address to bind to
-p: port to accept connections on
-c: maximum amount of clients
-t: amount of time in minutes to run the server for
"""

DESCRIPTION = "GSF Parser Sharing Server"

DEFAULT_PORT = 83
DEFAULT_CLIENTS = 16
DEFAULT_TIME = 0
DEFAULT_ADDRESS = "127.0.0.1"

if __name__ == '__main__':
    """
    First, setup the argument parser with all the possible arguments
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    # Address
    parser.add_argument(
        "-a", type=str, nargs=1, help="Address to bind the server to, 'all' means all available",
        default=DEFAULT_ADDRESS)
    # Port
    parser.add_argument(
        "-p", type=int, nargs=1, help="Port to accept connections on", default=DEFAULT_PORT)
    # Clients
    parser.add_argument(
        "-c", type=str, nargs=1, help="Maximum amount of Clients to allow on the Server simultaneously",
        default=DEFAULT_CLIENTS)
    # Time
    parser.add_argument(
        "-t", type=int, nargs=1, help="Amount of time in minutes to run the server for", default=DEFAULT_TIME)

    args = parser.parse_args()

    """
    Acquire options for the ArgParser
    """
    address = "" if isinstance(args.a, list) and args.a[0] == "all" else \
        (args.a if args.a == DEFAULT_ADDRESS else args.a[0])
    port = int(args.p[0] if args.p != DEFAULT_PORT else DEFAULT_PORT)
    clients = int(args.c[0] if isinstance(args.c, list) else args.c)
    time = int(args.t[0] if isinstance(args.t, list) else args.t)

    """
    Start the server
    """
    server = SharingServer(address=(address, port), max_clients=clients)
    server.start()

    if time > 0:
        start_time = datetime.now()
        try:
            while divmod((datetime.now() - start_time).total_seconds(), 60)[0] < time:
                pass
        except KeyboardInterrupt:
            print("[Server] Actions interrupted by user.")
        server.stop()
    exit()

