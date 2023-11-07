#!/usr/bin/env python3.10
import socket
import sys
import subprocess
import re
import time

class IpBook(object):
    def __init__(self, topo_dir):
        '''
        Handles web server ip management and selection.
        '''
        self.ip_list = self.get_ip_list(topo_dir)
        self.ip_list_len = len(self.ip_list)
        self.latencies = {}
        self.last_given_ip_index = 0
        return
    
    def get_ip_list(self, topo_dir) -> list:
        '''
        Get IP list from topox.servers.
        '''
        with open(f"{topo_dir}/{topo_dir[-5:]}.servers", 'r') as fo:
            content = fo.readlines()
        ip_list = [i.strip() for i in content]
        return ip_list
    
    def get_an_ip(self, decision_method) -> str:
        '''
        Select the "best" IP based on the decision method.
        '''
        if decision_method == "round-robin":
            self.last_given_ip_index = (self.last_given_ip_index + 1) % self.ip_list_len
            ip_response = self.ip_list[self.last_given_ip_index]
        elif decision_method == "lowest-latency":
            ip_response = min(self.latencies, key=lambda x: self.latencies[x])
        return ip_response


class DnsServer(object):
    def __init__(self):
        self.dns_records = [b'\x05video\x08columbia\x03edu']
        topo_dir, log_path, listen_port, decision_method = self.get_inputs()
        with open(f"{topo_dir}/{topo_dir[-5:]}.dns", 'r') as fo:
            self.listening_ip = fo.read().strip()
        self.server_socket = self.listen_to_connection(int(listen_port))
        self.ip_book = IpBook(topo_dir)
        self.logger = Logger(log_path)
        self.decision_method = decision_method
        return
    
    def get_inputs(self):
        '''
        Get command line inputs.
        '''
        topo_dir, log_path, listen_port, decision_method = sys.argv[1:]
        return topo_dir, log_path, listen_port, decision_method
    
    def listen_to_connection(self, listen_port: int):
        '''
        Listen to UDP connections.
        '''
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.settimeout(3)
        server_socket.bind((self.listening_ip, listen_port))
        print(f"DNS server listening on {self.listening_ip}:{listen_port}")
        return server_socket
    
    def measure_latency(self):
        for ip in self.ip_book.ip_list:
            ping_output = subprocess.check_output(f'ping -c 1 {ip}', shell=True, universal_newlines=True)
            latency = eval(re.search(r'time=(\S+) ms', ping_output).group(1))
            self.logger.log(f'measurement-report {ip} {latency}')
            self.ip_book.latencies[ip] = latency
        return

    def handle_dns_request(self, data, client_address):
        '''
        Parse the DNS request and give response.
        '''
        domain_name = data[12:].split(b'\x00', 1)[0]
        if domain_name in self.dns_records:
            server_ip = self.ip_book.get_an_ip(self.decision_method)
            response = (
                data[:2] +                          # transaction ID
                b'\x84\x00' +                       # flags: QR = 1, Opcode, AA = 1, TC, RD, RA, Z, RCODE  
                b'\x00\x01' +                       # QDCOUNT = 1
                b'\x00\x01' +                       # ANCOUNT = 1
                b'\x00\x00' +                       # NSCOUNT = 0
                b'\x00\x00' +                       # ARCOUNT = 0
                domain_name + b'\x00' +             # domain_name
                b'\x00\x01' +                       # QTYPE = 1
                b'\x00\x01' +                       # QCLASS = 1
                b'\xc0\x0c' +                       # NAME
                b'\x00\x01' +                       # TYPE = 1
                b'\x00\x01' +                       # CLASS = 1
                b'\x00\x00\x00\x00' +               # TTL = 0
                b'\x00\x04' +                       # RDLENGTH = 4
                self.ip_to_hex(server_ip)
            )
            self.logger.log(f'request-report {self.decision_method} {server_ip}')
        else:
            response = (
                data[:2] +                          # transaction ID
                b'\x84\x03' +                       # flags: QR = 1, Opcode, AA = 1, TC, RD, RA, Z, RCODE = 3 
                b'\x00\x01' +                       # QDCOUNT = 1
                b'\x00\x00' +                       # ANCOUNT = 0
                b'\x00\x00' +                       # NSCOUNT = 0
                b'\x00\x00' +                       # ARCOUNT = 0
                domain_name + b'\x00' +             # domain_name
                b'\x00\x01' +                       # QTYPE = 1
                b'\x00\x01'                         # QCLASS = 1
            )
        self.server_socket.sendto(response, client_address)
        return
    
    def ip_to_hex(self, ip: str):
        result = b''
        for i in ip.split('.'):
            result += bytes([int(i)])
        return result

    def serve(self):
        while True:
            try:
                self.measure_latency()
                data, client_address = self.server_socket.recvfrom(1024)
                print(f"Received DNS request from {client_address}")
                self.handle_dns_request(data, client_address)
            except socket.timeout:
                pass
            except Exception as e:
                print(e)


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


if __name__ == '__main__':
    dns_server = DnsServer()
    dns_server.serve()