import pickle
import random
from socket import socket

hostIP = 'localhost'
hostPort = 13000
BUFFERSIZE = 1024


def getServerSocket():
    return (hostIP, hostPort)


def getDefaultBufferSize():
    return BUFFERSIZE


def serializeClass(item):
    return pickle.dumps(item)


def deserializeClass(item):
    return pickle.loads(item)


def set_default_socket(item: socket):
    """
    Set the 127.0.0.1:0 binding for the socket.
    Args:
        item(socket): socket to bind to the default
    Returns:
        socket: the socket bind with the default values
    """
    return item.bind(('127.0.0.1', 0))


def mac_gen():
    """
    Return a MAC randomly generated
    Returns:
        str: the MAC generated
    """
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    picks = []
    for x in range(6):
        pick = random.choices(values, k=2)
        picks.append(''.join(pick))
    return '-'.join(picks)
