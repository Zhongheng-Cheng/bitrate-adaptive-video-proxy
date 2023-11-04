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
from connection import Connection

class Proxy(object):
    def __init__(self, 
                 listen_port: int = None, 
                 server_ip: str = None, 
                 server_port: int = None,
                 fake_ip: str = None,
                 log_path: str = None,
                 alpha: int = None):
        
        self.logging = Logger(log_path)
        self.alpha = alpha
        self.client_conn = Connection()
        self.client_conn.listen_to_connection(listen_port)
        self.server_conn = Connection()
        self.server_conn.connect_to_server(server_ip, server_port, fake_ip)
        return
    
    def dns_request(self, dns_server_ip, dns_server_port):
        pass
    
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
    

if __name__ == '__main__':
    # read input
    topo_dir, log_path, alpha, listen_port, fake_ip, dns_server_port = sys.argv[1:]
    server_ip = '127.0.0.1'
    # proxy init
    proxy = Proxy(int(listen_port), server_ip, 8080, fake_ip, log_path, int(alpha))
    proxy.serve()
    


