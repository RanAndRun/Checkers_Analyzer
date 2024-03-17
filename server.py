import socket
import pickle


DISCONNECT_MSG = "DISCONNECT!"
BUFFER_SIZE = 2048


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("10.100.102.33", 12345)
    server_socket.bind(server_address)

    server_socket.listen(2)
    print("Server started. Waiting for players...")

    white_player_socket, white_player_address = server_socket.accept()
    print("White player connected:", white_player_address)

    white_player_socket.send(pickle.dumps(True))

    black_player_socket, black_player_address = server_socket.accept()
    print("Black player connected:", black_player_address)

    black_player_socket.send(pickle.dumps(False))

    # Send initial color information to both players

    connected = True
    while connected:
        try:
            msg = pickle.loads(white_player_socket.recv(BUFFER_SIZE))
            print(f"[{white_player_address}]: {msg}")

            black_player_socket.send(pickle.dumps(msg))

            if msg == DISCONNECT_MSG:
                connected = False
                break

            msg = pickle.loads(black_player_socket.recv(BUFFER_SIZE))
            print(f"[{black_player_address}]: {msg}")

            white_player_socket.send(pickle.dumps(msg))

            if msg == DISCONNECT_MSG:
                connected = False
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    server_socket.close()


start_server()
