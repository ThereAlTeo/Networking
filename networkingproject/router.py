from socket import AF_INET, socket, SOCK_STREAM
import sys, signal
import pickle
import http.server
import socketserver
from threading import Thread
from classes.Message import Message, MessageType
from utilities import Utilities as util

macServerSide = ''
ipServerSide = ''
macClientSide = ''
ipClientSide = ''
serverConnection = None

routerServerSide = socket(AF_INET, SOCK_STREAM)
routerClientSide = socket(AF_INET, SOCK_STREAM)

def welcomeType(message):
    print("Il SERVER ha dato il Benvenuto!")
    message.prepareForNextMessage()
    message.sourceIP = "255.255.255.255"
    message.sourceMac = macServerSide
    message.messageType = MessageType.DHCPROUTERREQUEST
    message.message = "MyClientSocketName:" + routerClientSide.getsockname() + "\n"
    return message

def managementServerMessage(message):
    switcher = {
        messageType.WELCOME: welcomeType,
        #messageType.DHCPREQUEST: welcomeType(message),
        #messageType.ROUTERLISTREQUEST: welcomeType(message),
        #messageType.WELCOME: welcomeType(message),
    }
    return switcher.get(message.messageType)(message)

def reciveMessageFromServer():
    while True:
        try:
            message = pickle.loads(routerServerSide.recv(util.getDefaultBufferSize()))
            print("E' arrivato un messaggio dal SERVER.");
            message = managementServerMessage(message)
            routerServerSide.send(pickle.dumps(message))
        except OSError:
            break

def createConnectionWithServer():
    routerServerSide.connect(util.getServerSocket())
    Thread(target=reciveMessageFromServer).start()

def createConnectionWithClients():
    routerClientSide.listen(5)
    while True:
        client, address = listen.accept()
        print("%s:%s si è collegato." % client_address)


def main():
    macServerSide = input('Inserire il MAC Address dell\'interfaccia lato SERVER: ')
    macClientSide = input('Inserire il MAC Address dell\'interfaccia lato CLIENT: ')
    createConnectionWithServer()
    createConnectionWithClients()

if __name__ == "__main__":
    main()
