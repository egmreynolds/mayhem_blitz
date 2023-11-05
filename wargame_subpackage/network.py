import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: use env vars instead of hardcoding
        self.server = "127.0.0.1" #"192.168.0.197"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def receive(self):
        try:
            return pickle.loads(self.client.recv(2048*5))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)

    def send_to_server(self, msg):
        try:
            self.client.send(pickle.dumps(msg))
        except socket.error as e:
            print(e)