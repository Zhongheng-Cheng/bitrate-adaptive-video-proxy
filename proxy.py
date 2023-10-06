import sys

class Proxy(object):
    def __init__(self, listen_port, fake_ip):
        import socket as s

        # binding client-end socket
        self.listen_address = ('', int(listen_port))
        self.socket_to_client = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket_to_client.bind(self.listen_address)

        # binding server-end socket
        self.fake_address = (fake_ip, 0)
        self.socket_to_server = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket_to_server.bind(self.fake_address)
        return

    def connect_to_server(self, server):
        self.socket_to_server.connect(server.address)
        print("Successfully connected to server")
        return

    def listen_to_connection(self):
        self.socket_to_client.listen(1)
        print("The proxy is ready to receive")
        self.current_client_info = self.socket_to_client.accept()
        print("Connection established with ", self.current_client_info)
        return
    
    def receive_from_client(self, client):
        self.message = client.socket.recv(1024).decode()
        print("Proxy received from %s: %s" % (client.address, self.message))
        return
    
    def send_to_server(self):
        proxy.socket_to_server.send(self.message.encode())
        return
    
    def receive_from_server(self):
        self.message = self.socket_to_server.recv(1024).decode()
        print("From server: ", self.message)

    def send_to_client(self, client):
        client.socket.send(self.message.encode())

class Client(object):
    def __init__(self, client_info):
        self.socket, self.address = client_info
        return

class Server(object):
    def __init__(self, server_info):
        self.address = server_info
        return

if __name__ == '__main__':
    listen_port, fake_ip, server_ip = sys.argv[1:]
    server = Server((server_ip, 8080))
    proxy = Proxy(listen_port, fake_ip)

    # establish server-end connection
    proxy.connect_to_server(server)
    proxy.message = "testtest" ###

    # listen for client-end connection
    proxy.listen_to_connection()
    client = Client(proxy.current_client_info)
    while True:
        proxy.receive_from_client(client)
        proxy.send_to_server()
        proxy.receive_from_server()
        proxy.send_to_client(client)
        
        # connectionSocket.close()
        # print("Connection closed")