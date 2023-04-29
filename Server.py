import socket
import time
import hashlib
import zlib
localIP = "127.0.0.1"

localPort = 20001

bufferSize = 1024

msgFromServer = "Hello UDP Client"

bytesToSend = str.encode(msgFromServer)

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
expected_seq_num = 0
print("UDP server up and listening")
flag = 0
# Listen for incoming datagrams
while (True):
    data,addr = UDPServerSocket.recvfrom(bufferSize)
    packet = data.decode().split('|')
    seq_num = int(packet[0])
    checksum = packet[1]
    original_checksum = zlib.crc32(packet[2])
    if int(checksum)==original_checksum:
        if seq_num == expected_seq_num:
            ack = str(seq_num)
            UDPServerSocket.sendto(ack.encode(), addr)
            print('Received packet:', packet[2].encode("utf-8"))
            expected_seq_num += 1
        else:
            print('Received duplicate packet:', seq_num)
    else:
        print("Message corrupted,waiting for a retransmission")
    time.sleep(1.2)
    