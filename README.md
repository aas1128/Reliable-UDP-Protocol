Aayan Sayed 
CSCI 351
HW 03

Project: Reliable UDP Protocol
Description: 
The IP protocol enables addressing, packet routing, and forwarding in the network as a best-effort service, which does not guarantee packet delivery. This project uses datagrams in UDP to send and receive data through a reliable data transfer protocol. 

1) How to compile and run the code:
    1) Clone the github repository to access the python code and the dependencies (can make a virtual environment using python)
    2) Check if python is downloaded on the system
    3) install the requirements needed to run the code 

    4) For Part 1:
        The order in which the sender, mediator, and receiver are run doesn't matter however if the sender is started first
        it will timeout after 10 seconds and resent packets as it hasn't received Acks for them.

        Sender:   When ran the sender prompts the user to enter data which will be created into packets and sent to the mediator. It also 
                  listens for Acks once packets are sent and only retransmits packets in case of bad network conditions. 
                

        Mediator: When ran the mediator it listens for packets on port 9000 and receives them from the sender. The mediator is responsible 
                  for simulating the network conditions in this case: corrupted packets, re-ordered packets, and dropped packets.

        Receiver: When ran the receiver it listens for packets on port 10000 and receives them from the mediator. The receiver has logic which
                  recomputes/verifies the checksum and handles retransmission if packets are dropped or corrupted. It can also reorder
                  packets based on their sequence number.
    
    5) For Part 2:
        The order in which the client or server is ran doesn't matter however if the client is started first after 10 seconds
        the packets would time out and be retransmitted.

        Client: When ran it prompts the user for the filepath to the text it wants to read. It then reads the file, splits it into 
                packets, and sends it to the client. It also starts a thread which listens to Acks for the sent packets.

        Server: When ran it listens for packets from the client. The server has logic which account for the packets being corrupted
        reordered, and dropped. If the packets are verified they are reordered and written to a file called "createdFile". 
