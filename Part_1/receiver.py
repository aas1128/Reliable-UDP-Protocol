import socket 
import time
import random
# Configuration Constants
receiverPort = 10000  # Port to receive packets on
PACKET_SIZE = 5 #Default packet size across the Protocol

#Binding the mediator socket to port 10000
socket_receiver= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receiver.bind(('127.0.0.1', receiverPort)) 
sender_address = ('127.0.0.1', 8000) #Address which the mediator would sent the packets to
received_packets = []
expected_seq_num = 0
buffer = {}  # Optional: to store out-of-order packets


def receiver():
    """
    Function that listens for packets and accounts for Dropped, reordered, and corrupted packets.
    """
    pass
#Im going to send Acks straight back to the sender rather than through the mediator
#reordering is the annoying part
    global expected_seq_num
    #Loop that runs and listens for packets sent from the sender
    while(True):
        packet, mediator_address = socket_receiver.recvfrom(PACKET_SIZE + 6)
        packet_str = packet.decode()
        print("this is the packet received from sender" , packet_str)
        data = 0
        seq_num = " "
        checksum = " "
        #Split packet into data, checksum and the seq_num
        try:
            data, seq_num, checksum = packet_str.split(':', 2)
            seq_num = int(seq_num)
            checksum = int(checksum)
        except:
            print(f"[ERROR] Malformed packet received for packet {seq_num}. Ignoring...")
            continue

        #These are checks for corrupted, out of order, and dropped packets
        if checksum != compute_checksum(data):
            print(f"[ERROR] Checksum mismatch for packet {seq_num}. Please Retransmit...")
            continue
        else:
            received_packets.append(packet_str)

        if seq_num == expected_seq_num:
            print(f"Delivered packet {seq_num} with data: '{data}'")
            expected_seq_num += 1

        # check the buffer for subsequent packets
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
            socket_receiver.sendto(ack, sender_address)
            print(f"Sent ACK for packet {seq_num}")  

        # Send cumulative ACK: the last in-order packet received is (expected_seq_num - 1)
        ack = str(expected_seq_num - 1).encode()
        socket_receiver.sendto(ack, sender_address)
        print(f"Sent ACK for packet {expected_seq_num - 1}")  


def compute_checksum(data):
    """
    Function recomputes the checksum for the data to 
    check for corrupted data.
    """
    sum = 0
    for char in data:
        sum += ord(char)
    #print("this is the checksum" , sum)
    return int(sum)

if __name__ == "__receiver__":
    receiver()