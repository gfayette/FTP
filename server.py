import os
from os import path
import socket
import time
from _thread import *

chunk_size = 1024000


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 0))
    # server_socket.bind(('192.168.0.11', 37777))
    server_socket.listen()
    print('The server is listening on', (socket.gethostbyname(socket.gethostname()),
                                         server_socket.getsockname()[1]))
    while True:
        socket_connection, address = server_socket.accept()
        print("lmao cd")
        print('Accepted connection from', address)
        start_new_thread(service_existing_connection, (socket_connection, address))


def service_existing_connection(socket_connection, address):
    while True:
        received_data = socket_connection.recv(chunk_size)
        if received_data:
            if received_data == b'CLOSE_CONNECTION':
                print('Closing connection with', address)
                socket_connection.close()
                break
            elif received_data == b'LIST':
                list_cmd(socket_connection)
            elif received_data == b'RETRIEVE':
                retrieve_cmd(socket_connection)
            elif received_data == b'STORE':
                store_cmd(socket_connection)


def list_cmd(socket_connection):
    files = [f for f in os.listdir('.')
             if os.path.isfile(f)]
    for f in files:
        socket_connection.send(f.encode())
        time.sleep(.1)
    socket_connection.send(b'END_TRANSMISSION')


def retrieve_cmd(socket_connection):
    file_name = socket_connection.recv(chunk_size).decode()
    if not path.isfile(file_name):
        socket_connection.send(b'NOT_FOUND')
    else:
        with open(file_name, "rb") as f:
            for piece in read_in_chunks(f):
                socket_connection.send(piece)
    time.sleep(1)
    socket_connection.send(b'END_TRANSMISSION')


def store_cmd(socket_connection):
    print("store")
    file_name = socket_connection.recv(chunk_size).decode()
    file_data = receive(socket_connection)
    print("store")
    f = open(file_name, "wb")
    f.write(file_data)
    f.close()


def receive(sock):
    print("rec")
    received_chunk = sock.recv(chunk_size)
    message = b''
    while received_chunk != b'END_TRANSMISSION':
        print("recchunk", received_chunk)
        message = message + received_chunk
        received_chunk = sock.recv(chunk_size)
    print("rec")
    return message


def read_in_chunks(file_object):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


if __name__ == "__main__":
    start_server()
