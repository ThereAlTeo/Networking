from datetime import datetime
from socket import AF_INET, socket, SOCK_STREAM, SHUT_RDWR
from threading import Thread
from classes.message import Message, MessageType
from utilities import Utilities
import sys


class Client:
    """
    Client that connects to the server by the given IP then switches it's socket to a Router
    """

    def __init__(self, target_ip: str, target_port: str):
        """
        Init the Client that targets the server for a connection
        Parameters
        ----------
        target_ip: str
        target_port: str
        """
        self.ip = ""
        self.id = str(datetime.now().timestamp())
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((target_ip, target_port))
        receive_thread = Thread(target=self.receive)
        receive_thread.start()

    def handle_startup(self):
        """
        At the Welcome message, find the available subnets, picking the router given by the server.
        """
        print("Finding Available Subnets...")
        message = Message.empty()
        message.message_type = MessageType.ROUTER_LIST_REQUEST
        self.sock.send(Utilities.serializeClass(message))
        message = Utilities.deserializeClass(self.sock.recv(Utilities.getDefaultBufferSize()))
        if message.message_type == MessageType.ROUTER_LIST_EMPTY:
            print('No router found on server')
            self.exit()
        connections = {}
        for line in message.text.splitlines():
            connections[line[:line.find('-')]] = line[line.find(',') + 1:]
        print('Select a router to connect (type the IP):')
        for key in connections.keys():
            print("- " + key)
        selection = ""
        while selection not in connections.keys():
            selection = input('-> ')
        self.init_socket()
        self.sock.connect(('127.0.0.1', int(connections[selection])))
        message = Message.empty()
        message.message_type = MessageType.DHCP_REQUEST
        message.text = self.id
        self.sock.send(Utilities.serializeClass(message))
        self.await_for_ip()
        self.exit()

    def await_for_ip(self):
        """
        Wait for the server to give back a IP, if it's not mine, leave it
        """
        while True:
            message = Utilities.deserializeClass(self.sock.recv(Utilities.getDefaultBufferSize()))
            if message.text[:message.text.find(',')] == self.id and message.message_type == MessageType.DHCP_ACK:
                self.ip = message.text[message.text.find(',') + 1:]
                break
        # self.id_to_router()

    def id_to_router(self):
        """
        Send a message to the now connected router, tell them your IP
        """
        message = Message.empty()
        message.message_type = None
        message.source_ip = self.ip
        self.sock.send(Utilities.serializeClass(message))

    def receive(self):
        """
        Start a Thread that filters the requests received and manages the Messages received
        """
        while True:
            try:
                message = Utilities.deserializeClass(self.sock.recv(Utilities.getDefaultBufferSize()))
                switcher = {
                    MessageType.WELCOME: self.handle_startup
                }
                switcher.get(message.message_type)()
            except Exception as e:
                print(e)
                break

    def exit(self):
        """
        Exit the client gracefully, closing everything.
        """
        print("Shutting down the client...")
        message = Message.empty()
        message.source_ip = self.ip
        message.message_type = MessageType.CLIENT_EXIT
        self.sock.send(Utilities.serializeClass(message))
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()
        sys.exit(0)

    def init_socket(self):
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()
        self.sock = socket(AF_INET, SOCK_STREAM)


def __main__():
    Client(Utilities.hostIP, Utilities.hostPort)


if __name__ == "__main__":
    __main__()
