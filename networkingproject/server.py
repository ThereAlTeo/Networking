import random
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from classes.message import Message, MessageType
from utilities import Utilities as util


class Server:
    def __init__(self, target_ip: str, target_port: str):
        self.routerConnected = 0
        self.serverMacAddress = "52:AB:0A:DF:10:DC"
        self.serverIPAddress = "195.1.10.10"
        "Dizionario che continene Key=IndiizzoIP pubblico del router Value=socketName alla quale i client devono collegarsi"
        self.routerSocketName = {}
        "Dizionario che continene Key=socket diretta verso router Value=IndirizzoIP pubblico del router"
        self.routerIP = {}
        "Dizionario che continene Key=socket del router Value=lista di indirizzi IP connessi"
        self.clientConnectedInRouter = {}
        "Dizionario che contiene key=indirizzo lato client router Value=indirizzo lato server router. PROBABILMENTE INUTILE"
        self.routerInterfaceIP = {}
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind((target_ip, target_port))
        self.serverSocket.listen(5)
        ACCEPT_THREAD = Thread(target=self.accept_incoming_client)
        ACCEPT_THREAD.start()
        ACCEPT_THREAD.join()
        self.serverSocket.close()

    def accept_incoming_client(self):
        while True:
            print("Attendo prossima connessione ...")
            client, clientAddress = self.serverSocket.accept()
            print("Benvenuto %s:%s !" % clientAddress)
            message = Message.empty()
            message.source_mac = self.serverMacAddress
            message.source_ip = self.serverIPAddress
            message.message_type = MessageType.WELCOME

            client.send(util.serializeClass(message))
            Thread(target=self.client_management, args=(client,)).start()

    def client_management(self, client: socket):
        while True:
            try:
                message = util.deserializeClass(client.recv(util.getDefaultBufferSize()))
                if message.message_type == MessageType.CLIENT_EXIT:
                    self.client_exit(message, client)
                elif message.message_type == MessageType.CLIENT_SEND_MESSAGE:
                    self.client_send_message(message, client)
                elif message.message_type != MessageType.NONE:
                    message = self.server_action(message, client)
                    client.send(util.serializeClass(message))
                    if message.message_type == MessageType.ROUTER_LIST_RESPONSE:
                        client.close()
                        break
            except Exception as e:
                break

    def prepare_for_next_message_to_client(self, message: Message):
        message.prepare_for_next_message()
        message.source_mac = self.serverMacAddress
        message.source_ip = self.serverIPAddress

    def generate_server_ip(self, publicnetwork: str):
        if self.routerConnected == 9:
            self.routerConnected = 11
        elif self.routerConnected >= 254:
            raise Exception("Non è possibile aggiungere nuovi router")
        self.routerConnected += 1
        serverSideIP = "195.1.10." + str(self.routerConnected)
        self.routerInterfaceIP[publicnetwork] = serverSideIP
        return serverSideIP

    def generate_client_ip(self, content: str, client: socket):
        publicNetwork = ""
        while True:
            publicNetwork = str(random.randint(1, 92)) + '.' + str(random.randint(1, 10)) + ".10.1"
            if not (publicNetwork in self.routerSocketName):
                break
        self.routerSocketName[publicNetwork] = content.split(":")[1]
        self.routerIP[client] = publicNetwork
        self.clientConnectedInRouter[client] = []
        return publicNetwork

    def create_router_ips(self, message: Message, client: socket):
        print("Il SERVER sta generando gli indirizzi IP per %s:%s" % client.getsockname())
        content = message.text
        print(content)
        self.prepare_for_next_message_to_client(message)
        message.message_type = MessageType.DHCP_ROUTER_ACK
        publicnetwork = self.generate_client_ip(content, client)
        message.text = "ServerIP:" + self.generate_server_ip(publicnetwork) + "\nClienIP:" + publicnetwork
        return message

    def create_router_list(self, message: Message, client: socket):
        print("Il SERVER sta restituendo il nome delle reti disponibili")
        content = message.text
        print(content)
        self.prepare_for_next_message_to_client(message)
        if len(self.routerSocketName) > 0:
            message.message_type = MessageType.ROUTER_LIST_RESPONSE
            routerSocketNameList = [key + "-" + self.routerSocketName[key] for key in self.routerSocketName]
            message.text = "".join(routerSocketNameList)
        else:
            message.message_type = MessageType.ROUTER_LIST_EMPTY
        return message

    def ack_ip_to_client(self, message: Message, client: socket):
        print("Il SERVER offre un indirizzo IP relativo alla sottorete scelta")
        content = message.text
        print(content)
        self.prepare_for_next_message_to_client(message)
        message.message_type = MessageType.DHCP_ACK
        ipAddressNetwork = self.routerIP[client].split(".")
        ipAddressACK = ".".join(ipAddressNetwork[:3]) + "." + str(len(self.clientConnectedInRouter[client]) + 2)
        self.clientConnectedInRouter[client].append(ipAddressACK)
        message.text = content + "," + ipAddressACK
        return message

    def send_message_to_router(self, message: Message, router: socket):
        router.send(util.serializeClass(message))

    def client_send_message(self, message: Message, client: socket):
        print("Il SERVER riceve notifica da parte del client, il quale vorrebbe inviare un messaggio")
        content = message.text
        print(content)
        for router in self.clientConnectedInRouter:
            if message.destination_ip in self.clientConnectedInRouter[router]:
                message.message_type = MessageType.CLIENT_RECEIVE_MESSAGE
                self.send_message_to_router(message, router)

        message.prepare_for_next_message()
        message.message_type = MessageType.CLIENT_NOT_FOUND
        message.text = content
        self.send_message_to_router(message, client)

    def client_exit(self, message: Message, client: socket):
        print("Il SERVER riceve uscita da parte di client")
        content = message.text
        print(content)
        self.clientConnectedInRouter[client].remove(message.source_ip)
        return message.empty()

    def create_client_list(self, message: Message, client: socket):
        message.prepare_for_next_message()
        message.source_ip = self.serverIPAddress
        message.source_mac = self.serverMacAddress
        message.message_type = MessageType.CLIENT_LIST_RESPONSE
        clientList = []
        for router in self.clientConnectedInRouter:
            for item in self.clientConnectedInRouter[router]:
                clientList.append(item)

        message.text = "-".join(clientList)
        return message

    def server_action(self, message: Message, client: socket):
        switcher = {
            MessageType.DHCP_ROUTER_REQUEST: self.create_router_ips,
            MessageType.DHCP_REQUEST: self.ack_ip_to_client,
            MessageType.ROUTER_LIST_REQUEST: self.create_router_list,
            MessageType.CLIENT_LIST_REQUEST: self.create_client_list,
        }
        return switcher.get(message.message_type)(message, client)


def main():
    Server(util.hostIP, util.hostPort)


if __name__ == "__main__":
    main()
