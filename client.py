import time
import socket
from os import path

message1 = b'Message 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from clientMessage 1 from client'
message2 = b'Message 2'
chunk_size = 24


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
    socket_connection.send(b'LIST')
    socket_connection.send(b'end_transmission')
    print(receive(socket_connection))


def retrieve_cmd(socket_connection, user_input_arr):
    if len(user_input_arr) != 2:
        print("ERROR: The RETRIEVE command requires a file name as input")
        return
    file_name = user_input_arr[1]
    socket_connection.send(b'RETRIEVE')
    socket_connection.send(file_name)
    socket_connection.send(b'end_transmission')
    file_data = receive(socket_connection)
    if file_data == "NOT_FOUND":
        print("ERROR:", file_name, "was not found on the server")
        return
    f = open(file_name, "w")
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
    with open(file_name) as f:
        for piece in read_in_chunks(f):
            socket_connection.send(piece)
    socket_connection.send(b'end_transmission')


def help_cmd():
    print(
        " 1. CONNECT <server name/IP address> <server port>: This command allows a client to connect to a server. The arguments are the IP address of the server and the port number on which the server is listening for connections.\n",
        "2. LIST: When this command is sent to the server, the server returns a list of the files in the current directory on which it is executing. The client should get the list and display it on the screen.\n",
        "3. RETRIEVE <filename>: This command allows a client to get a file specified by its filename from the server.\n",
        "4. STORE <filename>: This command allows a client to send a file specified by its filename to the server.\n",
        "5. QUIT: This command allows a client to terminate the control connection. On receiving this command, the client should send it to the server and terminate the connection. When the ftp_server receives the quit command it should close its end of the connection.\n")


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def quit_cmd(socket_connection):
    socket_connection.send(b'close_connection')
    socket_connection.close()


def start_connection(user_input_arr):
    if len(user_input_arr) != 3:
        print("The CONNECT command requires the servers IP address along with the server port number \n"
              "CONNECT <server name/IP address> <server port>")
        return None
    host = user_input_arr[1]
    port = user_input_arr[2]
    if not isInt(port) and 0 <= int(port) <= 65535:
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


def isInt(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


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
    return message


if __name__ == "__main__":
    main()
