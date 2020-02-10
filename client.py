import time
import socket

message1 = b'Message 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from client'
message2 = b'Message 2'
chunk_size = 24


def main():
    a_socket = start_connection('192.168.0.11', 37777, message1)
    time.sleep(1)
    send(message1, a_socket)
    receive(a_socket)
    time.sleep(1)
    a_socket.send(b'close_connection')
    a_socket.close()


def start_connection(host, port, message):
    print('starting connection to', host, ':', port)
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((host, port))
    return new_socket


def send(message, sock):
    total_bytes_sent = 0
    sock.send(b'start_transmission')
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
    print('received', message.decode(), 'from server')


main()
