import socket
import time
import re

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
    
    def receive_http_header(self, socket_connection):
        response_header = b""
        while True:
            chunk = socket_connection.recv(4096)
            response_header += chunk
            if b'\r\n\r\n' in response_header:
                break
        header, payload = response_header.split(b'\r\n\r\n')
        return header.decode(), payload

    def get_content_length(self, http_header):
        # Use regular expressions to extract the Content-Length value
        content_length_match = re.search(r'Content-Length: (\d+)', http_header)
        if content_length_match:
            return int(content_length_match.group(1))
        else:
            return None

    def receive_http_response(self):

        response_header, response_payload = self.receive_http_header(self.conn_socket)
        content_length = self.get_content_length(response_header)

        if content_length is not None:
            while len(response_payload) < content_length:
                chunk = self.conn_socket.recv(min(4096, content_length - len(response_payload)))
                if not chunk:
                    break
                response_payload += chunk
        return response_header, response_payload, content_length
    
    def receive(self):
        '''
        Receive a message from conn_socket.
        '''
        if self.type == "TCP":
            message = self.conn_socket.recv(4096)
            # if message == b'':
            #     raise TypeError("Empty input")
            if message:
                header, payload = message.split(b'\r\n\r\n')
                return header.decode(), payload
            else:
                return b''
            
        
        elif self.type == "UDP":
            message, server_address = self.conn_socket.recvfrom(2048)
            return message, server_address
    
    def send(self, message):
        '''
        Send a message to conn_socket.
        '''
        if self.type == "TCP":
            self.conn_socket.send(message)
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
                # self.conn_socket.settimeout(5)
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
        # self.conn_socket.settimeout(5)
        print(f"Connection established with {client_address}.")
        return
    
    def close(self):
        self.conn_socket.close()
        return