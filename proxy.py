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
        
        self.logger = Logger(log_path)
        self.alpha = alpha
        self.dns_server_port = dns_server_port
        self.listen_port = listen_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.fake_ip = fake_ip
        self.avg_tput = 10000 # TODO: modify
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

    def throughput_cal(self, ts, tf, B, alpha):
        current_tput = B / (tf - ts)
        self.avg_tput = alpha * current_tput + (1 - alpha) * self.avg_tput # TODO: initialize self.throughput
        return current_tput

    def bitrate_select(self):
        bitrate = None # TODO: select appropriate bitrate
        return bitrate
    
    def replace_bitrate(self, message: str, bitrate: int):
        new_message = re.sub(r'(bunny_)\d+(bps)', r"\g<1>" + str(bitrate) + r"\g<2>", message)
        return new_message
    
    def replace_nolist(self, message: str):
        new_message = re.sub('BigBuckBunny_6s.mpd', 'BigBuckBunny_6s_nolist.mpd', message)
        return new_message

    def process_header(self, header):
        if "BigBuckBunny_6s.mpd" in header:
            self.server_conn.send(header.encode() + b'\r\n\r\n')
            header_with_list, payload_with_list = self.server_conn.receive()
            print("++++++++++++++++++++")
            print(re.finditer(r'bandwidth="(\d+)"', payload_with_list.decode()))
            print("++++++++++++++++++++")
            # TODO: parse message_with_list to get bitrate list
            header = self.replace_nolist(header)
        # else:
        #     message = replace_bitrate(message, self.bitrate_select())
        return header
    
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
                # self.logger.log("Starting forwarding data") ###
                request_header, request_payload = self.client_conn.receive()
                # self.logger.log("Message received from client: %s" % request_header.split('\n')[0]) ###
                modified_header = self.process_header(request_header)
                ts = time.time()
                # self.logger.log("Header modified: %s" % modified_header.split('\n')[0]) ###
                self.server_conn.send(modified_header.encode() + b'\r\n\r\n' + request_payload)
                response_header, response_payload, content_length = self.server_conn.receive_http_response()
                # self.logger.log(f"Response received from server, content_length: {content_length}, payload_length: {len(response_payload)}") ###
                self.client_conn.send(response_header.encode() + b'\r\n\r\n' + response_payload)
                tf = time.time()
                current_tput = self.throughput_cal(ts, tf, int(content_length), self.alpha)
                chunkname = re.search(r'GET (\S+) ', modified_header).group(1)
                bitrate_match = re.search(r'bunny_(\d+)bps', modified_header)
                if bitrate_match:
                    self.logger.log(f"{tf - ts} {current_tput / 1000} {self.avg_tput / 1000} {bitrate_match.group(1)} {self.server_ip} {chunkname}")

            except TimeoutError:
                pass
            # except TypeError:
            #     self.client_conn.send(b'')
            except Exception as e:
                print(e)
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