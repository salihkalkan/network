import socket
import threading


class Udp:
    remoteEndPoint = ('127.0.0.1', 0)
    data_listener_thread = 0
    is_data_listener_thread_alive = False
    is_opened = False

    # disardaki siniflarin fonksiyonlarini saklar
    data_received_functions = []

    def __init__(self):
        self.udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def open(self, listen_port, ip, send_port):
        self.remoteEndPoint = (ip, int(send_port))
        self.udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udpSocket.bind(('', int(listen_port)))
        self.is_data_listener_thread_alive = True
        self.data_listener_thread = threading.Thread(target=self.begin_to_receive)
        self.data_listener_thread.start()
        self.is_opened = True

    def close(self):
        self.udpSocket.close()
        self.is_data_listener_thread_alive = False
        if self.data_listener_thread.is_alive():
            self.data_listener_thread.join()
        self.is_opened = False

    def send(self, data):
        self.udpSocket.sendto(bytes(data, 'utf-8'), self.remoteEndPoint)
        print(data + " <-- Udpden gönderilen data")

    # diger siniflar fonksiyonlarini alip data_received_functions'in icinde saklar
    def add_data_received_function(self, data_receive_func):
        self.data_received_functions.append(data_receive_func)

    def begin_to_receive(self):
        try:
            while self.is_data_listener_thread_alive:
                data_address = self.udpSocket.recvfrom(1024)

                if data_address[0] == b'':
                    self.is_data_listener_thread_alive = False
                    self.udpSocket.close()
                    break

                # data geldikten sonra, disardaki siniflarin fonksiyonlarina, data'yi parametre olarak vererek cagirir
                for func in self.data_received_functions:
                    func(data_address[0])
        except socket.error:
            self.is_data_listener_thread_alive = False
            self.udpSocket.close()
            self.is_opened = False
