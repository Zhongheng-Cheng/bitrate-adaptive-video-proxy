#!/usr/bin/env python3.10
import socket
import sys
import time

class Proxy(object):
    def __init__(self, listen_port):
        # binding listening socket
        self.listen_address = ('', int(listen_port))
        self.socket_listening = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_listening.bind(self.listen_address)
        return

    def connect_to_server(self, server_ip, fake_ip):
        '''
        Continuously try to connect server at 1 second interval.

        Input:
            server_ip: str
            fake_ip: str
        '''
        print("Connecting to server...")
        while True:
            try:
                self.server = InternetEntity((server_ip, 8080))
                self.server.bind_socket((fake_ip, 0))
                self.server.conn_socket.connect(self.server.address)
                break
            except Exception as e:
                time.sleep(1)
        print("Successfully connected to server.")
        return

    def listen_to_connection(self):
        '''
        Await a client to connect. Queueing up to 10 clients.
        '''
        # listen for client connection
        self.socket_listening.listen(10)
        print("The proxy is ready to receive...")
        client_socket, client_address = self.socket_listening.accept()

        # client connect and init
        self.client = InternetEntity(client_address, client_socket)
        print("Connection established with ", client_address)
        return 
    
    def receive_from(self, entity):
        '''
        Receive a message from an entity's socket.
        If the message length exceeds the recv buffer length, it keeps receiving until a '\n' appears.

        Input: 
            entity: <class 'InternetEntity'>
        '''
        is_end = False
        self.send_buffer = ''
        while not is_end:
            message = entity.conn_socket.recv(1024).decode()
            if message == '':
                raise
            self.send_buffer += message.split('\n')[0]
            if len(message) > 1:
                is_end = True
                self.send_buffer += '\n'
        print("Proxy received from %s: %s" % (entity.address, self.send_buffer))
        return
    
    def send_to(self, entity):
        '''
        Send a message to an entity's socket.
        
        Input: 
            entity: <class 'InternetEntity'>
        '''
        entity.conn_socket.send(self.send_buffer.encode())
        return
    

class InternetEntity(object):
    def __init__(self, address, conn_socket=None):
        '''
        Input:
            address: tuple, (ip, port)
            conn_socket: <class 'Socket'>, will create one if not entered
        '''
        self.address = address
        if not conn_socket:
            self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.conn_socket = conn_socket
        return
    
    def bind_socket(self, bind_address):
        '''
        Input:
            bind_address: tuple, (ip, port)
        '''
        self.conn_socket.bind(bind_address)
        return

if __name__ == '__main__':
    # read input
    listen_port, fake_ip, server_ip = sys.argv[1:]

    # proxy init
    proxy = Proxy(listen_port)
    
    # connect client and then server
    proxy.listen_to_connection()
    proxy.connect_to_server(server_ip, fake_ip)

    while True:
        try:
            # forwarding data between server and client
            proxy.receive_from(proxy.client)
            proxy.send_to(proxy.server)
            proxy.receive_from(proxy.server)
            proxy.send_to(proxy.client)

        except:
            print("Connection closed")

            # close connection from both sides
            proxy.client.conn_socket.close()
            proxy.server.conn_socket.close()

            # connect client and then server
            proxy.listen_to_connection()
            proxy.connect_to_server(server_ip, fake_ip)
