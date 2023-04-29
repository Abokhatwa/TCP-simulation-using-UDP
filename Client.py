import socket
import random
import zlib
data = []
data.append("Saeed")
data.append("Hossam")
data.append("Ehab")
serverAddressPort = ("127.0.0.1", 20001)

bufferSize = 1024

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
seq_num = 0
while seq_num < len(data):
    checksum = zlib.crc32(data[seq_num])
    packet = str(seq_num) + '|'+ str(checksum) + '|' + data[seq_num]
    if random.random() > 0.1:
        UDPClientSocket.sendto(packet.encode(), serverAddressPort)
        print("Packet sent")
    else:
        print("Packet lost")
    print('Sent packet:', seq_num)
    UDPClientSocket.settimeout(1.0)
    try:
        ack,addr = UDPClientSocket.recvfrom(bufferSize)
        ack_num = int(ack.decode())
        print(str(ack_num))
        if ack_num == seq_num:
            seq_num += 1
    except socket.timeout:
        print('Timeout occurred, retransmitting packet:', seq_num)
UDPClientSocket.close()