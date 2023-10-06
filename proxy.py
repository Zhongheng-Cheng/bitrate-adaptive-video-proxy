import sys
from socket import *

listen_port, fake_ip, server_ip = sys.argv[1:]

proxyPort = int(listen_port)
proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.bind(('', proxyPort))
print("The proxy is ready to receive")
proxySocket.listen(1)
connectionSocket, clientAddress = proxySocket.accept()
print("Connection established with ", clientAddress)

while True:
    message = connectionSocket.recv(1024).decode()
    print("Proxy received from %s: %s" % (clientAddress, message))
    # connectionSocket.send(message.encode())
    # connectionSocket.close()
    # print("Connection closed")