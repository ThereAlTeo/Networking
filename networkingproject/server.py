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
"Dizionario che continene Key=socket del router Value=lista di indirizzi IP connessi"
clientConnectedInRouter = {}

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


def generate_client_ip(content: str, client: socket):
    publicNetwork = ""
    while True:
        publicNetwork = str(random.randint(1, 92)) + '.' + str(random.randint(1, 10)) + ".10.1"
        if not (publicNetwork in routerSocketName):
            break
    routerSocketName[publicNetwork] = content.split(":")[1]
    routerIP[client] = publicNetwork
    clientConnectedInRouter[client] = []
    return publicNetwork


def create_router_ips(message: Message, client: socket):
    print("Il SERVER sta generando gli indirizzi IP per %s:%s" % client.getsockname())
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)
    message.message_type = MessageType.DHCP_ROUTER_ACK
    publicnetwork = generate_client_ip(content, client)
    message.text = "ServerIP:" + generate_server_ip(publicnetwork) + "\nClienIP:" + publicnetwork
    return message


def create_router_list(message: Message, client: socket):
    print("Il SERVER sta restituendo il nome delle reti disponibili")
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)
    if len(routerSocketName) > 0:
        message.message_type = MessageType.ROUTER_LIST_RESPONSE
        routerSocketNameList = [key + "-" + routerSocketName[key] for key in routerSocketName]
        message.text = "-".join(routerSocketNameList)
    else:
        message.message_type = MessageType.ROUTER_LIST_EMPTY
    return message


def ack_ip_to_client(message: Message, client: socket):
    print("Il SERVER offre un indirizzo IP relativo alla sottorete scelta")
    content = message.text
    print(content)
    prepare_for_next_message_to_client(message)
    message.message_type = MessageType.DHCP_ACK
    ipAddressNetwork = routerIP[client].split(".")
    ipAddressACK = ".".join(ipAddressNetwork[:3]) + "." + str(len(clientConnectedInRouter[client]) + 2)
    clientConnectedInRouter[client].append(ipAddressACK)
    message.text = content + "," + ipAddressACK
    return message


def send_message_to_router(message: Message, router: socket):
    router.send(util.serializeClass(message))


def client_send_message(message: Message, client: socket):
    print("Il SERVER riceve notifica da parte del client, il quale vorrebbe inviare un messaggio")
    content = message.text
    print(content)

    for router in clientConnectedInRouter:
        if content in clientConnectedInRouter[router]:
            send_message_to_router(message, router)

    message.prepare_for_next_message()
    message.message_type = MessageType.CLIENT_NOT_FOUND
    message.text = content
    send_message_to_router(message, client)


def client_exit(message: Message, client: socket):
    print("Il SERVER riceve uscita da parte di client")
    content = message.text
    print(content)
    clientConnectedInRouter[client].remove(message.source_ip)
    return message.empty()


def create_client_list(message: Message, client: socket):
    message.prepare_for_next_message()
    message.source_ip = serverIPAddress
    message.source_mac = serverMacAddress
    message.message_type = MessageType.CLIENT_LIST_RESPONSE
    message.text = "-".join(list(clientConnectedInRouter.keys()))
    return message


def server_action(message: Message, client: socket):
    switcher = {
        MessageType.DHCP_ROUTER_REQUEST: create_router_ips,
        MessageType.DHCP_REQUEST: ack_ip_to_client,
        MessageType.ROUTER_LIST_REQUEST: create_router_list,
        MessageType.CLIENT_LIST_REQUEST: create_client_list,
    }
    return switcher.get(message.message_type)(message, client)


def client_management(client: socket):
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
