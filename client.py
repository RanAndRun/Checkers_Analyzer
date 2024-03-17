import socket


HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "DISCONNECT!"
SERVER = "localhost"
PORT = 12345
ADDR = (SERVER, PORT)


def send(msg: str, client: socket.socket):
    massage = msg.encode(FORMAT)
    msg_length = len(massage)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(massage)


def receive(client: socket.socket):
    msg_length = client.recv(HEADER)
    if msg_length:
        msg_length = int(msg_length)
        return client.recv(msg_length).decode(FORMAT)


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    print("connected to server, waiting for color...")

    color = receive(client)
    print(f"You are player {color}")

    if color == "black":
        print("Waiting for white player to move...")
        opponent_move = receive(client)
        print(f"[SERVER]: {opponent_move}")

    connected = True
    while connected:
        msg = input("Enter a message: ")
        if msg == DISCONNECT_MSG:
            send(DISCONNECT_MSG, client)
            connected = False
        else:
            send(msg, client)
            msg_recieved = receive(client)
            print(f"[SERVER]: {msg_recieved}")
