#!/usr/bin/env python3.10
import socket
import sys

class DNSServer(object):
    def __init__(self):
        self.DNS_RECORDS = {
            'example.com': '192.168.1.100',
            'google.com': '8.8.8.8',
            'video.columbia.edu': '....',
        }
        topo_dir, log_path, listen_port, decision_method = self.get_inputs()
        self.server_socket = self.listen_to_udp(listen_port)
        return
    
    def get_inputs(self):
        topo_dir, log_path, listen_port, decision_method = sys.argv[1:]
        return topo_dir, log_path, listen_port, decision_method
    
    def listen_to_connection(self, listen_port: int):
        '''
        Listen to UDP connections.
        '''
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', listen_port))
        print(f"DNS server listening on 0.0.0.0:{listen_port}")
        return server_socket

    def handle_dns_request(self, data, client_address):
        try:
            # # Parse the DNS request
            # domain_name = data[12:].split(b'\x00', 1)[0]

            # if domain_name in self.DNS_RECORDS:
            #     # If the domain name is in our records, send a DNS response with the IP address
            #     response = (
            #         data[:2] + b'\x81\x80' + data[4:6] + b'\x00\x00\x00\x00' +
            #         data[12:] + b'\x00\x01\x00\x01' +
            #         b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04' +
            #         socket.inet_aton(self.DNS_RECORDS[domain_name])
            #     )
            #     self.server_socket.sendto(response, client_address)
            return

        except Exception as e:
            print(f"Error handling DNS request: {e}")

    def serve(self):
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            data = data.decode()
            print(f"Received DNS request from {client_address}: {data}")
            self.handle_dns_request(data, client_address)