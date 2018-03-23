"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from network.sharing.server import SharingServer
from network.minimap.server import MiniMapServer
import argparse

"""
Setup a SharingServer with command-line arguments. Available arguments:
-a: address to bind to
-p: port to accept connections on
-c: maximum amount of clients
-t: amount of time in minutes to run the network for
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
        "-a", type=str, nargs=1, help="Address to bind the network to, 'all' means all available",
        default=DEFAULT_ADDRESS)
    # Port
    parser.add_argument(
        "-p", type=int, nargs=1, help="Port to accept connections on", default=DEFAULT_PORT)
    # Clients
    parser.add_argument(
        "-c", type=str, nargs=1, help="Maximum amount of Clients to allow on the Server simultaneously",
        default=DEFAULT_CLIENTS)
    # Type
    parser.add_argument(
        "-t", type=str, nargs=1, help="Server type (sharing, minimap)", default="sharing")

    args = parser.parse_args()

    """
    Acquire options for the ArgParser
    """
    address = "" if isinstance(args.a, list) and args.a[0] == "all" else \
        (args.a if args.a == DEFAULT_ADDRESS else args.a[0])
    port = int(args.p[0] if args.p != DEFAULT_PORT else DEFAULT_PORT)
    clients = int(args.c[0] if isinstance(args.c, list) else args.c)
    type = args.t[0] if isinstance(args.t, list) else args.t

    """
    Start the network
    """
    if type == "sharing":
        server = SharingServer(address=(address, port), max_clients=clients)
    elif type == "minimap":
        server = MiniMapServer(address, port)
    else:
        raise ValueError("Invalid server type: {}".format(type))
    server.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()
    exit()


