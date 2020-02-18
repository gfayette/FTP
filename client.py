import struct
import sys
import time
import socket
from os import path


def main():
    socket_connection = None
    print("Enter HELP for a list of commands")
    while True:
        user_input = input("Enter a command: ")
        user_input_arr = user_input.split()
        command = user_input_arr[0]
        if command.upper() == "CONNECT":
            socket_connection = start_connection(user_input_arr)
        elif socket_connection is None:
            print("No connection has been made.  You must first connect to a "
                  "server with the CONNECT command before issuing other commands")
        else:
            if command.upper() == "LIST":
                list_cmd(socket_connection)
            elif command.upper() == "RETRIEVE":
                retrieve_cmd(socket_connection, user_input_arr)
            elif command.upper() == "STORE":
                store_cmd(socket_connection, user_input_arr)
            elif command.upper() == "QUIT":
                quit_cmd(socket_connection)
            elif command.upper() == "HELP":
                help_cmd()
            else:
                print(command, "is not a valid command.  Enter HELP for a list of all commands")


def list_cmd(socket_connection):
    send_msg(socket_connection, b'LIST')
    while True:
        received_chunk = receive_message(socket_connection)
        if received_chunk == b'END_TRANSMISSION':
            break
        else:
            print(received_chunk.decode())


def retrieve_cmd(socket_connection, user_input_arr):
    if len(user_input_arr) != 2:
        print("ERROR: The RETRIEVE command requires a file name as input")
        return
    file_name = user_input_arr[1]
    print('Retrieving', file_name, 'from server')
    send_msg(socket_connection, b'RETRIEVE')
    send_msg(socket_connection, file_name.encode())
    file_data = receive_in_chunks(socket_connection)
    if file_data == b'NOT_FOUND':
        print("ERROR:", file_name, "was not found on the server")
        return
    f = open(file_name, "wb")
    f.write(file_data)
    f.close()
    print(file_name, "was successfully retrieved from the server")


def store_cmd(socket_connection, user_input_arr):
    if len(user_input_arr) != 2:
        print("ERROR: The STORE command requires a file name as input")
        return
    file_name = user_input_arr[1]
    if not path.isfile(file_name):
        print("ERROR:", file_name, "was not found in your file system")
        return
    print('Storing', file_name, 'on the server')
    send_msg(socket_connection, b'STORE')
    send_msg(socket_connection, file_name.encode())
    with open(file_name, "rb") as f:
        for piece in read_in_chunks(f):
            send_msg(socket_connection, piece)
    send_msg(socket_connection, b'END_TRANSMISSION')


def help_cmd():
    print(
        " 1. CONNECT <server name/IP address> <server port>: This command allows a client to connect to a server. The arguments are the IP address of the server and the port number on which the server is listening for connections.\n",
        "2. LIST: When this command is sent to the server, the server returns a list of the files in the current directory on which it is executing. The client should get the list and display it on the screen.\n",
        "3. RETRIEVE <filename>: This command allows a client to get a file specified by its filename from the server.\n",
        "4. STORE <filename>: This command allows a client to send a file specified by its filename to the server.\n",
        "5. QUIT: This command allows a client to terminate the control connection. On receiving this command, the client should send it to the server and terminate the connection. When the ftp_server receives the quit command it should close its end of the connection.\n")


def quit_cmd(socket_connection):
    send_msg(socket_connection, b'CLOSE_CONNECTION')
    time.sleep(1)
    socket_connection.close()
    print('Closing connection with server and exiting')
    sys.exit()


def start_connection(user_input_arr):
    if len(user_input_arr) != 3:
        print("The CONNECT command requires the servers IP address along with the server port number \n"
              "CONNECT <server name/IP address> <server port>")
        return None
    host = user_input_arr[1]
    port = user_input_arr[2]
    if not is_int(port) and 0 <= int(port) <= 65535:
        print("Port number must be a valid integer from 0 to 65535: ", port)
        return None
    new_socket = None
    try:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect((host, int(port)))
        print("Connection to", (host, port), "was made successfully")
    except Exception:
        print("Connection to", (host, port), "was unsuccessful")
    time.sleep(1)
    return new_socket


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def send_msg(sock, msg):
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
    main()
