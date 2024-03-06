import socket
import pickle

HEADER = 64
FORMAT = "utf-8"


class Network:
    def __init__(self, server_address=("localhost", 12345)):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.addr = server_address
        self.id = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            message_length = self.client.recv(HEADER).decode(FORMAT)
            if message_length:
                message_length = int(message_length)
                return pickle.loads(self.client.recv(message_length))
        except Exception as e:
            print(e)

    def send(self, data):
        try:
            serialized_data = pickle.dumps(data)
            send_length = str(len(serialized_data)).encode(FORMAT)
            send_length += b" " * (HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(serialized_data)
            message_length = self.client.recv(HEADER).decode(FORMAT)
            if message_length:
                message_length = int(message_length)
                return pickle.loads(self.client.recv(message_length))
        except socket.error as e:
            print(e)

    def close(self):
        self.client.close()
