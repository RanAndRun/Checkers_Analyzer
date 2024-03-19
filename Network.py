import socket

from config import DISCONNECT_MSG, BUFFER_SIZE, SERVER_ADDRESS


class Network:
    def __init__(self, server_address=SERVER_ADDRESS):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.port = server_address[1]
        self.addr = server_address
        self.id = None  # Initialize ID to None

    def connect(self):
        if self.id is None:  # Check if already connected
            try:
                self.client.connect(self.addr)
                # Receive and directly use the ID as a string
                self.id = self.client.recv(BUFFER_SIZE).decode()
            except Exception as e:
                print(e)
        return self.id

    def send(self, data):
        try:
            if self.id is not None:
                # Convert data to string and encode
                self.client.send(str(data).encode())
        except socket.error as e:
            print("Problem sending data:", e)

    def receive(self):
        try:
            if self.id is not None:
                msg = self.client.recv(BUFFER_SIZE).decode()
                if msg == DISCONNECT_MSG:
                    self.client.close()
                    self.id = None
                return msg
        except socket.error as e:
            print("Problem receiving data:", e)

    def close(self):
        if self.id is not None:
            self.send(DISCONNECT_MSG)
            self.client.close()
            self.id = None
