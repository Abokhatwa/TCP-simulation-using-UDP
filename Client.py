import socket

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
    packet = str(seq_num) + '|' + data[seq_num]
    UDPClientSocket.sendto(packet.encode(), serverAddressPort)
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