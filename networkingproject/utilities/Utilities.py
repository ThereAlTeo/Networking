import pickle
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


def set_default_socket(item):
    """
    Set the default binding for the socket.
    Parameters
    ----------
    item: socket
    """
    return item.bind(('127.0.0.1', 0))
