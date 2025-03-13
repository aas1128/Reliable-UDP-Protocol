
import socket
import threading
import time
import struct

windowSize = 5
timeBetweenPackets = 5
packetSize = 5

base = 0
next_seq = 0
sent_packets = {}
timer = None
lock = threading.Lock() 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 8000))
receiver_address = ('127.0.0.1', 9000)
num_packets = 0

def main():
    
    data = input("Please enter data to be sent: ")
    send_packet(data)
    

def send_packet(data):
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

            #Send to the intermediary
            sock.sendto(newPacket.encode(), receiver_address)
            #base is supposed to be updated in the listen_for_ack thread
            sent_packets[next_seq] = newPacket

            # Move to the next sequence number
            next_seq += 1

            # Start timer if it's not running
            if not timer:
                #if the packet is started and we dont recieve an ack in 3 seconds we retransmit
                timer = threading.Timer(10, handle_timeout)
                timer.daemon = True
                timer.start()

            # Wait briefly to control sending rate


    
def createPacket(data, seqNum):
    checkSum = generateCheckSum(data)
    packet = data + ":" + str(seqNum) + ":" + str(checkSum)
    
    return (packet)


def generateCheckSum(data):
    sum = 0
    for char in data:
        sum += ord(char)
    #print("this is the checksum" , sum)
    return int(sum)
    


def handle_timeout():
    global timer
    with lock:
        print("Timeout! Resending all packets in the window.")
        for seq_num in range(base, next_seq):
            if seq_num in sent_packets:
                sock.sendto(sent_packets[seq_num].encode(), receiver_address)
                print(f"Resent packet {seq_num}")
        # Restart the timer after retransmission
        timer = threading.Timer(10, handle_timeout)
        timer.daemon = True
        timer.start()

def listen_for_ack(): 
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