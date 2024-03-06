import socket
import pickle


class Network:
    def __init__(self, server_address=("localhost", 12345)):
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
                    self.client.recv(2048)
                )  # Deserialize the received data
            except Exception as e:
                print(e)
        return self.id

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except socket.error as e:
            print(e)

    def receive(self):
        try:
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)

    def close(self):
        self.client.close()
