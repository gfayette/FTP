import os
import struct
import sys
from os import path
import socket
from _thread import *


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 0))
    server_socket.listen()
    print('The server is listening on', (socket.gethostbyname(socket.gethostname()),
                                         server_socket.getsockname()[1]))
    while True:
        try:
            socket_connection, address = server_socket.accept()
            print('Accepted connection from', address)
            start_new_thread(service_existing_connection, (socket_connection, address))
        except KeyboardInterrupt:
            break
    print('Closing server.')
    server_socket.close()
    sys.exit()


def service_existing_connection(socket_connection, address):
    while True:
        received_data = receive_message(socket_connection)
        if received_data == b'CLOSE_CONNECTION':
            print('Closing connection with', address)
            socket_connection.close()
            break
        elif received_data == b'LIST':
            list_cmd(socket_connection, address)
        elif received_data == b'RETRIEVE':
            retrieve_cmd(socket_connection, address)
        elif received_data == b'STORE':
            store_cmd(socket_connection, address)


def list_cmd(socket_connection, address):
    print('Sending file list to', address)
    files = [f for f in os.listdir('.')
             if os.path.isfile(f)]
    for f in files:
        send_message(socket_connection, f.encode())
    send_message(socket_connection, b'END_TRANSMISSION')


def retrieve_cmd(socket_connection, address):
    file_name = receive_message(socket_connection).decode()
    print('Sending', file_name, 'to', address)
    if not path.isfile(file_name):
        print("ERROR:", file_name, "was not found on the server")
        send_message(socket_connection, b'NOT_FOUND')
    else:
        with open(file_name, "rb") as f:
            for piece in read_in_chunks(f):
                send_message(socket_connection, piece)
            print(file_name, 'was successfully retrieved by', address)
    send_message(socket_connection, b'END_TRANSMISSION')


def store_cmd(socket_connection, address):
    file_name = receive_message(socket_connection).decode()
    print('Receiving', file_name, 'from', address)
    file_data = receive_in_chunks(socket_connection)
    f = open(file_name, "wb")
    f.write(file_data)
    f.close()
    print(file_name, 'was successfully stored on the server')


def send_message(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def receive_in_chunks(sock):
    received_chunk = receive_message(sock)
    message = b''
    while received_chunk != b'END_TRANSMISSION':
        message = message + received_chunk
        received_chunk = receive_message(sock)
    return message


def receive_message(sock):
    # Read message length and unpack it into an integer
    raw_msglen = receive_all(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return receive_all(sock, msglen)


def receive_all(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def read_in_chunks(file_object, chunk_size=1024000):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


if __name__ == "__main__":
    run_server()
