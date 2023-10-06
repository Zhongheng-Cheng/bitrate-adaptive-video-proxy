class Proxy(object):
    def __init__(self, listen_port):
        import socket as s

        # binding listening socket
        self.listen_address = ('', int(listen_port))
        self.socket_listening = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket_listening.bind(self.listen_address)
        return

    def connect_to_server(self, server):
        server.socket.connect(server.address)
        print("Successfully connected to server")
        return

    def listen_to_connection(self):
        self.socket_listening.listen(10)
        print("The proxy is ready to receive")
        current_client_info = self.socket_listening.accept()
        print("Connection established with ", current_client_info)
        return current_client_info
    
    def receive_from(self, entity):
        self.message = entity.socket.recv(1024).decode()
        print("Proxy received from %s: %s" % (entity.address, self.message))
        return
    
    def send_to(self, entity):
        entity.socket.send(self.message.encode())
        return
    

class InternetEntity(object):
    def __init__(self, address, socket=None):
        '''
        Input:
            address
            socket
        '''
        self.address = address
        self.socket = socket
        return
    
    def bind_socket(self, address):
        import socket as s
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket.bind(address)
        return

if __name__ == '__main__':
    # read input
    import sys
    listen_port, fake_ip, server_ip = sys.argv[1:]

    # server and proxy init
    proxy = Proxy(listen_port)
    server = InternetEntity((server_ip, 8080))
    server.bind_socket((fake_ip, 0))

    # client connect and init
    client_socket, client_address = proxy.listen_to_connection()
    client = InternetEntity(client_address, client_socket)

    # server connect
    proxy.connect_to_server(server)

    while True:
        proxy.receive_from(client)
        proxy.send_to(server)
        proxy.receive_from(server)
        proxy.send_to(client)
        
        # connectionSocket.close()
        # print("Connection closed")