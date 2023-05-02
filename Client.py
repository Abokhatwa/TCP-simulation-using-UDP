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

# data = []
# data.append("Saeed")
# data.append("Hossam")
# data.append("Ehab")

clientAddressPort=("127.0.0.1", 20023)
serverAddressPort = ("127.0.0.1", 20001)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind(clientAddressPort)

user_input=input("enter HTTP request\n")
print(user_input)

# Split the request into lines
request_lines = user_input.split("\r\n")
# Get the first line, which contains the command
command_line = request_lines[0]
# Split the command line into its parts
command_parts = command_line.split(" ")
# Get the HTTP method (GET or POST) from the command
http_method = command_parts[0]

three_way_flag = 0
data = []
data.append("Saeed")
data.append("Hossam")
data.append("Ehab")
datapointer = 0
postflag = 0
getflag = 0
while three_way_flag==0:
    UDPClientSocket.settimeout(2.0)
    flags = 20482
    Source_port=clientAddressPort[1]
    Destination_port=serverAddressPort[1]
    Sequence_number=datapointer
    data_t=""
    Acknowledgment_number=0
    Window=1024
    Urgent_pointer=0
    Tcp_send(data_t,Sequence_number,Acknowledgment_number,flags
             ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort)
    print("SYN SENT,Waiting for an SYN-ACK")
    #time.sleep(1.2)
    try:
        synack,addr = UDPClientSocket.recvfrom(Window)
    except socket.timeout:
        print("Couldn't connect to the server, Retrying to connect!")
        continue
    size_of_payload=len(synack)-20
    unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",synack)
    flags = unpacked_data[4]
    sequence_number = unpacked_data[2]
    if flags==20498:
        flags = 20496
        print("SYN-ACK received,Sending ACK")
        Tcp_send(data_t,datapointer,sequence_number+1,flags
             ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort)
        three_way_flag=1
    print({"---------------------------------------------------------------"})
    time.sleep(1.5)

#-------------------------------------------#
Source_port=clientAddressPort[1]
Destination_port=serverAddressPort[1]
data_t=user_input

Flags=20480 #"0101000000000000"
Window=1024
Urgent_pointer=0

#-------------------------------------------------#

if http_method == "GET":
    Sequence_number=0
    Acknowledgment_number=1

    Tcp_send(data_t,Sequence_number,Acknowledgment_number,Flags
        ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort) 
    print('Sent packet:', Sequence_number)
    UDPClientSocket.settimeout(1.0)
    try:
        res,addr = UDPClientSocket.recvfrom(Window)
        size_of_payload=len(res)-20
        unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",res)
        res = unpacked_data[8].decode('utf-8')
        print("Received response: ",str(res))
        if res == "HTTP/1.1 200 OK": #file found
            getflag = 1
        else:
            getflag==0
    except socket.timeout:
        print('Timeout occurred, retransmitting packet:', Sequence_number)

    print("This is a GET command.")
elif http_method == "POST":
    Sequence_number=0
    Acknowledgment_number=0

    Tcp_send(data_t,Sequence_number,Acknowledgment_number,Flags
            ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort) 
    print('Sent packet:', Sequence_number)
    UDPClientSocket.settimeout(1.0)
    try:
        res,addr = UDPClientSocket.recvfrom(Window)
        size_of_payload=len(res)-20
        unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",res)
        res = unpacked_data[8].decode('utf-8')
        print("Received response: ",str(res))
        if res == "HTTP/1.1 200 OK":
            postflag = 1
    except socket.timeout:
        print('Timeout occurred, retransmitting packet:', Sequence_number)

    print("This is a POST command.")
else:
    print("Unknown HTTP method.")
if postflag==1:
    Sequence_number=1
    while datapointer < len(data):
        Source_port=clientAddressPort[1]
        Destination_port=serverAddressPort[1]

        data_t=data[datapointer]
        Acknowledgment_number=1

        Flags=20480 #"0101000000000000"
        Window=1024
        Urgent_pointer=0

        Tcp_send(data_t,Sequence_number,Acknowledgment_number,Flags
                    ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort) 

        print('Sent packet:', Sequence_number)
        UDPClientSocket.settimeout(1.0)
        try:
            ack,addr = UDPClientSocket.recvfrom(Window)
            ack_num = int(ack.decode())
            print("Received ACK: ",str(ack_num))
            if ack_num == Sequence_number+len(data[datapointer]):
                datapointer += 1
                Sequence_number = ack_num
        except socket.timeout:
            print('Timeout occurred, retransmitting packet:', Sequence_number)

    #-------------#
    UDPClientSocket.settimeout(None)
    flags = 20481
    Source_port=clientAddressPort[1]
    Destination_port=serverAddressPort[1]
    Sequence_number=0
    data_t=""
    Acknowledgment_number=0
    Window=1024
    Urgent_pointer=0
    Tcp_send(data_t,Sequence_number,Acknowledgment_number,flags
                ,Window,Urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort)
    fin,addr = UDPClientSocket.recvfrom(Window)
    size_of_payload=len(fin)-20
    unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",fin)
    flags = unpacked_data[4]
    if flags == 29496:
        UDPClientSocket.close()
    #-------------#
if getflag==1:
    msg = []
    expected_seq_num = 1
    UDPClientSocket.settimeout(None)
    while True:
        data, src_addr = UDPClientSocket.recvfrom(Window)
        size_of_payload=len(data)-20
        unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",data)
        source_port = unpacked_data[0]
        destination_port = unpacked_data[1]
        sequence_number = unpacked_data[2]
        acknowledgment_number = unpacked_data[3]
        flags = unpacked_data[4]
        window = unpacked_data[5]
        check_sum = unpacked_data[6]
        urgent_pointer = unpacked_data[7]
        payload = unpacked_data[8]
        if flags == 20481:
            serverFlags=29496
            Tcp_send("",0,sequence_number+1,serverFlags
            ,window,urgent_pointer,UDPClientSocket,serverAddressPort,src_addr=clientAddressPort)
            break
        src_ip=ip2int(src_addr[0])
        dest_ip=ip2int(UDPClientSocket.getsockname()[0])
        src_ip = struct.pack('!4B', *src_ip)
        dest_ip = struct.pack('!4B', *dest_ip)
        Reserved = 0
        protocol = socket.IPPROTO_TCP
        pseudo_header = struct.pack('!BBH', Reserved, protocol, len(data))
        pseudo_header = src_ip + dest_ip + pseudo_header

        TCP_header=struct.pack(f"2H 2I 4H",source_port,destination_port
                ,sequence_number,acknowledgment_number,
                flags,window,0,urgent_pointer)
        
        verify = verify_checksum(pseudo_header + TCP_header + payload, check_sum)
        if verify == 0xFFFF:
            if int(sequence_number) == int(expected_seq_num):

                #save packets into textfile
                msg.append(payload.decode("UTF-8"))
                ack = sequence_number+size_of_payload
                ack = str(ack)
                clientAddressPort=src_addr
                UDPClientSocket.sendto(ack.encode(), clientAddressPort)
                print('Received packet:', payload)
                expected_seq_num = ack
            else:
                print('Received duplicate packet:', sequence_number)
        else:
            print("Message corrupted,waiting for a retransmission")
        #time.sleep(1.2)
    my_string = "".join(msg)
    print(my_string)