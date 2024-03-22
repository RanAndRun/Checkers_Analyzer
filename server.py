import socket
from config import DISCONNECT_MSG, BUFFER_SIZE, SERVER_ADDRESS


DISCONNECT_MSG = "DISCONNECT!"
BUFFER_SIZE = 2048


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(2)
    print("Server started. Waiting for players...")

    white_player_socket, _ = server_socket.accept()
    print("White player connected")
    white_player_socket.send("True".encode())

    black_player_socket, _ = server_socket.accept()
    print("Black player connected")
    black_player_socket.send("False".encode())

    players = [white_player_socket, black_player_socket]

    connected = True
    while connected:
        for player_socket in players:
            try:
                player_socket.setblocking(False)
                msg = player_socket.recv(BUFFER_SIZE).decode()
                if msg:
                    print("Message received:", msg)
                    # Relay message to the other player
                    for p in players:
                        if p != player_socket:
                            p.send(msg.encode())
                    if msg == DISCONNECT_MSG:
                        connected = False
                        break
            except BlockingIOError:
                continue
            except Exception as e:
                print(f"Error: {e}")
                connected = False
                break

    for p in players:
        p.close()
    server_socket.close()


start_server()
