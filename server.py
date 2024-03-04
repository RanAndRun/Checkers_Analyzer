import socket

DISCONNECT_MSG = "DISCONNECT!"
HEADER = 64
FORMAT = "utf-8"


def send(msg: str, client: socket.socket):
    massage = msg.encode(FORMAT)
    msg_length = len(massage)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(massage)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ("localhost", 12345)
    server_socket.bind(server_address)

    server_socket.listen(2)
    print("Server started. Waiting for players...")

    white_player_socket, white_player_address = server_socket.accept()
    print("White player connected:", white_player_address)

    black_player_socket, black_player_address = server_socket.accept()
    print("Black player connected:", black_player_address)

    # Decide which player is white and which player is black
    white_player_socket.send(b"white")
    black_player_socket.send(b"black")


    connected = True
    while connected:
        msg_length = white_player_socket.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length)
            msg = white_player_socket.recv(msg_length).decode(FORMAT)
            print(f"[{white_player_address}]: {msg}")
            if msg == DISCONNECT_MSG:
                connected = False
                break

            white_player_socket.send("Msg received".encode(FORMAT))
            send(msg, black_player_socket)

        msg_length = black_player_socket.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length)
            msg = black_player_socket.recv(msg_length).decode(FORMAT)
            print(f"[{white_player_address}]: {msg}")
            if msg == DISCONNECT_MSG:
                connected = False
                break

            black_player_socket.send("Msg received".encode(FORMAT))
            send(msg, white_player_socket)

    # Close the server socket
    server_socket.close()


start_server()
