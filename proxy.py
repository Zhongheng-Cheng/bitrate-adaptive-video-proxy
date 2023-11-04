#!/usr/bin/env python3.10
import socket
import sys
import time
import re
import select
import threading
import subprocess
import numpy
from logger import Logger

class Proxy(object):
    def __init__(self, 
                 listen_port: int = None, 
                 server_ip: str = None, 
                 server_port: int = None,
                 fake_ip: str = None,
                 logging = None,
                 alpha: int = None):
        
        self.logging = logging
        self.alpha = alpha
        self.client_conn = Connection()
        self.client_conn.listen_to_connection(listen_port)
        self.server_conn = Connection()
        self.server_conn.connect_to_server(server_ip, server_port, fake_ip)
        return
    
    def serve(self):

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

            message = self.client_conn.receive()
            print("========")
            self.server_conn.send(message)
    

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


class DnsRequest(object):
    def __init__(self, dns_server_ip, dns_server_port, cname):
        self.dns_server_ip = dns_server_ip
        self.dns_server_port = dns_server_port
        self.cname = cname
        return
    

if __name__ == '__main__':
    # read input
    topo_dir, log_path, alpha, listen_port, fake_ip, dns_server_port = sys.argv[1:]
    # server_ip = dns_request("video.columbia.edu")
    server_ip = '127.0.0.1'
    log = Logger(log_path)
    # proxy init
    proxy = Proxy(int(listen_port), server_ip, 8080, fake_ip, log, int(alpha))
    proxy.serve()
    


