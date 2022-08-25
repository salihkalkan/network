import socket
import threading

from RemoteTcpClientController import RemoteTcpClientController


class TcpServer:
    serverSocket = 0
    connectedClients = []
    client_listener_thread = 0
    is_client_listener_thread_alive = False
    is_started = False

    # disardaki siniflarin fonksiyonlarini saklar
    data_received_functions = []

    def __init__(self):
        self.serverSocket = socket.socket()

    def start(self, port):
        s = self.serverSocket = socket.socket()
        s.bind(('', int(port)))
        s.listen(5)

        # istemcileri kabul et
        self.is_client_listener_thread_alive = True
        self.client_listener_thread = threading.Thread(target=self.begin_to_accept_clients)
        self.client_listener_thread.start()
        self.is_started = True

    def begin_to_accept_clients(self):
        try:
            while self.is_client_listener_thread_alive:
                client_socket, addr = self.serverSocket.accept()
                self.connectedClients.append(RemoteTcpClientController(self, client_socket, addr))
                print("Server a client baglandi")
        except socket.error:
            self.is_client_listener_thread_alive = False

    def send(self, data):
        for connectedClientController in self.connectedClients:
            try:
                connectedClientController.clientSocket.send(bytes(data, 'utf-8'))
            except socket.error:
                self.on_connection_lost(connectedClientController)

    def stop(self):
        for connectedClientController in self.connectedClients:
            connectedClientController.clientSocket.close()
        self.serverSocket.close()
        self.is_client_listener_thread_alive = False
        if self.client_listener_thread.is_alive():
            self.client_listener_thread.join()
        self.is_started = False

    # diger siniflar fonksiyonlarini alip data_received_functions'in icinde saklar
    def add_data_received_function(self, data_receive_func):
        self.data_received_functions.append(data_receive_func)

    def on_data_received(self, data):
        # data geldikten sonra, disardaki siniflarin fonksiyonlarina, data'yi parametre olarak vererek cagirir
        for func in self.data_received_functions:
            func(data)

    def on_connection_lost(self, remote_tcp_client):
        print("baglanti koptu")
        self.connectedClients.remove(remote_tcp_client)

