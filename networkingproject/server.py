from socket import AF_INET, socket, SOCK_STREAM
import sys, signal
import pickle
import http.server
import socketserver
from threading import Thread
from classes.Message import Message, MessageType

indirizzi = {}
hostIP = 'localhost'
hostPort = 13000
BUFFERSIZE = 1024
SERVER = None
serverMacAddress = "52:AB:0A:DF:10:DC"
serverIPAddress = "195.1.10.10"

def acceptIncomingClient():
    while True:
        print("Attendo prossima connessione ...")
        client, clientAddress = SERVER.accept()
        print("Benvenuto %s:%s !" % clientAddress)
        message = Message()
        message.sourceMac = serverMacAddress
        message.destinationMac = serverIPAddress
        message.messageType = messageType.WELCOME

        client.send(pickle.dumps(message))
        indirizzi[client] = clientAddress
        Thread(target=clientManagement, args=(client,)).start()

def serverAction(messageType):
    switcher = {
        messageType.DHCPDISCOVER: print("a"),
        messageType.DHCPOFFER: print("a"),
        messageType.DHCPREQUEST: print("a"),
        messageType.DHCPACK: print("a"),
        messageType.ROUTERLISTREQUEST: print("a"),
        messageType.ROUTERLISTRESPONSE: print("a"),
        messageType.WELCOME: print("a"),
    }

    switcher.get(messageType, "nothing")

def clientManagement(client):
    while True:
        message = pickle.loads(client.recv(BUFSIZ))
        serverAction(message.messageType)

def main():
    global SERVER
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind((hostIP, hostPort))
    SERVER.listen(5)
    ACCEPT_THREAD = Thread(target=acceptIncomingClient)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

if __name__ == "__main__":
    main()
