import socket
import threading
import time
import struct

#Configuration for the sender 
windowSize = 5 #Default window size because the packet size is 5 
timeBetweenPackets = 5 #Used for the sliding window
packetSize = 5 # Default packet size across the entire Protocol
base = 0 #Latest packet sent
next_seq = 0 #Next expected Seq number
sent_packets = {} #Tracks all already sent packets 
timer = None
lock = threading.Lock() 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind(('127.0.0.1', 8000)) #Create and bind to Port 8000
receiver_address = ('127.0.0.1', 9000) #Port and IP for the mediator in this case
num_packets = 0


def main():
    """
    Main function that reads in input from user and sends to the mediator
    """
    data = input("Please enter data to be sent: ")
    send_packet(data)
    

def send_packet(data):
    """
    Send Packets is a function that takes in data from the user
    splits it into packets and starts a thread which listens for Acks 
    before sending all the packets to the mediator

    Params:
        Data: A string read in from the user
    """
    global next_seq, timer, base, timer,num_packets
    #find the total amount of packets needed to send
    num_packets = (len(data) + packetSize - 1) // packetSize
    #Start a separate thread to listen for ACKs
    ack_listener = threading.Thread(target=listen_for_ack)
    ack_listener.daemon = True
    ack_listener.start()

    #Begin sending packets:
    while base < num_packets:
        #Check if we can continue sending new packets in window
        while next_seq < base + windowSize and next_seq < num_packets:
            #Split the data into chunks for packet
            start = next_seq * packetSize
            end = min(start + packetSize, len(data))
            packet_data = data[start:end]
            #create a new packet
            newPacket = createPacket(packet_data, next_seq)
            receiver_address = ('127.0.0.1', 9000)
            #Send to the mediator
            sock.sendto(newPacket.encode(), receiver_address)
            #Add the sent packet to the dictionary incase of resend
            sent_packets[next_seq] = newPacket

            # Move to the next sequence number
            next_seq += 1

            # Start timer if it's not running
            if not timer:
                #if the packet is started and we dont recieve an ack in 3 seconds we retransmit
                timer = threading.Timer(10, handle_timeout)
                timer.daemon = True
                timer.start()
    
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
    


def handle_timeout():
    """
    Function called when packets have been sent but Acks havent been
    received. Resends all packets in the current window.
    """
    global timer
    with lock:
        print("Timeout! Resending all packets in the window.")
        #Resends all packets in the window incase of timeout
        for seq_num in range(base, next_seq):
            if seq_num in sent_packets:
                sock.sendto(sent_packets[seq_num].encode(), receiver_address)
                print(f"Resent packet {seq_num}")
        # Restart the timer after retransmission
        timer = threading.Timer(10, handle_timeout)
        timer.daemon = True
        timer.start()

def listen_for_ack(): 
    """
    Function called from  send_packet which operates on its thread 
    and listens for Acks send from previously sent packets
    """
    global base, timer, num_packets
    while True:
        # Wait for ACK packet
        ack, address = sock.recvfrom(1024)
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

if __name__ == "__main__":
    main()