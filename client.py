# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import socket
import vars
import time
import tkMessageBox
import hashlib

# This function takes a fileName and a readily created socket-object to send a CombatLog to a server
'''
Return values:
 0: File correctly sent
-1: The connection was lost while transferring the file
-2: The server could not parse one of the lines sent
-3: The server did not answer as expected
-4: The server did not answer at all
-5: The packet could not be sent
'''
def sendFile(fileName, userName, connectionObject):
    # Create received, a variable to store responses from the server
    received = None
    # Open the file as read-only
    fileObject = open(fileName, "r")
    # Read all the lines from this file
    lines = fileObject.readlines()
    # Prepare the progressbar in the GUI's shareTab
    vars.progressBar["maximum"] = len(lines)

    # Try to get a response from the server to check the connection
    connectionObject.send("Connection initialized by")
    connectionObject.send(userName)
    # Sleep for a very short time to wait for a response
    # time.sleep(0.01)
    # Read the server's response
    received = connectionObject.recv(64)

    # If the expected response was not given, stop the function
    if received != "Connection initialized":
        connectionObject.close()
        fileObject.close()
        return -3
    # Try to send the player's name, the filename and a hash of the file
    connectionObject.send(vars.playerName)
    connectionObject.send(vars.fileName)

    # Try to read the server's response
    received = connectionObject.recv(64)

    # If the expected response was not given, stop the function
    if received != "Send file":
        connectionObject.close()
        fileObject.close()
        return -3
    index = 0
    # Start the loop to send the lines of the file
    for line in lines:
        # Try to send a line
        connectionObject.send(line)
        # Sleep for a short amount of time
        # time.sleep(0.01)
        # If a response was received, the line was unparsable
        try:
            received = connectionObject.recv(64)
        except:
            pass
        finally:
            if received == "Line in file unparsable":
                fileObject.close()
                connectionObject.close()
                return -2
            # elif received == ""
            else:
                # If the server did send a response, but this response was not registered
                #  as an error, show a notice to the user
                tkMessageBox.showinfo("Notice", """A message was received from the
                 server, but it did not register as an error: %c""" % received)
        index += 1
        vars.progressBar["value"] = index
    # When the end of the file is reached, the server must be notified
    try:
        connectionObject.send("End of file")
    except:
        connectionObject.close()
        fileObject.close()
        return -5
    # Sleep for a short amount of time again
    time.sleep(0.01)
    # Try to read a response again
    try:
        received = connectionObject.recv(64)
        if received != "File received":
            connectionObject.close()
            fileObject.close()
            return -3
    except:
        connectionObject.close()
        fileObject.close()
        return -4
    # When the function gets to this point, the file was sent succesfully
    fileObject.close()
    connectionObject.close()
    return 0

# This function opens a connection to the server
def initConnection():
    try:
        socket.settimeout(100)
        connectionObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connectionObject.connect(vars.serverAddress)
    except:
        try:
            connectionObject.close()
        except:
            pass
        return None
    return connectionObject

# This function takes a file to send it to the server and does the user-interaction.
def send(fileName, userName):
    connectionObject = initConnection()
    if connectionObject == None:
        tkMessageBox.showerror("Error", "Connecting to the server over TCP/IP failed.")
        return
    else:
        if fileName == "":
            tkMessageBox.showerror("Error", "An empty file name was entered to send to the server")
            connectionObject.close()
            return -2
        else:
            fileObject = open(fileName, "r")
            returned = sendFile(fileName, userName, connectionObject)
            if returned == 0:
                tkMessageBox.showinfo("Notice", "The file was send successfully.")
                return
            elif returned == -1:
                 if tkMessageBox.askretrycancel("Error", "The connection was lost during transfer."):
                     send(fileName, userName)
                 else:
                    return
            elif returned == -2:
                tkMessageBox.showerror("Error", "A line in your file was unparsable for the server.")
                return
            elif returned == -3:
                if tkMessageBox.askretrycancel("Error", "The server did not return the expected response."):
                    send(fileName, userName)
                else:
                    return
            elif returned == -4:
                if tkMessageBox.askretrycancel("Error", "The server did not return a response."):
                    send(filename, userName)
                else:
                    return
            elif returned == -5:
                if tkMessageBox.askretrycancel("Error", "Could not send packet to the server."):
                    send(fileName, userName)
                else:
                    return
            else:
                tkMessageBox.showerror("Error", "An unknown error occurred.")
                return
