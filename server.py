import socket
from _thread import *

chunk_size = 24


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print('listening on', (host, port))
    while True:
        conn, addr = server_socket.accept()  # Should be ready to read
        print('accepted connection from', addr)
        start_new_thread(service_existing_connection, (conn, addr))


def service_existing_connection(connection, address):
    print('servicing', address)
    while True:
        received_data = connection.recv(1024)
        if received_data:
            if received_data.decode() == 'close_connection':
                print('closing connection')
                connection.close()
                break
            if received_data.decode() == 'start_transmission':
                print('receiving transmission')
                message = receive(connection)
                send(message, connection)


def send(message, sock):
    total_bytes_sent = 0
    while len(message) > 0:
        message_chunk = message[:chunk_size]
        bytes_sent = sock.send(message_chunk)
        print('Sending ', bytes_sent, ' bytes')
        message = message[bytes_sent:]
        total_bytes_sent = total_bytes_sent + bytes_sent
    print('Total bytes sent: ', total_bytes_sent)
    sock.send(b'end_transmission')


def receive(sock):
    received_chunk = sock.recv(chunk_size)
    message = b''
    while received_chunk.decode() != 'end_transmission':
        message = message + received_chunk
        print('Received ', len(received_chunk), ' bytes')
        received_chunk = sock.recv(chunk_size)
    print('received', message.decode(), 'from client')
    return message


start_server('35.40.127.168', 37777)
