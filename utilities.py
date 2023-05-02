import socket
import random
import struct
import time
import os


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
      #print("Packet sent")
    else:
        print("Packet lost")


    #print('Sent packet:', Sequence_number)




def tcp_recv(window_size,UDPServerSocket):
    Reserved = 0
    protocol = socket.IPPROTO_TCP
    print("UDP server up and listening")
    # Listen for incoming datagrams
    serverSeqnumber = 0
    expected_seq_num = 1
    three_way_flag=0
    print("Waiting for connection.....")
    flag_get=0
    postflag = 0
    msg=[]
    sendmsg = []
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
        if three_way_flag==0:
            if flags == 20482:
                print("SYN received, Sending a SYN-ACK")
                serverFlags = 20498
                Tcp_send("",serverSeqnumber,sequence_number+1,serverFlags
                ,window,urgent_pointer,UDPServerSocket,src_addr,src_addr=UDPServerSocket.getsockname())
                data, src_addr = UDPServerSocket.recvfrom(window_size)
                size_of_payload=len(data)-20
                unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",data)
                flags = unpacked_data[4]
                if flags == 20496:
                    print("Connection established!")
                    three_way_flag=1
                    print({"---------------------------------------------------------------"})

        else:
            if sequence_number==0 and acknowledgment_number==0 and flags==20480:
                response = "HTTP/1.1 200 OK"
                Tcp_send(response,0,0,flags
                ,window,urgent_pointer,UDPServerSocket,src_addr,src_addr=UDPServerSocket.getsockname())


                httpHeader=payload
                httpHeader=httpHeader.decode("UTF-8")
                # Split the request into lines
                request_lines = httpHeader.split("\r\n")
                # Get the first line, which contains the command
                command_line = request_lines[0]
                # Split the command line into its parts
                command_parts = command_line.split(" ")
                # Get the HTTP method (GET or POST) from the command


                # Define the directory to search in
                current_directory = os.getcwd()
                dir_path = current_directory

                # Define the filename to search for
                filename = str(command_parts[1])[1:]
                postflag=1
            elif sequence_number==0 and acknowledgment_number==1 and flags==20480:
                httpHeader=payload
                httpHeader=httpHeader.decode("UTF-8")
                # Split the request into lines
                request_lines = httpHeader.split("\r\n")
                # Get the first line, which contains the command
                command_line = request_lines[0]
                # Split the command line into its parts
                command_parts = command_line.split(" ")
                # Get the HTTP method (GET or POST) from the command


                # Define the directory to search in
                current_directory = os.getcwd()
                dir_path = current_directory

                # Define the filename to search for
                filename = str(command_parts[1])[1:]

                # Iterate over the files in the directory
                for root, dirs, files in os.walk(dir_path):
                    if filename in files:
                        # Found the file
                        print(f'File {filename} found in {root}')
                        response = "HTTP/1.1 200 OK"
                        flag_get=1
                        break
                else:
                    # File not found
                    print(f'File {filename} not found in {dir_path}')
                    response = "HTTP/1.1 404 Not Found"

                Tcp_send(response,0,0,flags
                ,window,urgent_pointer,UDPServerSocket,
                src_addr,src_addr=UDPServerSocket.getsockname())

                if flag_get==1:
                    with open(filename, 'r') as f:
                        lines = f.readlines()
                        sendmsg = lines

            if postflag==1:
                if flags == 20481:
                    serverFlags=29496
                    Tcp_send("",serverSeqnumber,sequence_number+1,serverFlags
                    ,window,urgent_pointer,UDPServerSocket,src_addr,src_addr=UDPServerSocket.getsockname())
                    break
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
                    if int(sequence_number) == int(expected_seq_num):

                        #save packets into textfile
                        msg.append(payload.decode("UTF-8"))

                        ack = sequence_number+size_of_payload
                        ack = str(ack)
                        clientAddressPort=src_addr
                        UDPServerSocket.sendto(ack.encode(), clientAddressPort)
                        print('Received packet:', payload)
                        expected_seq_num = ack
                    else:
                        print('Received duplicate packet:', sequence_number)
                else:
                    print("Message corrupted,waiting for a retransmission")
                time.sleep(1.2)
                if random.random() < 0.3:
                    time.sleep(1.2)
            else:
                Sequence_number=1
                datapointer = 0
                while datapointer < len(sendmsg):
                    data_t=sendmsg[datapointer]
                    Acknowledgment_number=1

                    Flags=20480 #"0101000000000000"
                    Window=1024
                    Urgent_pointer=0

                    Tcp_send(data_t,Sequence_number,Acknowledgment_number,Flags
                                ,Window,Urgent_pointer,UDPServerSocket,src_addr,src_addr=UDPServerSocket.getsockname()) 

                    print('Sent packet:', Sequence_number)
                    UDPServerSocket.settimeout(1.0)
                    try:
                        ack,addr = UDPServerSocket.recvfrom(Window)
                        ack_num = int(ack.decode())
                        print("Received ACK: ",str(ack_num))
                        if ack_num == Sequence_number+len(sendmsg[datapointer]):
                            datapointer += 1
                            Sequence_number = ack_num
                    except socket.timeout:
                        print('Timeout occurred, retransmitting packet:', Sequence_number)
                UDPServerSocket.settimeout(None)
                flags = 20481
                Sequence_number=0
                data_t=""
                Acknowledgment_number=0
                Window=1024
                Urgent_pointer=0
                Tcp_send(data_t,Sequence_number,Acknowledgment_number,flags
                            ,Window,Urgent_pointer,UDPServerSocket,src_addr,src_addr=UDPServerSocket.getsockname())
                fin,addr = UDPServerSocket.recvfrom(Window)
                size_of_payload=len(fin)-20
                unpacked_data=struct.unpack(f"2H 2I 4H {size_of_payload}s",fin)
                flags = unpacked_data[4]
                if flags == 29496:
                    UDPServerSocket.close()
                    break


    if flag_get==0:            
        with open(filename, 'w') as f:
            f.writelines("%s\n" % item for item in msg)     
        