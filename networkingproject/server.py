import sys, signal
import http.server
import socketserver
import random
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from classes.message import Message, MessageType
from utilities import Utilities as util

"Dizionario che continene Key=IndiizzoIP pubblico del router Value=socketName alla quale i client devono collegarsi"
routerSocketName = {}
"Dizionario che continene Key=socket diretta verso router Value=IndirizzoIP pubblico del router"
routerIP = {}
"Dizionario che continene Key=socket diretta verso router Value=IndirizzoIP pubblico del router"
routerIP = {}
"Dizionario che contiene key=indirizzo lato client router Value=indirizzo lato server router. PROBABILMENTE INUTILE"
routerInterfaceIP = {}

routerConnected = 0
SERVER = None
serverMacAddress = "52:AB:0A:DF:10:DC"
serverIPAddress = "195.1.10.10"


def accept_incoming_client():
    while True:
        print("Attendo prossima connessione ...")
        client, clientAddress = SERVER.accept()
        print("Benvenuto %s:%s !" % clientAddress)
        message = Message.empty()
        message.source_mac = serverMacAddress
        message.source_ip = serverIPAddress
        message.message_type = MessageType.WELCOME

        client.send(util.serializeClass(message))
        Thread(target=client_management, args=(client,)).start()

"TODO: Ripensare al nome e all'operato della funzione"
def prepare_for_next_message_to_client(message: Message):
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
    serverSideIP = "195.1.10." + str(routerConnected)
    routerInterfaceIP[publicnetwork] = serverSideIP
    return serverSideIP


def generate_client_ip(content: str, client):
    publicNetwork = ""
    while True:
        publicNetwork = str(random.randint(1, 92)) + '.' + str(random.randint(1, 10)) + ".10.1"
        if not (publicNetwork in routerSocketName):
            break
    routerSocketName[publicNetwork] = content.split(":")[1]
    routerIP[client] = publicNetwork

    return publicNetwork


def create_router_ips(message: Message, client):
    print("Il SERVER sta generando gli indirizzi IP per %s:%s" % client.getsockname())
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)
    message.message_type = MessageType.DHCP_ROUTER_ACK
    publicnetwork = generate_client_ip(content, client)
    message.text = "ServerIP:" + generate_server_ip(publicnetwork) + "\nClienIP:" + publicnetwork
    return message


def create_router_list(message: Message, client):
    print("Il SERVER sta restituendo il nome delle reti disponibili")
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)
    message.message_type = MessageType.DHCP_OFFER
    if len(routerSocketName) > 0:
        message.message_type = MessageType.ROUTER_LIST_RESPONSE
        routerSocketNameList = [key + "-" + routerSocketName[key] for key in routerSocketName]
        message.text = "-".join(routerSocketNameList)
    else:
        message.message_type = MessageType.ROUTER_LIST_EMPTY
    return message


def offer_ip_to_client(message: Message, client):
    print("Il SERVER offre un indirizzo IP relativo alla sottorete scelta")
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)
    message.message_type = MessageType.DHCP_ACK

    return message


def ack_ip_to_client(message: Message, client):
    print("Il SERVER conferma l'indirizzo IP al client")
    content = message.text
    print(content)

    return message


def client_send_message(message: Message, client):
    print("Il SERVER riceve notifica da parte del client, il quale vorrebbe inviare un messaggio")

    #if

    content = message.text
    print(content)

    return message


def client_exit(message: Message, client):
    print("Il SERVER riceve uscita da parte di client")
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)

    return message


def server_action(message: Message, client):
    switcher = {
        MessageType.DHCP_ROUTER_REQUEST: create_router_ips,
        MessageType.DHCP_DISCOVER: offer_ip_to_client,
        MessageType.DHCP_REQUEST: ack_ip_to_client,
        MessageType.ROUTER_LIST_REQUEST: create_router_list,
        MessageType.CLIENT_SEND_MESSAGE: client_send_message,
    }
    return switcher.get(message.message_type)(message, client)


def client_management(client):
    while True:
        try:
            message = util.deserializeClass(client.recv(util.getDefaultBufferSize()))
            print(message.message_type)
            if message.message_type == MessageType.CLIENT_EXIT:
                client_exit(message, client)
            elif message.message_type == MessageType.CLIENT_SEND_MESSAGE:
                client_send_message(message, client)
            elif message.message_type != MessageType.NONE:
                message = server_action(message, client)
                client.send(util.serializeClass(message))
                if message.message_type == MessageType.ROUTER_LIST_RESPONSE:
                    client.close()
                    break
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
