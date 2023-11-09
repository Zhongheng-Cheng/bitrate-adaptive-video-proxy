#!/usr/bin/env python3
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
                 log_path: str = None,
                 alpha: float = None,
                 dns_server_port: int = None):

        with open(f"{topo_dir}/{topo_dir[-5:]}.dns", 'r') as fo:
            self.dns_server_ip = fo.read().strip()
        self.logger = Logger(log_path)
        self.alpha = alpha
        self.dns_server_port = dns_server_port
        self.listen_port = listen_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.fake_ip = fake_ip
        self.avg_tput = 1000
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
        self.avg_tput = alpha * current_tput + (1 - alpha) * self.avg_tput
        return current_tput

    def bitrate_select(self):
        bitrate_options = [int(i) for i in self.bitrate_list if int(i) * 1.5 < self.avg_tput]
        if bitrate_options:
            best_bitrate = max(bitrate_options)
            return str(best_bitrate)
        else:
            return self.bitrate_list[0]
    
    def replace_bitrate(self, message: str, bitrate: str):
        new_message = re.sub(r'(bunny_)\d+(bps)', r"\g<1>" + bitrate + r"\g<2>", message)
        return new_message
    
    def replace_nolist(self, message: str):
        new_message = re.sub('BigBuckBunny_6s.mpd', 'BigBuckBunny_6s_nolist.mpd', message)
        return new_message
    
    def parse_bitrate_list(self, list_iter):
        self.bitrate_list = []
        for i in list_iter:
            self.bitrate_list.append(i.group(1))
        return

    def process_header(self, header):
        header = header.decode()
        if "BigBuckBunny_6s.mpd" in header:
            self.server_conn.send(header.encode() + b'\r\n\r\n')
            header_with_list, payload_with_list = self.server_conn.receive().split(b'\r\n\r\n')
            print("++++++++++++++++++++")
            list_iter = re.finditer(r'bandwidth="(\d+)"', payload_with_list.decode())
            self.parse_bitrate_list(list_iter)
            print(f"Parsed bitrate list: {self.bitrate_list}")
            print("++++++++++++++++++++")
            self.avg_tput = int(self.bitrate_list[0]) * 1.5
            header = self.replace_nolist(header)
        elif "bps" in header:
            header = self.replace_bitrate(header, self.bitrate_select())
        return header
    
    def serve(self):
        self.client_conn = Connection("TCP")
        self.client_conn.listen_to_connection(self.listen_port)
        
        while True:
            try:
                # receiving message from client and modify header
                print("#####: Receiving from client...")
                request_header, request_payload = self.client_conn.receive().split(b'\r\n\r\n')
                print("#####: Modifying header...")
                modified_header = self.process_header(request_header)

            except Exception as e:
                print("Connection with client closed")
                self.client_conn.close()
                # self.server_conn.close()
                self.client_conn = Connection("TCP")
                self.client_conn.listen_to_connection(self.listen_port)
                # self.server_ip = self.send_dns_request(self.dns_server_ip, self.dns_server_port)
                # self.server_conn = Connection("TCP")
                # self.server_conn.connect_to_server(self.server_ip, self.server_port, self.fake_ip)
                continue

            # try:
            # sending and receiving message with server
            self.server_ip = self.send_dns_request(self.dns_server_ip, self.dns_server_port)
            self.server_conn = Connection("TCP")
            self.server_conn.connect_to_server(self.server_ip, self.server_port, self.fake_ip)
            ts = time.time()
            print("#####: Sending to server...")
            self.server_conn.send(modified_header.encode() + b'\r\n\r\n' + request_payload)
            print("#####: Receiving from server...")
            response_header, response_payload, content_length = self.server_conn.receive_http_response()
            tf = time.time()

            # except Exception as e:
            #     print("Connection with server closed")
            #     self.server_conn.close()

            #     # connect to server
            #     self.server_ip = self.send_dns_request(self.dns_server_ip, self.dns_server_port)
            #     self.server_conn = Connection("TCP")
            #     self.server_conn.connect_to_server(self.server_ip, self.server_port, self.fake_ip)

            #     # resend request
            #     ts = time.time()
            #     print("#####: Sending to server...")
            #     self.server_conn.send(modified_header.encode() + b'\r\n\r\n' + request_payload)
            #     print("#####: Receiving from server...")
            #     response_header, response_payload, content_length = self.server_conn.receive_http_response()
            #     tf = time.time()
            
            print("#####: Sending to client...")
            self.client_conn.send(response_header.encode() + b'\r\n\r\n' + response_payload)

            # calculating and logging
            current_tput = self.throughput_cal(ts, tf, int(content_length), self.alpha)
            chunkname = re.search(r'GET (\S+) ', modified_header).group(1)
            bitrate_match = re.search(r'bunny_(\d+)bps', modified_header)
            if bitrate_match:
                self.logger.log(f"{tf - ts} {current_tput / 1000} {self.avg_tput / 1000} {round(int(bitrate_match.group(1)) / 1000)} {self.server_ip} {chunkname}")


class Logger(object):
    def __init__(self, filepath):
        '''
        Proxy logging: <time> <duration> <tput> <avg-tput> <bitrate> <server-ip> <chunkname>
        DNS Server logging: 
            After each response from a client: <time> "request-report" <decision-method> <returned-web-server-ip>
            After each measurement to the web server: <time> "measurement-report" <video-server-ip> <latency>
        '''
        self.filepath = filepath
        with open(self.filepath, 'w') as fo:
            fo.seek(0)
            fo.truncate()
        return

    def log(self, content):
        with open(self.filepath, 'a') as fo:
            fo.write(f"{time.time()} {content}\n")
        return


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
    
    def receive_http_header(self):
            response_header = b""
            while True:
                chunk = self.receive()
                response_header += chunk
                if b'\r\n\r\n' in response_header:
                    break
            header, payload = response_header.split(b'\r\n\r\n')
            return header.decode(), payload
    
    def get_content_length(self, http_header):
        content_length_match = re.search(r'Content-Length: (\d+)', http_header)
        if content_length_match:
            return int(content_length_match.group(1))
        else:
            return None

    def receive_http_response(self):
        response_header, response_payload = self.receive_http_header()
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
            if message == b'':
                raise TypeError("Empty input")
            return message
        
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
                self.conn_socket.settimeout(7)
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