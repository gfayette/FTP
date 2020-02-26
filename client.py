# Group members: George, Kyle and Dylan
# version 1.0 2-17-2020
# CIS 457 10
# Prof. Bhuse
# Files: client.py
# Purpose: to have a client issue commands to a server until client terminates connection by sending 'QUIT'
# Tested with 109MB across different devices with multiple clients connected
import struct
import sys
import time
import socket
import os
from os import path
import math


# Main method used to listen to user input and call functions
def main():
    socket_connection = None
    print("Enter HELP for a list of commands")
    while True:
        user_input = input("Enter a command: ")
        user_input_arr = user_input.split()
        command = user_input_arr[0]
        if command.upper() == "CONNECT":
            socket_connection = start_connection(user_input_arr)  # attempting to connect to a specified server
        elif command.upper() == "QUIT":
            quit_cmd(socket_connection)
        elif command.upper() == "HELP":
            help_cmd()
        elif socket_connection is None:
            print("No connection has been made.  You must first connect to a "
                  "server with the CONNECT command before issuing other commands")
        else:
            if command.upper() == "LIST":  # after connection is made, listens for commands to call functions
                list_cmd(socket_connection)
            elif command.upper() == "RETRIEVE":
                retrieve_cmd(socket_connection, user_input_arr)
            elif command.upper() == "STORE":
                store_cmd(socket_connection, user_input_arr)
            else:
                print(command, "is not a valid command.  Enter HELP for a list of all commands")


# Function that sends the list command to the server and reads in the servers output
def list_cmd(socket_connection):
    send_msg(socket_connection, b'LIST')  # sending list command to server
    num_files = struct.unpack('>I', receive_message(socket_connection))[0]
    while num_files > 0:
        received_chunk = receive_message(socket_connection)
        print(received_chunk.decode())  # showing the server output
        num_files = num_files - 1


# Function that requests a file from the server to be stored on the client
def retrieve_cmd(socket_connection, user_input_arr):
    if len(user_input_arr) != 2:  # Checks to see if there is a parameter
        print("ERROR: The RETRIEVE command requires a file name as input")
        return
    file_name = user_input_arr[1]
    print('Retrieving', file_name, 'from server')
    send_msg(socket_connection, b'RETRIEVE')  # sending retrieve command with file name
    send_msg(socket_connection, file_name.encode())
    response = receive_message(socket_connection)
    if response == b'NOT_FOUND':  # returned if file isn't on server
        print("ERROR:", file_name, "was not found on the server")
        return
    num_chunks = struct.unpack('>I', receive_message(socket_connection))[0]
    f = open(file_name, "wb")
    while num_chunks > 0:
        received_chunk = receive_message(socket_connection)
        f.write(received_chunk)
        num_chunks = num_chunks - 1
    f.close()
    print(file_name, "was successfully retrieved from the server")


# Function to send a file to the server to be stored
def store_cmd(socket_connection, user_input_arr, chunk_size=1024000):
    if len(user_input_arr) != 2:  # checks to see if there is a parameter
        print("ERROR: The STORE command requires a file name as input")
        return
    file_name = user_input_arr[1]
    if not path.isfile(file_name):  # checks to see if file is on client
        print("ERROR:", file_name, "was not found in your file system")
        return
    print('Storing', file_name, 'on the server')
    send_msg(socket_connection, b'STORE')
    send_msg(socket_connection, file_name.encode())  # sending file to server
    num_chunks = math.ceil(os.path.getsize(file_name)/chunk_size)
    send_msg(socket_connection, struct.pack('>I', num_chunks))
    with open(file_name, "rb") as f:
        for piece in read_in_chunks(f, chunk_size):
            send_msg(socket_connection, piece)


# Function that displays usable commands and functionality
def help_cmd():
    print(
        " 1. CONNECT <server name/IP address> <server port>: This command allows a client to connect to a server. The arguments are the IP address of the server and the port number on which the server is listening for connections.\n",
        "2. LIST: When this command is sent to the server, the server returns a list of the files in the current directory on which it is executing. The client should get the list and display it on the screen.\n",
        "3. RETRIEVE <filename>: This command allows a client to get a file specified by its filename from the server.\n",
        "4. STORE <filename>: This command allows a client to send a file specified by its filename to the server.\n",
        "5. QUIT: This command allows a client to terminate the control connection. On receiving this command, the client should send it to the server and terminate the connection. When the ftp_server receives the quit command it should close its end of the connection.\n")


# Function that sends a closing notification to server and closes connection
def quit_cmd(socket_connection):
    if socket_connection is not None:
        print('Closing connection with server')
        send_msg(socket_connection, b'CLOSE_CONNECTION')  # Sending closing message to server
        time.sleep(1)
        socket_connection.close()      # Closing on clients end
    print('Exiting')
    sys.exit()


# Function to begin a connection with server
def start_connection(user_input_arr):
    if len(user_input_arr) != 3:  # checks for proper amount of parameters
        print("The CONNECT command requires the servers IP address along with the server port number \n"
              "CONNECT <server name/IP address> <server port>")
        return None
    host = user_input_arr[1]        # initializes host and port of server
    port = user_input_arr[2]
    if not is_int(port) and 0 <= int(port) <= 65535:        # checks to see if it's a valid port
        print("Port number must be a valid integer from 0 to 65535: ", port)
        return None
    new_socket = None
    try:    # creates socket to communicate with server
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect((host, int(port)))
        print("Connection to", (host, port), "was made successfully")
    except Exception:           # if connection is unsuccessful
        print("Connection to", (host, port), "was unsuccessful")
    time.sleep(1)
    return new_socket


# Helper function to check if value is an integer
def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


# Function to send messages to server
def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


# Function to receive message from the socket
def receive_message(sock):
    # Read message length and unpack it into an integer
    raw_msglen = receive_all(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return receive_all(sock, msglen)


# Helper function to receive_message for n bytes or return None if EOF is hit
def receive_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


# Helper function to get read in chunks
def read_in_chunks(file_object, chunk_size):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


# Used to run client
if __name__ == "__main__":
    main()
