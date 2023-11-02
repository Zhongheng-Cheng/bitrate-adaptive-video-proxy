from socket import *

serverName = "127.0.0.1"
serverPort = 8012
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
print("Successfully connected")
while True:
    message = input("Sending message: ")
    clientSocket.send(message.encode())
    modifiedMessage = clientSocket.recv(1024)
    print("From server: ", modifiedMessage.decode())