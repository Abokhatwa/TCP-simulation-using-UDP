import socket
from utilities import *

serverAddressPort = ("127.0.0.1", 20001)
window_size = 1024

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(serverAddressPort)
tcp_recv(window_size,UDPServerSocket)