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
                 alpha: float = None,
                 dns_server_port: int = None):
        
        self.logging = Logger(log_path)
        self.alpha = alpha
        self.dns_server_port = dns_server_port
        self.listen_port = listen_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.fake_ip = fake_ip
        return
    
    def send_dns_request(self, dns_server_ip: str, dns_server_port: int):
        dns_conn = Connection("UDP")
        dns_conn.set_address(dns_server_ip, dns_server_port)
        dns_conn.send(self.make_dns_request_message())
        response, dns_server_address = dns_conn.receive()
        print(f"Message received from DNS server {dns_server_address}: {response}")
        return response
    
    def make_dns_request_message(self):
        domain_name = b'\x05video\x08columbia\x03edu'
        message = (
            b'\x23\x33' +           # transaction ID
            b'\x80\x00' +           # flags: QR = 1, Opcode, AA, TC, RD, RA, Z, RCODE
            b'\x00\x01' +           # QDCOUNT = 1
            b'\x00\x00' +           # ANCOUNT = 0
            b'\x00\x00' +           # NSCOUNT = 0
            b'\x00\x00' +           # ARCOUNT = 0
            domain_name + b'\x00' + # domain_name
            b'\x00\x01' +           # QTYPE = 1
            b'\x00\x01'             # QCLASS = 1
        )
        return message
    
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

            self.client_conn = Connection("TCP")
            self.client_conn.listen_to_connection(self.listen_port)
            message = self.client_conn.receive()
            print("========")
            response = self.send_dns_request('127.0.0.1', self.dns_server_port)
            # self.server_conn = Connection("TCP")
            # self.server_conn.connect_to_server(self.server_ip, self.server_port, self.fake_ip)
            # self.server_conn.send(message)
    

if __name__ == '__main__':
    # read input
    topo_dir, log_path, alpha, listen_port, fake_ip, dns_server_port = sys.argv[1:]
    server_ip = '127.0.0.1'
    # proxy init
    proxy = Proxy(int(listen_port), server_ip, 8080, fake_ip, log_path, eval(alpha), int(dns_server_port))
    proxy.serve()
    


