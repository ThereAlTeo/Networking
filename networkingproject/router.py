from socket import AF_INET, socket, SOCK_STREAM
from classes.message import Message, MessageType
from utilities import Utilities as util
import sys, signal
import http.server
import socketserver
from threading import Thread

# Dizionario che continene Key=IndirizzoIP Value=socket
clientIpSocket = {}
#Dizionario che contine Key=IndirizzoIP Value=IndirizzoMac
clientMacSocket = {}

macServerSide = ''
ipServerSide = ''
macClientSide = ''
ipClientSide = ''
serverConnection = None

routerServerSide = socket(AF_INET, SOCK_STREAM)
routerClientSide = socket(AF_INET, SOCK_STREAM)


def welcome_type(message):
    print("Il SERVER ha dato il Benvenuto!")
    message.prepare_for_next_message()
    message.source_ip = "255.255.255.255"
    message.source_mac = macServerSide
    message.message_type = MessageType.DHCP_ROUTER_REQUEST
    message.text = "MyClientSocketName: " + routerClientSide.getsockname()[0] + "," + str(routerClientSide.getsockname()[1]) + "\n"
    return message


def router_interface_ip(message):
    global ipClientSide, ipServerSide
    print("Il SERVER ha restituito gli indirizzi IP delle interfacce lato client e server!")
    content = message.text
    print(content)
    message.prepare_for_next_message()
    message.message_type = MessageType.NONE
    ipServerSide = content.split("\n")[0].split(":")[1]
    ipClientSide = content.split("\n")[1].split(":")[1]
    return message


def management_server_message(message):
    switcher = {
        MessageType.WELCOME: welcome_type,
        MessageType.DHCP_ROUTER_ACK: router_interface_ip,
        MessageType.DHCP_REQUEST: welcome_type,
        MessageType.ROUTER_LIST_REQUEST: welcome_type,
    }
    return switcher.get(message.message_type)(message)


def recive_message_from_server():
    while True:
        try:
            message = util.deserializeClass(routerServerSide.recv(util.getDefaultBufferSize()))
            print("E' arrivato un messaggio dal SERVER.")
            message = management_server_message(message)
            if message.message_type == MessageType.DHCP_ACK or message.message_type == MessageType.DHCP_OFFER:
                for state in clientIpSocket.values():
                    state.send(util.serializeClass(message))
            elif message.message_type == MessageType.CLIENT_RECEIVE_MESSAGE or message.message_type == MessageType.CLIENT_NOT_FOUND:
                clientIpSocket[message.source_ip].send(util.serializeClass(message))
            else:
                routerServerSide.send(util.serializeClass(message))
        except OSError:
            break


def create_connection_with_server():
    routerServerSide.connect(util.getServerSocket())
    Thread(target=recive_message_from_server).start()


def recive_message_from_client(client):
    while True:
        try:
            message = client.recv(util.getDefaultBufferSize())
            routerServerSide.send(message)
        except Exception as e:
            break


def create_connection_with_clients():
    routerClientSide.listen(5)
    while True:
        client, address = routerClientSide.accept()
        print("%s:%s si è collegato." % address)
        Thread(target=recive_message_from_client, args=(client,)).start()


def main():
    global macClientSide, macServerSide
    macServerSide = input('Inserire il MAC Address dell\'interfaccia lato SERVER: ')
    macClientSide = input('Inserire il MAC Address dell\'interfaccia lato CLIENT: ')
    create_connection_with_server()
    create_connection_with_clients()


if __name__ == "__main__":
    main()
