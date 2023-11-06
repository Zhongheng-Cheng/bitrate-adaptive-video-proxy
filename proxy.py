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
        print(f"Message received from DNS server {dns_server_address}")
        response = self.parse_dns_response(response)
        print(f"Message content: {response}")
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
    
    def parse_dns_response(self, response):
        server_ip = ''
        if len(response) == 52:
            server_ip = '.'.join([str(i) for i in list(response[-4:])])
        return server_ip
    
    def get_content_length(self, http_response):
        '''
        Parse the received data and return the "Content-Length" parameter.
        '''
        content_length_match = re.search(r'Content-Length: (\d+)', http_response)
        if content_length_match:
            content_length = int(content_length_match.group(1))
            return content_length
        else:
            print("Content-Length header not found in the response.")
            return

    def throughput_cal(self, ts, tf, B, alpha):
        tput = B / (tf - ts)
        self.throughput = alpha * tput + (1 - alpha) * self.throughput # TODO: initialize self.throughput
        return tput

    def bitrate_select(self):
        bitrate = None # TODO: select appropriate bitrate
        return bitrate
    
    def replace_bitrate(self, message: str, bitrate: int):
        new_message = re.sub(r'(bunny_)\d+(bps)', r"\g<1>" + str(bitrate) + r"\g<2>", message)
        return new_message
    
    def serve(self):
        self.client_conn = Connection("TCP")
        self.client_conn.listen_to_connection(self.listen_port)
        self.server_ip = self.send_dns_request('127.0.0.1', self.dns_server_port)
        self.server_conn = Connection("TCP")
        self.server_conn.connect_to_server(self.server_ip, self.server_port, self.fake_ip)
        while True:
            try:
                # TODO: throughput_cal()

                # forwarding data between server and client
                print("Starting forwarding data")
                message = self.client_conn.receive()
                if not message:
                    raise
                print("========")
                # TODO: modifying bitrate information
                self.server_conn.send(message)
                response = self.server_conn.receive()
                print(f"Response received from server {self.server_ip}: {response}")
                self.client_conn.send(response)

            except:
                print("Connection closed")

                # close connection from both sides
                self.client_conn.close()
                self.server_conn.close()

                # connect client and then server
                self.client_conn = Connection("TCP")
                self.client_conn.listen_to_connection(self.listen_port)
                self.server_ip = self.send_dns_request('127.0.0.1', self.dns_server_port)
                self.server_conn = Connection("TCP")
                self.server_conn.connect_to_server(self.server_ip, self.server_port, self.fake_ip)

if __name__ == '__main__':
    # read input
    topo_dir, log_path, alpha, listen_port, fake_ip, dns_server_port = sys.argv[1:]
    # proxy init
    proxy = Proxy(listen_port=int(listen_port), 
                  server_port=8080, 
                  fake_ip=fake_ip, 
                  log_path=log_path, 
                  alpha=eval(alpha), 
                  dns_server_port=int(dns_server_port))
    proxy.serve()