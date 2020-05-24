import pickle

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
