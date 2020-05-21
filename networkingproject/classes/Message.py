from enum import Enum

class MessageType(Enum):
    NONE = 0
    DHCPDISCOVER = 1
    DHCPOFFER = 2
    DHCPREQUEST = 3
    DHCPACK = 4
    ROUTERLISTREQUEST = 5
    ROUTERLISTRESPONSE = 6
    WELCOME = 7

class Message:
    def __init__(self, CompactMessage):
        self.sourceMac = CompactMessage[0:17]
        self.destinationMac = CompactMessage[17:34]
        ipAddressSection = [i for i, char in enumerate(CompactMessage) if char=="."]
        self.sourceIP = CompactMessage[34:ipAddressSection[2]+2]
        self.destinationIP = CompactMessage[ipAddressSection[2]+2:ipAddressSection[5]+2]
        #ultimo byte però deve essere a 2 cifre

    def __init__(self):
        self.sourceIP = "0.0.0.0"
        self.destinationIP = "255.255.255.255"
        self.sourceMac = "00:00:00:00:00:00"
        self.destinationMac = "00:00:00:00:00:00"
        self.messageType = MessageType.NONE;
        self.message = ""

    def __str__(self):
        return "{0}{1}{2}{3}{4}".format(self.sourceMac, self.destinationMac, self.sourceIP, self.destinationIP, self.message);

    def setMessageType(self, type):
        self.messageType = type
