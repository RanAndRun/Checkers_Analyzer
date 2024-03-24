import socket

from Config import *
from time import sleep


class Network:
    def __init__(self, server_address=SERVER_ADDRESS):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.port = server_address[1]
        self.addr = server_address
        self.is_white = None  # Initialize ID to None

    def connect(self):
        print("Connecting to server...", self.is_white)
        try:
            if self.is_white is None:
                self.server.setblocking(True)  # Temporarily set to blocking
                self.server.connect(self.addr)
                print("Connected to server")
                self.is_white = self.server.recv(BUFFER_SIZE).decode()
                print("Received:", self.is_white)
                self.server.setblocking(False)  # Set back to non-blocking
            return self.is_white
        except Exception as e:
            print("Connection error:", e)

    def send(self, data):
        try:
            if self.is_white is not None:
                # Convert data to string and encode
                self.server.send(str(data).encode())
                print("Data sent:", data)
        except socket.error as e:
            print("Problem sending data:", e)

    def receive(self):
        try:
            if self.is_white is not None:
                msg = self.server.recv(BUFFER_SIZE).decode()
                return msg
        except BlockingIOError:
            # No data available to read at this moment
            return None
        except socket.error as e:
            print("Problem receiving data:", e)
            return None

    def close(self):
        if self.is_white is not None:
            try:
                # Send disconnect message and wait for acknowledgment
                self.send(DISCONNECT_MSG)
                while True:
                    ack = self.server.recv(BUFFER_SIZE).decode()
                    if ack == DISCONNECT_ACK_MSG:
                        break
            except socket.error as e:
                if e.errno != 10035:  # Ignore WSAEWOULDBLOCK
                    print("Error during disconnection:", e)

            finally:
                self.server.close()
                self.is_white = None

    def shutdown(self):
        try:
            self.server.shutdown(socket.SHUT_RDWR)
            self.is_white = None
        except socket.error as e:
            print("Error during shutdown:", e)
