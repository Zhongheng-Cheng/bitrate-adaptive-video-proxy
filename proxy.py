import socket as s
import sys

class Proxy(object):
    def __init__(self, listen_port):
        # binding listening socket
        self.listen_address = ('', int(listen_port))
        self.socket_listening = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket_listening.bind(self.listen_address)
        return

    def connect_to_server(self, server_ip, fake_ip):
        '''
        Input:
            server_ip: str
            fake_ip: str
        '''
        print("Connecting to server...")
        self.server = InternetEntity((server_ip, 8080))
        self.server.bind_socket((fake_ip, 0))
        self.server.socket.connect(self.server.address)
        print("Successfully connected to server.")
        return

    def listen_to_connection(self):
        '''
        Await a client to connect. Queueing up to 10 clients.
        '''
        self.socket_listening.listen(10)
        print("The proxy is ready to receive...")
        client_socket, client_address = self.socket_listening.accept()

        # client connect and init
        self.client = InternetEntity(client_address, client_socket)
        print("Connection established with ", client_address)
        return 
    
    def receive_from(self, entity):
        '''
        Receive a message from an entity socket.

        Input: 
            entity: <class 'InternetEntity'>
        '''
        is_end = False
        self.send_buffer = ''
        while not is_end:
            message = entity.socket.recv(1024).decode().split('\n')
            self.send_buffer += message[0]
            if len(message) > 1:
                is_end = True
                self.send_buffer += '\n'
        print("Proxy received from %s: %s" % (entity.address, self.send_buffer))
        return
    
    def send_to(self, entity):
        '''
        Send a message to an entity socket.
        
        Input: 
            entity: <class 'InternetEntity'>
        '''
        entity.socket.send(self.send_buffer.encode())
        return
    

class InternetEntity(object):
    def __init__(self, address, socket=None):
        '''
        Input:
            address: tuple, (ip, port)
            socket: <class 'Socket'>, will create one if not entered
        '''
        self.address = address
        if not socket:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        else:
            self.socket = socket

        return
    
    def bind_socket(self, bind_address):
        '''
        Input:
            bind_address: tuple, (ip, port)
        '''
        self.socket.bind(bind_address)
        return

if __name__ == '__main__':
    # read input
    listen_port, fake_ip, server_ip = sys.argv[1:]

    # server and proxy init
    proxy = Proxy(listen_port)
    
    # client connect
    proxy.listen_to_connection()

    # server connect
    proxy.connect_to_server(server_ip, fake_ip)

    while True:        
        try:
            proxy.receive_from(proxy.client)
            proxy.send_to(proxy.server)
        except:
            print("Server connection closed")
            proxy.server.socket.close()
            proxy.client.socket.close()
        
        try:
            proxy.receive_from(proxy.server)
            proxy.send_to(proxy.client)
        except:
            print("Client connection closed")
            proxy.client.socket.close()
            proxy.listen_to_connection()
