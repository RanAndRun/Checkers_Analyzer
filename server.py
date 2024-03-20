import socket
from config import DISCONNECT_MSG, BUFFER_SIZE, SERVER_ADDRESS

DISCONNECT_MSG = "DISCONNECT!"
BUFFER_SIZE = 2048


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)

    server_socket.listen(2)
    print("Server started. Waiting for players...")

    white_player_socket, white_player_address = server_socket.accept()
    print("White player connected:", white_player_address)

    # Sending color information as string
    white_player_socket.send("True".encode())

    black_player_socket, black_player_address = server_socket.accept()
    print("Black player connected:", black_player_address)

    # Sending color information as string
    black_player_socket.send("False".encode())

    connected = True
    while connected:
        try:
            msg = white_player_socket.recv(BUFFER_SIZE).decode()
            print(f"[{white_player_address}]: {msg}")
            print(msg)
            black_player_socket.send(msg.encode())

            if msg == DISCONNECT_MSG:
                connected = False
                break

            msg = black_player_socket.recv(BUFFER_SIZE).decode()
            print(f"[{black_player_address}]: {msg}")

            white_player_socket.send(msg.encode())

            if msg == DISCONNECT_MSG:
                connected = False
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    server_socket.close()


start_server()
