import socket  # For creating UDP sockets
import time
import random
# Configuration Constants
server_port = 7979    # Port to receive packets on
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', server_port))
client_address = ('127.0.0.1', 6969)
received_packets = []
expected_seq_num = 0
buffer = {}
PACKET_SIZE = 5

def server():
     """
    The server listens for incoming packets from the client and has code 
    which account for corrupted, out-of-order, and reordered
    """
     global expected_seq_num, buffer,received_packets
     while(True):
        packet, client_address = server_socket.recvfrom(PACKET_SIZE + 6)
        packet_str = packet.decode()
        if packet_str == "EOF":
            print("EOF")
            write_file(received_packets)
            expected_seq_num = 0
            buffer = {}
            received_packets = []
            continue
        #print("this is the packet" , packet_str)
        data = 0
        seq_num = " "
        checksum = " "

        # if packet_str.strip() == "EOF":
        #     print("EOF received. Resetting server state.")
        #     # Process any remaining buffered data if necessary.
        #     # For example, write buffered data to the file.
        #     expected_seq_num = 0
        #     buffer = {}
        #     received_packets = []  # Clear previous file data.
        #     # Optionally, close the file and open a new one for the next transfer.
        #     continue
        try:
            data, seq_num, checksum = packet_str.split(':', 2)
            seq_num = int(seq_num)
            checksum = int(checksum)
        except:
            print(f"[ERROR] Malformed packet received for packet {seq_num}. Ignoring...")
            
            continue

        if checksum != compute_checksum(data):
            print(f"[ERROR] Checksum mismatch for packet {seq_num}. Please Retransmit...")
            continue
        else:
            received_packets.append(data)

        if seq_num == expected_seq_num:
            # Deliver the packet (for example, print it)
            print(f"Delivered packet {seq_num} with data: '{data}'")
            expected_seq_num += 1

        # Optionally, check the buffer for subsequent packets
            while expected_seq_num in buffer:
                buffered_data = buffer.pop(expected_seq_num)
                print(f"Delivered buffered packet {expected_seq_num} with data: '{buffered_data}'")
                expected_seq_num += 1

        elif seq_num > expected_seq_num:
            # Out-of-order packet: buffer it for later
            print(f"Packet {seq_num} out-of-order. Expected {expected_seq_num}. Buffering it.")
            buffer[seq_num] = data
        else:
            # Duplicate packet: already delivered.
            ack = str(seq_num).encode()
            server_socket.sendto(ack, client_address)
            print(f"Sent ACK for packet {seq_num}")  

        # Send cumulative ACK: the last in-order packet received is (expected_seq_num - 1)
        ack = str(expected_seq_num - 1).encode()
        server_socket.sendto(ack, client_address)
        print(f"Sent ACK for packet {expected_seq_num - 1}")  


def compute_checksum(data):
    """
    Function called from the createPacket function which takes in
    already split data and generates a checksum for it.
    Params:
        Data: Split data for 1 packet
    """
    sum = 0
    for char in data:
        sum += ord(char)
    #print("this is the checksum" , sum)
    return int(sum)

def write_file(received_packets):
    """
    Fuction with takes all the packets and writes them to a 
    file in the parent directory
    """
    print("Writing to createdFile.txt")
    with open("createdFile.txt", "a") as file:
        for packets in received_packets:
            file.write(packets)
server()