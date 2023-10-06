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

    def listen_to_connection(self):
        self.socket_to_client.listen(1)
        print("The proxy is ready to receive")
        self.current_client_info = self.socket_to_client.accept()
        print("Connection established with ", self.current_client_info)
        return
    
    def receive_message(self, client):
        message = client.socket.recv(1024).decode()
        print("Proxy received from %s: %s" % (client.address, message))
        return

class Client(object):
    def __init__(self, client_info):
        self.socket, self.address = client_info
        return

class Server(object):
    def __init__(self, server_info):
        self.socket, self.address = server_info
        return

if __name__ == '__main__':
    listen_port, fake_ip, server_ip = sys.argv[1:]
    server = Server((server_ip, 8080))
    proxy = Proxy(listen_port, fake_ip)
    proxy.listen_to_connection()
    client = Client(proxy.current_client_info)
    while True:
        proxy.receive_message(client)
        
        # connectionSocket.send(message.encode())
        # connectionSocket.close()
        # print("Connection closed")