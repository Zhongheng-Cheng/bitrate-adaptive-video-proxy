#!/usr/bin/env python3.10
import socket
import sys

class DnsServer(object):
    def __init__(self):
        self.dns_records = {
            b'\x05video\x08columbia\x03edu': '1.1.1.1', # point to the "best" server's ip
        }
        topo_dir, log_path, listen_port, decision_method = self.get_inputs()
        self.server_socket = self.listen_to_connection(int(listen_port))
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
            # Parse the DNS request
            domain_name = data[12:].split(b'\x00', 1)[0]
            if domain_name in self.dns_records:
                # If the domain name is in our records, send a DNS response with the IP address
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
                    self.ip_to_hex(self.dns_records[domain_name])
                )
                self.server_socket.sendto(response, client_address)
            return

        except Exception as e:
            print(f"Error handling DNS request: {e}")
            return
    
    def ip_to_hex(self, ip: str):
        result = b''
        for i in ip.split('.'):
            result += bytes([int(i)])
        return result

    def serve(self):
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            print(f"Received DNS request from {client_address}: {data}")
            self.handle_dns_request(data, client_address)


# def resolve_dns(dns_request):
#     header = dns_request[0:7]
#     body = dns_request[7:]
#     return header, body

# def make_dns_request():
#     pass

if __name__ == '__main__':
    dns_server = DnsServer()
    dns_server.serve()