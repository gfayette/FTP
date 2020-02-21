# Group members: George Fayette, Kyle Russcher and Dylan Vannatter
# version 1.0 2-17-2019
# CIS 457 10
# Prof. Bhuse
# Files: server.py
# Purpose: to have a multi-threaded server receive and process commands from clients with further details below.
# On receiving a command, the server should parse the command and perform the appropriate action.
# The format of the commands is such as follows:

# 1.	CONNECT <server name/IP address> <server port>: This command allows a client to connect to a server.
# The arguments are the IP address of the server and the port number on which the server is listening for connections.

# 2.	LIST: When this command is sent to the server, the server returns a list of the files
# in the current directory on which it is executing. The client should get the list and display it on the screen.

# 3.	RETRIEVE <filename>: This command allows a client to get a file specified by its filename from the server.

# 4.	STORE <filename>: This command allows a client to send a file specified by its filename to the server.

# 5.	QUIT: This command allows a client to terminate the control connection.
# On receiving this command, the client should send it to the server and terminate the connection.
# When the ftp_server receives the quit command it should close its end of the connection.
import os
import struct
import sys
from os import path
import socket
import math
from _thread import *


# Function to get the server running on an address and port and listen for clients to connect
def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket for server
    server_socket.bind(('', 0))
    server_socket.listen()
    print('The server is listening on', (socket.gethostbyname(socket.gethostname()),
                                         server_socket.getsockname()[1]))
    while True:
        try:
            socket_connection, address = server_socket.accept()  # listening for client connection requests
            print('Accepted connection from', address)
            start_new_thread(service_existing_connection, (socket_connection, address))
        except KeyboardInterrupt:
            break
    print('Closing server.')
    server_socket.close()
    sys.exit()


# Function used to service a connection between a client and the server
def service_existing_connection(socket_connection, address):
    while True:
        received_data = receive_message(socket_connection)
        if received_data == b'CLOSE_CONNECTION':
            print('Closing connection with', address)  # closing connection with client
            socket_connection.close()
            break
        elif received_data == b'LIST':  # calling commands based on client requests
            list_cmd(socket_connection, address)
        elif received_data == b'RETRIEVE':
            retrieve_cmd(socket_connection, address)
        elif received_data == b'STORE':
            store_cmd(socket_connection, address)


# Function to list the files on the server to the client
def list_cmd(socket_connection, address):
    print('Sending file list to', address)
    files = [f for f in os.listdir('.')
             if os.path.isfile(f)]  # gathering all the files in the current directory
    num_files = len(files)
    send_message(socket_connection, struct.pack('>I', num_files))
    for f in files:
        send_message(socket_connection, f.encode())  # sending files to client


# Function used to retrieve a file from the server to the client
def retrieve_cmd(socket_connection, address, chunk_size=1024000):
    file_name = receive_message(socket_connection).decode()
    print('Retrieving', file_name)
    if not path.isfile(file_name):  # checks to see if file is on server
        print("ERROR:", file_name, "was not found on the server")
        send_message(socket_connection, b'NOT_FOUND')
    else:
        send_message(socket_connection, b'OK')
        num_chunks = math.ceil(os.path.getsize(file_name) / chunk_size)
        send_message(socket_connection, struct.pack('>I', num_chunks))
        with open(file_name, "rb") as f:
            for piece in read_in_chunks(f, chunk_size):
                send_message(socket_connection, piece)
        print(file_name, 'was successfully retrieved by', address)


# Function used to store a file from a client to the server
def store_cmd(socket_connection, address):
    file_name = receive_message(socket_connection).decode()  # reading in data from client
    print('Receiving', file_name, 'from', address)
    num_chunks = struct.unpack('>I', receive_message(socket_connection))[0]
    f = open(file_name, "wb")
    while num_chunks > 0:
        received_chunk = receive_message(socket_connection)
        f.write(received_chunk)
        num_chunks = num_chunks - 1
    f.close()
    print(file_name, 'was successfully stored on the server')


# Function to send data to client
def send_message(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


# Function to receive the message in chunks
def receive_in_chunks(sock):
    received_chunk = receive_message(sock)
    message = b''
    while received_chunk != b'END_TRANSMISSION':
        message = message + received_chunk
        received_chunk = receive_message(sock)
    return message


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
def read_in_chunks(file_object, chunk_size=1024000):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


# Used to run server
if __name__ == "__main__":
    run_server()
