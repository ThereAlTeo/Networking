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
    DHCP_ROUTE_RACK = 6
    ROUTER_LIST_REQUEST = 7
    ROUTER_LIST_RESPONSE = 8
    WELCOME = 9


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
