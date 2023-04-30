import socket
import random
import struct
import time


def ip2int(ip_addr):
    if ip_addr == 'localhost':
        ip_addr = '127.0.0.1'
    return [int(x) for x in ip_addr.split('.')]




def checksum_func(data):
    checksum = 0
    data_len = len(data)
    if (data_len % 2):
        data_len += 1
        data += struct.pack('!B', 0)
    
    for i in range(0, data_len, 2):
        w = (data[i] << 8) + (data[i + 1])
        checksum += w

    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF
    return checksum


def verify_checksum(data, checksum):
    data_len = len(data)
    if (data_len % 2) == 1:
        data_len += 1
        data += struct.pack('!B', 0)
    
    for i in range(0, data_len, 2):
        w = (data[i] << 8) + (data[i + 1])
        checksum += w
        checksum = (checksum >> 16) + (checksum & 0xFFFF)

    return checksum


def Tcp_send(data,Sequence_number,Acknowledgment_number,Flags,Window,Urgent_pointer,UDPClientSocket,dest_addr,src_addr=('127.0.0.1', 14)):
    #Generate TCP pseudo header
    src_ip, dest_ip = ip2int(src_addr[0]), ip2int(dest_addr[0])
    src_ip = struct.pack('!4B', *src_ip)
    dest_ip = struct.pack('!4B', *dest_ip)

    Reserved = 0

    protocol = socket.IPPROTO_TCP  #is 6 for TCP

    #Check the type of data
    try:
        data = data.encode()
    except AttributeError:
        pass

    src_port = src_addr[1]
    dest_port = dest_addr[1]

    data_len = len(data)
    
    tcp_length = 20 + data_len   #tcp header length is 20

    checksum = 0
    pseudo_header = struct.pack('!BBH', Reserved, protocol, tcp_length)

    pseudo_header = src_ip + dest_ip + pseudo_header
 

    TCP_header=struct.pack(f"2H 2I 4H",src_port,dest_port
                ,Sequence_number,Acknowledgment_number,
                Flags,Window,checksum,Urgent_pointer)


    #cpy=pseudo_header + TCP_header + data

    checksum = checksum_func(pseudo_header + TCP_header + data)

    #test=verify_checksum(cpy,checksum)

    #print(hex(test))

    TCP_header=struct.pack("2H 2I 4H",src_port,dest_port
                ,Sequence_number,Acknowledgment_number,
                Flags,Window,checksum,Urgent_pointer)
    

    if random.random() > 0:
      UDPClientSocket.sendto(TCP_header+data, dest_addr)
      print("Packet sent")
    else:
        print("Packet lost")


    print('Sent packet:', Sequence_number)


    

def tcp_recv(window_size,UDPServerSocket):
    Reserved = 0
    protocol = socket.IPPROTO_TCP

    print("UDP server up and listening")
    # Listen for incoming datagrams

    expected_seq_num = 0

    while True:
        data, src_addr = UDPServerSocket.recvfrom(window_size)

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



        src_ip=ip2int(src_addr[0])
        dest_ip=ip2int(UDPServerSocket.getsockname()[0])
        
        src_ip = struct.pack('!4B', *src_ip)
        dest_ip = struct.pack('!4B', *dest_ip)


        pseudo_header = struct.pack('!BBH', Reserved, protocol, len(data))
        pseudo_header = src_ip + dest_ip + pseudo_header

        TCP_header=struct.pack(f"2H 2I 4H",source_port,destination_port
                ,sequence_number,acknowledgment_number,
                flags,window,0,urgent_pointer)
        
        verify = verify_checksum(pseudo_header + TCP_header + payload, check_sum)
        if verify == 0xFFFF:
            if sequence_number == expected_seq_num:
                ack = str(sequence_number)
                clientAddressPort=src_addr
                UDPServerSocket.sendto(ack.encode(), clientAddressPort)
                print('Received packet:', payload)
                expected_seq_num += 1
            else:
                print('Received duplicate packet:', sequence_number)
        else:
            print("Message corrupted,waiting for a retransmission")
        time.sleep(1.2)
