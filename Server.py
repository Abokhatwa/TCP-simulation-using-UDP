import socket
import time
import hashlib
import zlib
import struct

clientAddressPort=("127.0.0.1", 20023)
serverAddressPort = ("127.0.0.1", 20001)


bufferSize = 1024

msgFromServer = "Hello UDP Client"

bytesToSend = str.encode(msgFromServer)

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(serverAddressPort)

expected_seq_num = 0
print("UDP server up and listening")
# Listen for incoming datagrams
while (True):
    #data,addr = UDPServerSocket.recvfrom(bufferSize)
    data = UDPServerSocket.recvfrom(bufferSize)
    size_of_payload=len(data)-20
    unpacked_data = struct.unpack(f"2H 2I 4H {size_of_payload}s", data)

    source_port = unpacked_data[0]
    destination_port = unpacked_data[1]
    sequence_number = unpacked_data[2]
    acknowledgment_number = unpacked_data[3]
    flags = unpacked_data[4]
    window = unpacked_data[5]
    check_sum = unpacked_data[6]
    urgent_pointer = unpacked_data[7]
    payload = unpacked_data[8]







    packet = payload
    seq_num = sequence_number
    checksum = check_sum
    original_checksum = zlib.crc32(check_sum.encode())


    if int(checksum)==original_checksum:
        if seq_num == expected_seq_num:
            ack = str(seq_num)
            UDPServerSocket.sendto(ack.encode(), clientAddressPort)
            print('Received packet:', packet.encode("utf-8"))
            expected_seq_num += 1
        else:
            print('Received duplicate packet:', seq_num)
    else:
        print("Message corrupted,waiting for a retransmission")
    time.sleep(1.2)
