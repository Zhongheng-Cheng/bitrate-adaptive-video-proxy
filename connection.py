import socket
import time

class Connection(object):
    def __init__(self, type: str):
        if type == "UDP":
            self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.type = type
        self.address = ('', 0)
        return
    
    def set_address(self, ip: str, port: int):
        self.address = (ip, port)
        return
    
    def receive(self):
        '''
        Receive a message from conn_socket.
        '''
        if self.type == "TCP":
            message = self.conn_socket.recv(4096).decode()
            return message
        
        elif self.type == "UDP":
            message, server_address = self.conn_socket.recvfrom(2048)
            message = message
            return message, server_address
    
    def send(self, message):
        '''
        Send a message to conn_socket.
        '''
        if self.type == "TCP":
            self.conn_socket.send(message.encode())
            return
        
        elif self.type == "UDP":
            self.conn_socket.sendto(message, self.address)
            return
    
    def connect_to_server(self, server_ip: str, server_port: int, fake_ip: str = None):
        '''
        Continuously try to connect server at 1 second interval.
        '''
        while True:
            try:
                self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if fake_ip:
                    self.conn_socket.bind((fake_ip, 0))
                self.address = (server_ip, server_port)
                print(f"Connecting to server at {self.address}")
                self.conn_socket.connect(self.address)
                break
            except ConnectionRefusedError:
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(10)
        print("Successfully connected to server.")
        return
    
    def listen_to_connection(self, listen_port: int):
        '''
        Await a client to connect. Queueing up to 10 clients.
        '''
        # binding listening socket
        listen_address = ('', listen_port)
        socket_listening = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_listening.bind(listen_address)
        
        # listen for client connection
        socket_listening.listen(10)
        print("The proxy is ready to receive...")
        client_socket, client_address = socket_listening.accept()

        # client connect and init
        self.address = client_address
        self.conn_socket = client_socket
        print(f"Connection established with {client_address}.")
        return
    
    def close(self):
        self.conn_socket.close()
        return