import socket
import pickle

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
                self.id = pickle.loads(
                    self.client.recv(BUFFER_SIZE)
                )  # Deserialize the received data
            except Exception as e:
                print(e)
        return self.id

    def send(self, data):
        try:
            if self.id is not None:
                self.client.send(pickle.dumps(data))
        except socket.error as e:
            print("problem sendoing data", e)

    def receive(self):
        try:
            if self.id is not None:
                msg = pickle.loads(self.client.recv(BUFFER_SIZE))
                if msg == DISCONNECT_MSG:
                    self.client.close()
                    self.id = None
                return msg
        except socket.error as e:
            # TODO handle this exception
            print("problem receinving data: ", e)

    def close(self):
        if self.id is not None:
            self.send(DISCONNECT_MSG)
            self.client.close()
            self.id = None
