import socket
import hashlib
import sys
import thread

def client(connection, address):
    print "Connection from ", address


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("thrantasquadron.tk", 83))
    except:
        print "Binding to port failed"

    server.listen()
    while True:
        connection, address = server.accept()
        thread.start_new_thread(client(connection,address))

