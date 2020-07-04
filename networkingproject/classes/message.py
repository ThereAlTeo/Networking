from enum import Enum


class MessageType(Enum):
    """
    Simple Enum that holds all the various types of Message that can be sent.
    """
    NONE = 0
    DHCP_DISCOVER = 1
    DHCP_OFFER = 2
    DHCP_REQUEST = 3
    DHCP_ROUTER_REQUEST = 4
    DHCP_ACK = 5
    DHCP_ROUTER_ACK = 6
    ROUTER_LIST_REQUEST = 7
    ROUTER_LIST_RESPONSE = 8
    ROUTER_LIST_EMPTY = 9
    WELCOME = 10
    CLIENT_EXIT = 11
    CLIENT_SEND_MESSAGE = 12
    CLIENT_RECEIVE_MESSAGE = 13
    CLIENT_NOT_FOUND = 14


class Message:
    """
    This class handles the messages itself, with source, destination, type and text.
    """

    def __init__(self, source_mac: str, source_ip: str, destination_mac: str, destination_ip: str,
                 message_type: MessageType, text: str):
        """
        Initializes the Message, there are no checks for the inputs, so care on what you do.

        Parameters
        ----------
        source_mac: str
        source_ip: str
        destination_mac: str
        destination_ip: str
        message_type: MessageType
        text: str
        """
        self.source_mac = source_mac
        self.source_ip = source_ip
        self.destination_mac = destination_mac
        self.destination_ip = destination_ip
        self.message_type = message_type
        self.text = text

    @classmethod
    def empty(cls):
        return cls("", "", "", "", MessageType.NONE, "")

    def prepare_for_next_message(self):
        self.destination_ip = self.source_ip
        self.destination_mac = self.source_mac
        self.message_type = MessageType.NONE
        self.text = ""
