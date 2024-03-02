import socket
import pickle
from MoveNode import MoveNode 


def start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ("localhost", 12345)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(2)
    print("Server started. Waiting for players...")

    # Accept the first client connection
    white_player_socket, white_player_address = server_socket.accept()
    print("White player connected:", white_player_address)

    # Accept the second client connection
    black_player_socket, black_player_address = server_socket.accept()
    print("Black player connected:", black_player_address)

    # Decide which player is white and which player is black
    white_player_socket.sendall(b"white")
    black_player_socket.sendall(b"black")

    # Start forwarding moves between players
    while True:
        # Receive a move from the white player
        white_move = pickle.loads(white_player_socket.recv(1024))
        print("Received move from white player:", white_move.__dict__)

        # Forward the move to the black player
        black_player_socket.sendall(pickle.dumps(white_move))

        # Receive a move from the black player
        black_move = pickle.loads(black_player_socket.recv(1024))
        print("Received move from black player:", black_move.__dict__)

        # Forward the move to the white player
        white_player_socket.sendall(pickle.dumps(black_move))

    # Close the server socket
    server_socket.close()


start_server()
