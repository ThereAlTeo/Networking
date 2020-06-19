from socket import AF_INET, socket, SOCK_STREAM
from classes.message import Message, MessageType
from utilities import Utilities as util
import sys, signal
import http.server
import socketserver
from threading import Thread

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
    message.source_ip = "255.255.255.255"
    message.source_mac = macServerSide
    message.message_type = MessageType.DHCP_ROUTER_REQUEST
    message.text = "MyClientSocketName:" + routerClientSide.getsockname() + "\n"
    return message


def managementServerMessage(message):
    switcher = {
        MessageType.WELCOME: welcomeType,
        MessageType.DHCP_REQUEST: welcomeType,
        MessageType.ROUTER_LIST_REQUEST: welcomeType,
    }
    return switcher.get(message.messageType)(message)


def reciveMessageFromServer():
    while True:
        try:
            message = util.deserializeClass(routerServerSide.recv(util.getDefaultBufferSize()))
            print("E' arrivato un messaggio dal SERVER.")
            message = managementServerMessage(message)
            routerServerSide.send(util.serializeClass(message))
        except OSError:
            break


def createConnectionWithServer():
    routerServerSide.connect(util.getServerSocket())
    Thread(target=reciveMessageFromServer).start()


def createConnectionWithClients():
    routerClientSide.listen(5)
    while True:
        client, address = routerClientSide.accept()
        print("%s:%s si è collegato." % address)


def main():
    macServerSide = input('Inserire il MAC Address dell\'interfaccia lato SERVER: ')
    macClientSide = input('Inserire il MAC Address dell\'interfaccia lato CLIENT: ')
    createConnectionWithServer()
    createConnectionWithClients()


if __name__ == "__main__":
    main()
