import socket
import random
import zlib
import struct
from utilities import *

#TCP header
# Fields:
# Source port (unsigned short 2 bytes): this is a 16 bit field that specifies the port number of the sender. 
# Destination port (unsigned short 2 bytes): this is a 16 bit field that specifies the port number of the receiver.
# Sequence number (unsigned int 4 bytes): the sequence number is a 32 bit field that indicates how much data is sent during the TCP session. When you establish a new TCP connection (3 way handshake) then the initial sequence number is a random 32 bit value. The receiver will use this sequence number and sends back an acknowledgment. Protocol analyzers like wireshark will often use a relative sequence number of 0 since it’s easier to read than some high random number.
# Acknowledgment number (unsigned int 4 bytes): this 32 bit field is used by the receiver to request the next TCP segment. This value will be the sequence number incremented by 1.
# DO(2 bytes1): this is the 4 bit data offset field, also known as the header length. It indicates the length of the TCP header so that we know where the actual data begins.
# RSV(2 bytes2): these are 3 bits for the reserved field. They are unused and are always set to 0.
# Flags(2 bytes3 ->unsigned short): there are 9 bits for flags, we also call them control bits. We use them to establish connections, send data and terminate connections:
    # URG  : urgent pointer. When this bit is set, the data should be treated as priority over other data.
    # ACK: used for the acknowledgment.
    # PSH: this is the push function. This tells an application that the data should be transmitted immediately and that we don’t want to wait to fill the entire TCP segment.
    # RST: this resets the connection, when you receive this you have to terminate the connection right away. This is only used when there are unrecoverable errors and it’s not a normal way to finish the TCP connection.
    # SYN: we use this for the initial three way handshake and it’s used to set the initial sequence number.
    # FIN: this finish bit is used to end the TCP connection. TCP is full duplex so both parties will have to use the FIN bit to end the connection. This is the normal method how we end an connection.
# Window(unsigned short): the 16 bit window field specifies how many bytes the receiver is willing to receive. It is used so the receiver can tell the sender that it would like to receive more data than what it is currently receiving. It does so by specifying the number of bytes beyond the sequence number in the acknowledgment field.
# Checksum(unsigned short): 16 bits are used for a checksum to check if the TCP header is OK or not.
# Urgent pointer(unsigned short): these 16 bits are used when the URG bit has been set, the urgent pointer is used to indicate where the urgent data ends.
# Options(not implemented): this field is optional and can be anywhere between 0 and 320 bits.

data = []
data.append("Saeed")
data.append("Hossam")
data.append("Ehab")

clientAddressPort=("127.0.0.1", 20023)
serverAddressPort = ("127.0.0.1", 20001)


# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind(clientAddressPort)

seq_num = 0
while seq_num < len(data):
        
    Source_port=clientAddressPort[1]
    Destination_port=serverAddressPort[1]

    Sequence_number=seq_num
    data_t=data[seq_num]
    Acknowledgment_number=0+len(data_t)

    Flags=20480 #"0101000000000000"
    Window=1024
    Urgent_pointer=0

    Tcp_send(data_t,Sequence_number,Acknowledgment_number,Flags
             ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort) 
    
    print('Sent packet:', seq_num)
    UDPClientSocket.settimeout(1.0)

    try:
        ack,addr = UDPClientSocket.recvfrom(Window)
        ack_num = int(ack.decode())
        print(str(ack_num))
        if ack_num == seq_num:
            seq_num += 1
    except socket.timeout:
        print('Timeout occurred, retransmitting packet:', seq_num)


UDPClientSocket.close()