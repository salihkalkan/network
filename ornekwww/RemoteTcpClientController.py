import socket
import threading


class RemoteTcpClientController:
    clientSocket = 0
    clientAddress = 0
    data_listener_thread = 0
    is_data_listener_thread_alive = False

    def __init__(self, owner_tcp_server, client_socket, addr):
        self.owner_tcp_server = owner_tcp_server
        self.clientSocket = client_socket
        self.clientAddress = addr

        # data yi al
        self.is_data_listener_thread_alive = True
        self.data_listener_thread = threading.Thread(target=self.begin_to_receive)
        self.data_listener_thread.start()

    def begin_to_receive(self):
        try:
            while self.is_data_listener_thread_alive:
                data = self.clientSocket.recv(1024)

                if data == b'':
                    self.is_data_listener_thread_alive = False
                    self.owner_tcp_server.on_connection_lost(self)
                    break

                # datayi server a gonder
                self.owner_tcp_server.on_data_received(data)
        except socket.error:
            self.is_data_listener_thread_alive = False
            self.owner_tcp_server.on_connection_lost(self)
