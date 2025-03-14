import socket  # For creating UDP sockets
import time
import random
# Configuration Constants
mediatorPort = 9000    # Port to receive packets on
PACKET_SIZE = 5

#Binding the mediator socket to port 9000
socket_mediator= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_mediator.bind(('127.0.0.1', mediatorPort))

expected_seq_num = 0  # Next expected sequence number
receiver_address = ('127.0.0.1', 10000) #Port for the receiver

LOSS_PROB = 0.5   # 20% chance to drop a packet
CORRUPT_PROB = 0.2  # 20% chance to corrupt a packet
REORDER_PROB = 0.2

reorder_buffer = []  # Global buffer for packets to be reordered
def simulateNetwork():
    """
    Function that listens for packets from the sender and 
    simulates the network conditions.
    """
    global expected_seq_num
    while True:
        # if reorder_buffer and random.random() < 0.5:
        #     buffered_packet = reorder_buffer.pop(0)
        #     socket_mediator.sendto(buffered_packet.encode(), receiver_address)
        #     print("[Mediator] Forwarded buffered packet to receiver.")

        # Wait for a packet
        packet, sender_address = socket_mediator.recvfrom(PACKET_SIZE + 6)
        packet_str = packet.decode()
        print("this is the packet" , packet_str)
        data = 0
        seq_num = " "
        checksum = " "

        try:
            data, seq_num, checksum = packet_str.split(':', 2)
            seq_num = int(seq_num)
            checksum = int(checksum)
        except:
            print("[ERROR] Malformed packet received. Ignoring...")
            continue

        #This packet might be dropped before being sent to receiver 
        if random.random() < LOSS_PROB:
            print("[Mediator] Packet dropped (simulated loss).")
            continue 

        # #This packet might get a byte corrupted 
        # if random.random() < CORRUPT_PROB:
        #     print("[Mediator] Packet corrupted (simulated corruption).")
        #     #replace a random character with 'X'
        #     if len(packet_str) > 0:
        #         idx = random.randint(0, len(packet_str) - 1)
        #         packet_str = packet_str[:idx] + "X" + packet_str[idx+1:]
        

        # if random.random() < REORDER_PROB:
        #     print("[Mediator] Packet buffered for reordering (simulated reordering).")
        #     reorder_buffer.append(packet_str)  # Buffer the packet as-is
        #     continue  # Do not forward immediately

        socket_mediator.sendto(packet_str.encode(), receiver_address)
        print("[Mediator] Forwarded packet to receiver.")

        # Small delay to simulate network latency
       
        

if __name__ == "__simulateNetwork__":

    simulateNetwork()