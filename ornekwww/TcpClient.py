import socket
import threading


class TcpClient:
    clientSocket = 0
    data_listener_thread = 0
    is_data_listener_thread_alive = False
    is_connected = False

    # disardaki siniflarin fonksiyonlarini saklar
    data_received_functions = []
    connection_lost_functions = []

    def __init__(self):
        self.clientSocket = socket.socket()

    def connect(self, ip, port):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((ip, int(port)))
        self.is_data_listener_thread_alive = True
        self.data_listener_thread = threading.Thread(target=self.begin_to_receive)
        self.data_listener_thread.start()
        self.is_connected = True

    def disconnect(self):
        self.clientSocket.close()
        self.is_data_listener_thread_alive = False
        if self.data_listener_thread.is_alive():
            self.data_listener_thread.join()
        self.is_connected = False

    def send(self, data):
        self.clientSocket.send(bytes(data, 'utf-8'))
        print(data + " <-- Clienttan gönderilen data")

    # diger siniflar fonksiyonlarini alip data_received_functions'in icinde saklar
    def add_data_received_function(self, data_receive_func):
        self.data_received_functions.append(data_receive_func)

    def add_connection_lost_function(self, connection_lost_func):
        self.connection_lost_functions.append(connection_lost_func)

    def begin_to_receive(self):
        try:
            while self.is_data_listener_thread_alive:
                data = self.clientSocket.recv(1024)

                if data == b'':
                    self.is_data_listener_thread_alive = False
                    self.clientSocket.close()
                    break

                # data geldikten sonra, disardaki siniflarin fonksiyonlarina, data'yi parametre olarak vererek cagirir
                for func in self.data_received_functions:
                    func(data)
        except socket.error:
            self.is_data_listener_thread_alive = False
            self.clientSocket.close()
            self.is_connected = False
            for func in self.connection_lost_functions:
                func(self)
