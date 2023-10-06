import sys

class Proxy(object):
    def __init__(self, listen_port, fake_ip, server_ip):
        import socket as s

        self.address = ('', int(listen_port))
        self.fake_ip = fake_ip
        self.server_ip = server_ip

        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket.bind(self.address)
        return

    def listen_to_connection(self):
        self.socket.listen(1)
        print("The proxy is ready to receive")
        self.current_client_info = self.socket.accept()
        print("Connection established with ", self.current_client_info)
        return
    
    def receive_message(self, client):
        message = client.socket.recv(1024).decode()
        print("Proxy received from %s: %s" % (client.address, message))
        return

class Client(object):
    def __init__(self, client_info):
        self.socket = client_info[0]
        self.address = client_info[1]
        return
    
if __name__ == '__main__':
    listen_port, fake_ip, server_ip = sys.argv[1:]
    proxy = Proxy(listen_port, fake_ip, server_ip)
    proxy.listen_to_connection()
    client = Client(proxy.current_client_info)
    while True:
        proxy.receive_message(client)
        
        # connectionSocket.send(message.encode())
        # connectionSocket.close()
        # print("Connection closed")