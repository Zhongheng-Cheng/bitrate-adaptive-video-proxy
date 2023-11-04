#!/usr/bin/env python3.10
import socket
import sys
import time
import re
import select
import threading
import subprocess
import numpy

class Proxy(object):
    def __init__(self, 
                 listen_port: int = None, 
                 server_ip: str = None, 
                 server_port: int = None,
                 fake_ip: str = None,
                 logging = None):
        self.listen_port = listen_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.fake_ip = fake_ip
        self.logging = logging
        return

    def connect_to_server(self, server_ip: str, server_port: int, fake_ip: str):
        '''
        Continuously try to connect server at 1 second interval.
        '''
        assert server_ip and server_port, "server_ip and server_port should not be None."
        print("Connecting to server...")
        while True:
            try:
                self.server = Connection((server_ip, server_port))
                if fake_ip:
                    self.server.bind_socket((fake_ip, 0))
                self.server.conn_socket.connect(self.server.address)
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
        listen_address = ('0.0.0.0', listen_port)
        socket_listening = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_listening.bind(listen_address)
        
        # listen for client connection
        socket_listening.listen(10)
        print("The proxy is ready to receive...")
        client_socket, client_address = socket_listening.accept()

        # client connect and init
        self.client = Connection(client_address, client_socket)
        print(f"Connection established with {client_address}.")
        return 
    
    def receive_from(self, conn):
        '''
        Receive a message from an conn's socket.
        Input: 
            conn: <class 'Connection'>
        '''
        self.message = conn.conn_socket.recv(4096).decode()
        print(f"Proxy received from {conn.address}: {self.message}")
        return self.message
    
    def send_to(self, conn):
        '''
        Send a message to an conn's socket.
        
        Input: 
            conn: <class 'Connection'>
        '''
        conn.conn_socket.send(self.message.encode())
        return
    

class Connection(object):
    def __init__(self, address: tuple, conn_socket=None):
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
    # topo_dir, log, alpha, listen_port, fake_ip, dns_server_port = sys.argv[1:]
    listen_port, fake_ip, server_ip = sys.argv[1:]

    # proxy init
    # proxy = Proxy(topo_dir, log, alpha, listen_port, fake_ip, dns_server_port)
    proxy = Proxy(listen_port)
    
    # connect client and then server
    proxy.listen_to_connection()
    proxy.connect_to_server(server_ip, fake_ip)

    while True:
        # try:
        #     # forwarding data between server and client
        #     proxy.receive_from(proxy.client)
        #     proxy.send_to(proxy.server)
        #     proxy.receive_from(proxy.server)
        #     proxy.send_to(proxy.client)

        # except:
        #     print("Connection closed")

        #     # close connection from both sides
        #     proxy.client.conn_socket.close()
        #     proxy.server.conn_socket.close()

        #     # connect client and then server
        #     proxy.listen_to_connection()
        #     proxy.connect_to_server(server_ip, fake_ip)

        proxy.receive_from(proxy.client)
        print("========")
        proxy.send_to(proxy.server)

