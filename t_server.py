from socket import *

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

while True:
    connectionSocket, clientAddress = serverSocket.accept()
    print("Connection established with ", clientAddress)
    for i in range(10):
        message = connectionSocket.recv(1024).decode()
        print("Server received from %s: %s" % (clientAddress, message))
        modifiedMessage = message.upper()
        connectionSocket.send(modifiedMessage.encode())
    connectionSocket.close()
    print("Connection closed")