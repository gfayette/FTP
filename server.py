import socket
from _thread import *

chunk_size = 1024


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 0))
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
    # expects 'END_TRANSMISSION' then sends the files in the directory followed by 'END_TRANSMISSION'
    print('list')


def retrieve_cmd(socket_connection):
    # expects the file name followed by 'END_TRANSMISSION' then sends the requested file or 'NOT_FOUND'
    # followed by 'END_TRANSMISSION'
    print('retrieve', socket_connection.recv(chunk_size))


def store_cmd(socket_connection):
    # expects the file name followed by the file data followed by 'END_TRANSMISSION'
    print('store', socket_connection.recv(chunk_size))


def receive(sock):
    received_chunk = sock.recv(chunk_size)
    message = b''
    while received_chunk != b'END_TRANSMISSION':
        message = message + received_chunk
        print('Received ', len(received_chunk), ' bytes')
        received_chunk = sock.recv(chunk_size)
    print('received', message.decode(), 'from client')
    return message


if __name__ == "__main__":
    start_server()
