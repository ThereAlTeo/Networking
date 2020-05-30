from socket import AF_INET, socket, SOCK_STREAM


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
        self.target_ip = target_ip
        self.target_port = target_port

    def connect(self):
        """
        Connect the Client to a Socket with the ip and port given in the constructor.
        """
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.target_ip, self.target_port))

    def __str__(self):
        """
        Return the Object in String format.
        Returns
        -------
        str
        """
        return "IP: " + self.target_ip + "\tPort: " + str(self.target_port)
