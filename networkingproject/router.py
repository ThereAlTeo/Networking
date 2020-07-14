import signal
import sys
from socket import AF_INET, socket, SOCK_STREAM
from classes.message import Message, MessageType
from utilities import Utilities as util
from threading import Thread


class Router:
    def __init__(self):
        self.macServerSide = util.mac_gen()
        self.macClientSide = util.mac_gen()
        # Dizionario che continene Key=IndirizzoIP Value=socket
        self.clientIpSocket = {}
        # Lista che mi contiene tutte le socket dei client
        self.broadcastMessage = []
        self.ipServerSide = ''
        self.ipClientSide = ''
        self.routerServerSide = socket(AF_INET, SOCK_STREAM)
        self.routerClientSide = socket(AF_INET, SOCK_STREAM)
        self.create_connection_with_server()
        self.create_connection_with_clients()
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGQUIT, self.exit)

    def exit(self, signum, frame):
        print("Uscita dallo script")
        try:
            self.routerServerSide.close()
            self.routerClientSide.close()
        except:
            print("Errore nella chiusa dei socket")
        finally:
            sys.exit(0)

    def create_connection_with_clients(self):
        util.set_default_socket(self.routerClientSide)
        self.routerClientSide.listen(5)
        while True:
            client, address = self.routerClientSide.accept()
            print("%s:%s si è collegato." % address)
            self.broadcastMessage.append(client)
            Thread(target=self.receive_message_from_client, args=(client,)).start()

    def create_connection_with_server(self):
        self.routerServerSide.connect((util.hostIP, util.hostPort))
        Thread(target=self.recive_message_from_server).start()

    def welcome_type(self, message: Message):
        print("Il SERVER ha dato il Benvenuto!")
        message.prepare_for_next_message()
        message.source_ip = "255.255.255.255"
        message.source_mac = self.macServerSide
        message.message_type = MessageType.DHCP_ROUTER_REQUEST
        message.text = "MyClientSocketName: " + self.routerClientSide.getsockname()[0] + "," + str(
            self.routerClientSide.getsockname()[1]) + "\n"
        return message

    def router_interface_ip(self, message: Message):
        print("Il SERVER ha restituito gli indirizzi IP delle interfacce lato client e server!")
        content = message.text
        message.prepare_for_next_message()
        message.message_type = MessageType.NONE
        self.ipServerSide = content.split("\n")[0].split(":")[1]
        self.ipClientSide = content.split("\n")[1].split(":")[1]
        return message

    def management_server_message(self, message: Message):
        switcher = {
            MessageType.WELCOME: self.welcome_type,
            MessageType.DHCP_ROUTER_ACK: self.router_interface_ip,
            MessageType.DHCP_REQUEST: self.welcome_type,
            MessageType.ROUTER_LIST_REQUEST: self.welcome_type,
        }
        return switcher.get(message.message_type)(message)

    def recive_message_from_server(self):
        while True:
            try:
                message = util.deserializeClass(self.routerServerSide.recv(util.getDefaultBufferSize()))
                print("E' arrivato un messaggio dal SERVER.")
                if message.message_type == MessageType.DHCP_ACK:
                    for state in self.broadcastMessage:
                        state.send(util.serializeClass(message))
                elif message.message_type == MessageType.CLIENT_RECEIVE_MESSAGE or message.message_type == MessageType.CLIENT_NOT_FOUND or \
                        message.message_type == MessageType.CLIENT_LIST_RESPONSE:
                    self.clientIpSocket[message.destination_ip].send(util.serializeClass(message))
                else:
                    message = self.management_server_message(message)
                    self.routerServerSide.send(util.serializeClass(message))
            except OSError:
                break

    def receive_message_from_client(self, client: socket):
        while True:
            try:
                message = util.deserializeClass(client.recv(util.getDefaultBufferSize()))
                if message.message_type == MessageType.CLIENT_IDENTIFY:
                    self.clientIpSocket[message.source_ip] = client
                else:
                    self.routerServerSide.send(util.serializeClass(message))
            except Exception as e:
                break


def main():
    Router()


if __name__ == "__main__":
    main()
