import sys, signal
import http.server
import socketserver
import random
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from classes.message import Message, MessageType
from utilities import Utilities as util

# Dizionario per entità generica in ingresso Key=socket Value=socketName
entitySocketName = {}
# Dizionario che contiene Key=socket del router Value=socketName del router
socketNameDictionary = {}
# Dizionario che contiene key=indirizzo pubblico della rete Value=socket del router da cui è gestita
routerNetwork = {}
# Dizionario che contiene key=indirizzo lato server del router Value= indirizzo pubblico della rete
routerInterfaceIP = {}
# Dizionario che contiene Key=indirizzo lato server Value= lista di client all'iterno della rete
clientInsideNetwork = {}
routerConnected = 1
SERVER = None
serverMacAddress = "52:AB:0A:DF:10:DC"
serverIPAddress = "195.1.10.10"


def accept_incoming_client():
    while True:
        print("Attendo prossima connessione ...")
        client, clientAddress = SERVER.accept()
        print("Benvenuto %s:%s !" % clientAddress)
        message = Message()
        message.source_mac = serverMacAddress
        message.source_ip = serverIPAddress
        message.message_type = MessageType.WELCOME

        client.send(util.serializeClass(message))
        entitySocketName[client] = clientAddress
        Thread(target=client_management, args=(client,)).start()


def prepare_for_next_message(message: Message):
    message.prepare_for_next_message()
    message.source_mac = serverMacAddress
    message.source_ip = serverIPAddress


def generate_server_ip(publicnetwork: str):
    global routerConnected
    if routerConnected == 9:
        routerConnected = 11
    elif routerConnected >= 254:
        raise Exception("Non è possibile aggiungere nuovi router")
    routerConnected += 1
    serverSideIP = "195.1.10." + routerConnected
    routerInterfaceIP[serverSideIP] = publicnetwork
    clientInsideNetwork[serverSideIP] = []
    return serverSideIP


def generate_client_ip(content: str, client):
    socketNameDictionary[client] = content.split(":")[1]
    publicNetwork = ""
    while True:
        publicNetwork = random.randint(1, 92) + random.randint(1, 10) + "10.1"
        if not (publicNetwork in routerNetwork):
            break
    routerNetwork[publicNetwork] = client
    return publicNetwork


def create_router_ips(message: Message, client):
    print("Il SERVER sta generando gli indirizzi IP per %s:%s" % entitySocketName[client])
    content = message.text
    print(content)
    prepare_for_next_message(message)
    message.message_type = MessageType.DHCP_ROUTER_ACK
    publicnetwork = generate_client_ip(content, client)
    message.text = "ServerIP:" + generate_server_ip(publicnetwork) + "\nClienIP:" + publicnetwork
    return message


def create_router_list(message: Message, client):
    print("Il SERVER sta restituendo il nome delle reti disponibili")
    content = message.text
    print(content)
    prepare_for_next_message(message)
    if len(routerNetwork) > 0:
        message.message_type = MessageType.ROUTER_LIST_RESPONSE
        message.text = "NetworkNames:" + "-".join(list(routerNetwork.keys()))
    else:
        message.message_type = MessageType.ROUTER_LIST_EMPTY
    return message


def server_action(message: Message, client):
    switcher = {
        MessageType.DHCP_ROUTER_REQUEST: create_router_ips,
        MessageType.DHCP_DISCOVER: create_router_ips,
        MessageType.DHCP_REQUEST: create_router_ips,
        MessageType.ROUTER_LIST_REQUEST: create_router_list,
    }
    return switcher.get(message.message_type)(message, client)


def client_management(client):
    while True:
        try:
            message = util.deserializeClass(client.recv(util.getDefaultBufferSize()))
            message = server_action(message, client)
            client.send(util.serializeClass(message))
        except Exception as e:
            break


def main():
    global SERVER
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(util.getServerSocket())
    SERVER.listen(5)
    ACCEPT_THREAD = Thread(target=accept_incoming_client)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()


if __name__ == "__main__":
    main()
