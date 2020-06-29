from socket import AF_INET, socket, SOCK_STREAM
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
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((target_ip, target_port))
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

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
        if message.message_type == MessageType.ROUTER_LIST_RESPONSE:
            print('Printing all the Routers Available')
            print(message.text)

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
        message.message_type = MessageType.WELCOME
        self.sock.send(Utilities.serializeClass(message))
        self.sock.close()
        sys.exit(0)


def __main__():
    Client(Utilities.hostIP, Utilities.hostPort)


if __name__ == "__main__":
    __main__()
