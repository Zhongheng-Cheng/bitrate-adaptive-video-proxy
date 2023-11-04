import socket
import time

class Connection(object):
    def __init__(self):
        pass

    def bind_socket(self, bind_address):
        '''
        Input:
            bind_address: tuple, (ip, port)
        '''
        self.conn_socket.bind(bind_address)
        return
    
    def receive(self):
        '''
        Receive a message from conn_socket.
        '''
        message = self.conn_socket.recv(4096).decode()
        print(f"Proxy received from {self.address}: {message}")
        return message
    
    def send(self, message):
        '''
        Send a message to conn_socket.
        '''
        self.conn_socket.send(message.encode())
        return
    
    def connect_to_server(self, server_ip: str, server_port: int, fake_ip: str):
        '''
        Continuously try to connect server at 1 second interval.
        '''
        print("Connecting to server...")
        while True:
            try:
                self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if fake_ip:
                    self.bind_socket((fake_ip, 0))
                self.address = (server_ip, server_port)
                self.conn_socket.connect(self.address)
                break
            except ConnectionRefusedError:
                time.sleep(1)
            except Exception as e:
                print(e)
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