import sys, signal
import http.server
import socketserver
import random
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from classes.Message import Message, MessageType
from utilities import Utilities as util

#Dizionario per entità generica in ingresso Key=socket Value=socketName
entitySocketName = {}
#Dizionario che contiene Key=socket del router Value=socketName del router
socketNameDictionary = {}
#Dizionario che contiene key=indirizzo pubblico della rete Value=socket del router da cui è gestita
routerNetwork = {}
routerConnected = 1;
SERVER = None
serverMacAddress = "52:AB:0A:DF:10:DC"
serverIPAddress = "195.1.10.10"

def acceptIncomingClient():
    while True:
        print("Attendo prossima connessione ...")
        client, clientAddress = SERVER.accept()
        print("Benvenuto %s:%s !" % clientAddress)
        message = Message()
        message.sourceMac = serverMacAddress
        message.sourceIP = serverIPAddress
        message.messageType = messageType.WELCOME

        client.send(util.serializeClass(message))
        entitySocketName[client] = clientAddress
        Thread(target=clientManagement, args=(client,)).start()

def prepareForNextMessage(message):
    message.prepareForNextMessage()
    message.sourceMac = serverMacAddress
    message.sourceIP = serverIPAddress

def generateServerIP():
    if routerConnected == 9:
        routerConnected = 11
    else if routerConnected >= 254:
        raise Exception("Non è possibile aggiungere nuovi router")
    routerConnected += 1
    return "195.1.10." + routerConnected

def generateClientIP(content, client):
    socketNameDictionary[client] = content.split(":")[1]
    publicNetwork = ""
    while True:
        publicNetwork = random.randint(1, 92) + random.randint(1, 10) + "10.1"
        if !(publicNetwork in routerNetwork):
            break;
    routerNetwork[publicNetwork] = client
    return publicNetwork

def createRouterIps(message, client):
    print("Il SERVER sta generando gli indirizzi IP per %s:%s" % entitySocketName[client])
    content = message.message
    print(content)
    prepareForNextMessage(message)
    message.messageType = MessageType.DHCPROUTERACK
    messa.message = "ServerIP: " + generateServerIP() + "\nClienIP: " + generateClientIP(content, client)
    return message

def serverAction(message, client):
    switcher = {
        MessageType.DHCPROUTERREQUEST: createRouterIps,
        #messageType.DHCPDISCOVER: createRouterIps,
        #messageType.DHCPREQUEST: createRouterIps,
        #messageType.ROUTERLISTREQUEST: print("a"),
        #messageType.WELCOME: print("a"),
    }

    return switcher.get(message.messageType)(message, client)

def clientManagement(client):
    while True:
        try:
            message = util.deserializeClass(client.recv(util.getDefaultBufferSize()))
            message = serverAction(message, client)
            client.send(util.serializeClass(message))
        except Exception as e:
            break

def main():
    global SERVER
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(util.getServerSocket())
    SERVER.listen(5)
    ACCEPT_THREAD = Thread(target=acceptIncomingClient)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

if __name__ == "__main__":
    main()
