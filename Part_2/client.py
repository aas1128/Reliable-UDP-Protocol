import os 
import socket
import sys
import threading
import time 

base = 0
next_seq = 0
sent_packets = {}
timer = None
num_packets = 0
lock = threading.Lock() 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('127.0.0.1', 6969))
server_address = ('127.0.0.1', 7979)

def main():
    """
    Main function that reads in a filePath and 
    creates packets which are sent to the server
    """
    filepath = input("Enter the path to the file: ")
    if not os.path.isfile(filepath):
        print("Error: The file path is invalid or the file does not exist.")
    else:
        #/Users/aayansayed/Documents/CSCI - 351/Sayed_Aayan_hw03/testFile.txt
        packets = split_into_packets(filepath, 5)
        send_packets(packets)
        

def split_into_packets(filepath, packet_size):
    """
    Helper function with takes in the contents of a file 
    and splits it into an array of length 5
    """
    #Opens file and reads contents
    with open(filepath, 'r') as f:
        content = f.read()
    packet_data = []
    
    pos = 0
    #Reads in 5 chars at a time and creates packets
    while pos < len(content):
        packet_data.append(content[pos:pos+packet_size])
        pos += packet_size
    print(packet_data)
    return packet_data
    
def send_packets(all_packets):
    """
    Function that takes in a list of packets and sends it to 
    the server with a generated checksum and expected seq num
    """
    #Start a separate thread to listen for ACKs
    ack_listener = threading.Thread(target=listen_for_ack)
    ack_listener.daemon = True
    ack_listener.start()

    global next_seq, timer, base, timer,num_packets
    num_packets = len(all_packets)
    for packet in all_packets:
        new_packet = createPacket(packet, next_seq)
        client_socket.sendto(new_packet.encode(), server_address)
        sent_packets[next_seq] = new_packet
        next_seq += 1
        # Start timer if it's not running
        if not timer:
            #if the packet is started and we dont recieve an ack in 3 seconds we retransmit
            timer = threading.Timer(10, handle_timeout)
            timer.daemon = True
            timer.start()
         # Wait until all packets are acknowledged
    # Wait until all packets are acknowledged
    
    client_socket.sendto("EOF".encode(), server_address)
    while base < num_packets:
        time.sleep(0.1)
    print("All packets acknowledged; exiting send_packets.")



           
def createPacket(data, seqNum):
    """
    Function called from the send_packet which takes in
    already split data and assigns it a sequence number
    and checksum to create a packet to send.
    Params:
        Data: Split data for 1 packet
    """
    checkSum = generateCheckSum(data)
    packet = data + ":" + str(seqNum) + ":" + str(checkSum)
    return (packet)


def generateCheckSum(data):
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

        
def listen_for_ack(): 
    """
    Function called from  send_packet which operates on its thread 
    and listens for Acks send from previously sent packets
    """
    global base, timer, num_packets
    while True:
        # Wait for ACK packet
        ack, address = client_socket.recvfrom(1024)
        try:
            ack_num = int(ack.decode())
        except Exception as e:
            print(f"Invalid ACK received: {ack}. Error: {e}")
            continue

        # If the received ack number is not valid (i.e. equal to or greater than the total packets),
        # ignore it.
        if ack_num >= num_packets:
            print(f"Ignoring invalid ACK {ack_num} (only {num_packets} packets sent).")
            continue

        with lock:
            # Slide the window forward if the ACK is for the base packet or later
            if ack_num >= base:
                print(f"Received ACK for packet {ack_num}")

                # Remove acknowledged packets from our sent_packets store
                for i in range(base, ack_num + 1):
                    if i in sent_packets:
                        del sent_packets[i]
                # Move the base forward
                base = ack_num + 1

                # Stop the timer if all packets are acknowledged
                if base == next_seq:
                    if timer:
                        timer.cancel()
                    timer = None
                else:
                    # Restart the timer for the remaining packets
                    if timer:
                        timer.cancel()
                    timer = threading.Timer(5, handle_timeout)
                    timer.daemon = True
                    timer.start()


def handle_timeout():
    """
    Function called when packets have been sent but Acks havent been
    received. Resends all packets in the current window.
    """
    global timer
    with lock:
        print("Timeout! Resending all packets in the window.")
        for seq_num in range(base, next_seq):
            print(seq_num)
            if seq_num in sent_packets:
                print("here in timeout")
                client_socket.sendto(sent_packets[seq_num].encode(), server_address)
                print(f"Resent packet {seq_num}")
        client_socket.sendto("EOF".encode(), server_address)
        # Restart the timer after retransmission
        timer = threading.Timer(10, handle_timeout)
        timer.daemon = True
        timer.start()
if __name__ == "__main__":
    main()