import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, pyqtSlot, Q_ARG, QDateTime

from MainView import Ui_MainWindow
from TcpServer import TcpServer
from TcpClient import TcpClient
from Udp import Udp
import threading
import socket


class MainViewController(QObject):
    Window = Ui_MainWindow()
    TcpServer = TcpServer()
    TcpClient = TcpClient()
    Udp = Udp()

    is_data_sender_thread_client_alive = False
    is_data_sender_thread_server_alive = False
    is_data_sender_thread_udp_alive = False

    def __init__(self, window):
        super().__init__()
        self.Window = window
        self.Window.ButonBaslat.clicked.connect(self.start_server)
        self.Window.ButonDurdur_Server.clicked.connect(self.stop_server)
        self.Window.ButonSendData_Server.clicked.connect(self.send_data_from_server)
        self.Window.ButonSendData_Client.clicked.connect(self.send_data_from_client)
        self.Window.ButonBaglanClient.clicked.connect(self.connect_to_server)
        self.Window.ButonBaglantKes_Client.clicked.connect(self.client_disconnect)
        self.Window.ButonSendingStop_Server.clicked.connect(self.server_stop_sending)
        self.Window.ButonSendingStop_Client.clicked.connect(self.client_stop_sending)

        self.Window.ButonBaslaUDP.clicked.connect(self.baslat_udp)
        self.Window.ButonDurdurUDP.clicked.connect(self.durdur_udp)
        self.Window.ButonSendData_UDP.clicked.connect(self.send_data_udp)
        self.Window.ButonSendingStop_UDP.clicked.connect(self.udp_stop_sending)

        self.Window.ButonDurdur_Server.setEnabled(False)
        self.Window.ButonBaglantKes_Client.setEnabled(False)

        self.Window.checkBoxServerDurum.setEnabled(False)
        self.Window.checkBoxClientDurum.setEnabled(False)

        self.Window.ButonSendingStop_Server.setEnabled(False)
        self.Window.ButonSendingStop_Client.setEnabled(False)

        self.Window.ButonDurdurUDP.setEnabled(False)
        self.Window.ButonSendingStop_UDP.setEnabled(False)

        # data gelince haber ver
        self.TcpServer.add_data_received_function(self.on_server_receive_data)
        self.TcpClient.add_data_received_function(self.on_client_receive_data)
        self.Udp.add_data_received_function(self.on_udp_receive_data)
        self.TcpClient.add_connection_lost_function(self.on_client_connection_lost)

        self.data_sender_thread_server = threading.Thread(target=self.send_data_periodically_server,
                                                          args=[self.Window.textEditDataServer.toPlainText()])
        self.data_sender_thread_client = threading.Thread(target=self.send_data_periodically_client,
                                                          args=[self.Window.textEditData_Client.toPlainText()])
        self.data_sender_thread_udp = threading.Thread(target=self.send_data_periodically_udp,
                                                          args=[self.Window.textEditData_UDP.toPlainText()])

    def start_server(self):
        self.TcpServer.start(self.Window.textEdit_Port_Server.toPlainText())
        self.Window.ButonBaslat.setEnabled(False)
        self.Window.ButonDurdur_Server.setEnabled(True)
        print("Başlatıldı.")

    def stop_server(self):
        self.TcpServer.stop()
        self.Window.ButonBaslat.setEnabled(True)
        self.Window.ButonDurdur_Server.setEnabled(False)
        print("Server durduruldu.")
        self.Window.checkBoxServerDurum.setChecked(False)
        self.server_stop_sending()

    @pyqtSlot(str)
    def invoke_change_textBrowserIncoming_Client(self, text):
        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserIncoming_Client.append("Zaman: " + current_time + " | Data: " + text)

    def on_client_receive_data(self, data):
        print("Client a data geldi")
        QtCore.QMetaObject.invokeMethod(self, "invoke_change_textBrowserIncoming_Client", Qt.QueuedConnection,
                                        Q_ARG(str, data.decode('utf-8')))

    @pyqtSlot(str)
    def invoke_change_textBrowserIncoming_Server(self, text):
        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserIncoming_Server.append("Zaman: " + current_time + " | Data: " + text)

    def on_server_receive_data(self, data):
        print("Server a data geldi")
        QtCore.QMetaObject.invokeMethod(self, "invoke_change_textBrowserIncoming_Server", Qt.QueuedConnection,
                                        Q_ARG(str, data.decode('utf-8')))

    @pyqtSlot()
    def invoke_client_connection_lost(self):
        self.Window.ButonBaglanClient.setEnabled(True)
        self.Window.ButonBaglantKes_Client.setEnabled(False)
        self.Window.checkBoxClientDurum.setChecked(False)
        self.client_stop_sending()

    def on_client_connection_lost(self, tcp_client):
        QtCore.QMetaObject.invokeMethod(self, "invoke_client_connection_lost", Qt.QueuedConnection)

    def connect_to_server(self):
        try:
            self.TcpClient.connect(self.Window.textEditClientIP.toPlainText(), self.Window.textEdit_Port_Client.toPlainText())
            self.Window.ButonBaglanClient.setEnabled(False)
            self.Window.ButonBaglantKes_Client.setEnabled(True)
            print("Client servera bağlandı.")
            self.Window.checkBoxClientDurum.setChecked(True)
        except:
            print("Client servera bağlanamadı!")

    def client_disconnect(self):
        self.TcpClient.disconnect()
        self.Window.ButonBaglanClient.setEnabled(True)
        self.Window.ButonBaglantKes_Client.setEnabled(False)
        print("Client bağlatısı kesildi.")
        self.Window.checkBoxClientDurum.setChecked(False)
        self.client_stop_sending()

    def send_data_from_server(self):
        try:
            self.TcpServer.send(self.Window.textEditDataServer.toPlainText())
        except socket.error:
            print("Connection is lost")

        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserOutgoing_Server.append("Zaman: " + current_time + " | Data: " + self.Window.textEditDataServer.toPlainText())
        print("serverdan data gönderildi.")

        if self.Window.checkBoxPeriyodikServer.isChecked():
            self.Window.ButonSendingStop_Server.setEnabled(True)
            self.Window.ButonSendData_Server.setEnabled(False)
            self.Window.checkBoxPeriyodikServer.setEnabled(False)

            self.is_data_sender_thread_server_alive = True
            self.data_sender_thread_server = threading.Thread(target=self.send_data_periodically_server,
                                                              args=[self.Window.textEditDataServer.toPlainText()])
            self.data_sender_thread_server.start()

    def send_data_periodically_server(self, data):
        while self.is_data_sender_thread_server_alive:
            time.sleep(float(self.Window.textEdit_ServerPeriyot.toPlainText()))

            if len(self.TcpServer.connectedClients) > 0 and self.TcpServer.is_started:
                QtCore.QMetaObject.invokeMethod(self, "invoke_change_textBrowserOutgoing_Server", Qt.QueuedConnection,
                                                Q_ARG(str, data))
            try:
                self.TcpServer.send(data)
            except socket.error:
                self.is_data_sender_thread_server_alive = False
                print("Connection is lost")
            print("serverdan data gönderildi.")

    @pyqtSlot(str)
    def invoke_change_textBrowserOutgoing_Server(self, text):
        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserOutgoing_Server.append(
            "Zaman: " + current_time + " | Data: " + text)

    def server_stop_sending(self):
        self.Window.ButonSendingStop_Server.setEnabled(False)
        self.Window.ButonSendData_Server.setEnabled(True)
        self.Window.checkBoxPeriyodikServer.setEnabled(True)

        self.is_data_sender_thread_server_alive = False
        if self.data_sender_thread_server.is_alive():
            self.data_sender_thread_server.join()

    def client_stop_sending(self):
        self.Window.ButonSendingStop_Client.setEnabled(False)
        self.Window.ButonSendData_Client.setEnabled(True)
        self.Window.checkBoxPeriyodik_Client.setEnabled(True)

        self.is_data_sender_thread_client_alive = False
        if self.data_sender_thread_client.is_alive():
            self.data_sender_thread_client.join()

    def send_data_from_client(self):
        try:
            self.TcpClient.send(self.Window.textEditData_Client.toPlainText())
        except socket.error:
            print("Connection is lost")

        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserOutgoing_Client.append("Zaman: " + current_time + " | Data: " + self.Window.textEditData_Client.toPlainText())
        print("clientdan data gönderildi.")

        if self.Window.checkBoxPeriyodik_Client.isChecked():
            self.Window.ButonSendingStop_Client.setEnabled(True)
            self.Window.ButonSendData_Client.setEnabled(False)
            self.Window.checkBoxPeriyodik_Client.setEnabled(False)

            self.is_data_sender_thread_client_alive = True
            self.data_sender_thread_client = threading.Thread(target=self.send_data_periodically_client,
                                                              args=[self.Window.textEditData_Client.toPlainText()])
            self.data_sender_thread_client.start()

    def send_data_periodically_client(self, data):
        while self.is_data_sender_thread_client_alive:
            time.sleep(float(self.Window.textEditClientPeriyot.toPlainText()))

            if self.TcpClient.is_connected:
                QtCore.QMetaObject.invokeMethod(self, "invoke_change_textBrowserOutgoing_Client", Qt.QueuedConnection,
                                                Q_ARG(str, data))
            try:
                self.TcpClient.send(data)
            except socket.error:
                self.is_data_sender_thread_client_alive = False
                print("Connection is lost")
            print("clientdan data gönderildi.")

    def send_data_periodically_udp(self, data):
        while self.is_data_sender_thread_udp_alive:
            time.sleep(float(self.Window.textEditUDPPeriyot.toPlainText()))

            if self.Udp.is_opened:
                QtCore.QMetaObject.invokeMethod(self, "invoke_change_textBrowserOutgoing_Udp", Qt.QueuedConnection,
                                                Q_ARG(str, data))
            try:
                self.Udp.send(data)
            except socket.error:
                self.is_data_sender_thread_udp_alive = False

    @pyqtSlot(str)
    def invoke_change_textBrowserOutgoing_Udp(self, text):
        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserOutgoingUDP.append(
            "Zaman: " + current_time + " | Data: " + text)

    @pyqtSlot(str)
    def invoke_change_textBrowserOutgoing_Client(self, text):
        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserOutgoing_Client.append(
            "Zaman: " + current_time + " | Data: " + text)

    def baslat_udp(self):
        self.Udp.open(self.Window.textEdit_ListenPort_UDP.toPlainText(), self.Window.textEdit_IP_UDP.toPlainText(),
                      self.Window.textEdit_SendPort_UDP.toPlainText())
        self.Window.ButonBaslaUDP.setEnabled(False)
        self.Window.ButonDurdurUDP.setEnabled(True)

    def durdur_udp(self):
        self.Udp.close()
        self.Window.ButonBaslaUDP.setEnabled(True)
        self.Window.ButonDurdurUDP.setEnabled(False)
        self.udp_stop_sending()
        print("udp durduruldu")

    def send_data_udp(self):
        try:
            self.Udp.send(self.Window.textEditData_UDP.toPlainText())
        except socket.error:
            print("Udp is closed")

        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserOutgoingUDP.append("Zaman: " + current_time + " | Data: " + self.Window.textEditData_UDP.toPlainText())
        print("data udp den gönderildi")

        if self.Window.checkBoxPeriyodik_UDP.isChecked():
            self.Window.ButonSendingStop_UDP.setEnabled(True)
            self.Window.ButonSendData_UDP.setEnabled(False)
            self.Window.checkBoxPeriyodik_UDP.setEnabled(False)

            self.is_data_sender_thread_udp_alive = True
            self.data_sender_thread_udp = threading.Thread(target=self.send_data_periodically_udp,
                                                           args=[self.Window.textEditData_UDP.toPlainText()])
            self.data_sender_thread_udp.start()

    @pyqtSlot(str)
    def invoke_change_textBrowserIncomingUDP(self, text):
        current_time = QDateTime.currentDateTime().toString()
        self.Window.textBrowserIncomingUDP.append("Zaman: " + current_time + " | Data: " + text)

    def on_udp_receive_data(self, data):
        print("Udp ye data geldi")
        QtCore.QMetaObject.invokeMethod(self, "invoke_change_textBrowserIncomingUDP", Qt.QueuedConnection,
                                        Q_ARG(str, data.decode('utf-8')))

    def udp_stop_sending(self):
        self.Window.ButonSendingStop_UDP.setEnabled(False)
        self.Window.ButonSendData_UDP.setEnabled(True)
        self.Window.checkBoxPeriyodik_UDP.setEnabled(True)

        self.is_data_sender_thread_udp_alive = False
        if self.data_sender_thread_udp.is_alive():
            self.data_sender_thread_udp.join()
