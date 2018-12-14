PA2 By Tianen Chen
CSEE 4119 
04/22/2017

All code written for Python 2.7.6
----------------------
gbnnode.py
----------------------
OVERVIEW:
For gbnnode.py, I implement the go-back-n procedure. According to the go-back-n procedure, we have need to have two key features: a sender and receiver. The sender sends packets split up by every character and waits for a receiver before advancing a limited window size. The receiver waits on the packet and if the packet number matches the correct sequence number or is greater than the correct sequence number, an ack is replied for the packet received. The key to go-back-n is the timeout procedure. Upon packet dropping, if the sender does not receive an ack for the packet sent in 500ms, the packet 'times out' and the entire window is re-sent. If a packet reaches receiver side that is lower than the packet number, the ack back is for the current packet number. Finally, the window advances upon successive acks. The window moves and the last packet in the window is sent upon the window moving.
----------------------
MY PROGRAM FEATURES:
My GBN program features a multi-threaded approach. There are two primary threads, a listening thread and a timer thread. The listening thread is meant to 'always be listening.' The timer thread has a global current time, timing out whenever an ACK is not received in 500ms. The data structure that I use are tuples. I send tuples in the following manner: (MESSAGETYPE, SEQUENCENUMBER, DATA, PROBE). MESSAGETYPE tells me the incoming message either as an ack or a message. The SEQUENCENUMBER tells me what number packet that is sent out. The DATA is the character itself. The PROBE was implemented in anticipation of part 4. However, I was not able to utilize GBN effectively in part 4. Thus, it is attached for posterity's sake.

The buffer is an array of all the tuples. Thus, the buffer matches whatever length the string input is.

Additionally, the multithreading of the program provides for some problems. For example, the quick sending time can cause the first four packets to be sent and the ack may not come back until all 4 packets are sent. Alternatively, the ack may be received intermittently between the four packets. This was solved by giving all my packets a faux round trip time of .02 seconds using time.sleep() function.

Algorithmically, I just send and receive packets and use different methods for parsing the strings received over the socket.
----------------------
FLAWS IN MY PROGRAM:
First and foremost, the most important flaw is that for some reason, my program will sometimes not continue working if the sender and receiver exchange multiple messages alternating who is the sender and who is the receiver. This has something to do with the fact that the dropped acks and dropped packets are layering on top of each other, sometimes bumping into each other and causing bugs in my program. The reason I know this is that the program works fine if I do not drop acks or do not drop packets indivdually. However, the first time the sender sends to the receiver should work every time. 

Also, another flaw in my program is that the deterministic drop does not work if the drop value is smaller than window. For example, I cannot drop every third packet for a window size of 5. However, I can drop for every 5 packets with a window size of 3. I do not understand what the cause of this is, but I am guessing it has to do with the modulo arithmetic and the total packet and ack count I use to calculate which packets get dropped. The program will get stuck in an infinite loop.

My program is not user friendly. I assume a smart user who knows how to input the proper inputs.

Lastly, there are many edge cases that I have potentially not caught.

----------------------
HOW TO RUN MY PROGRAM:
Both sides, receiver and sender will input this into the terminal line where the program is located. 

python gbnnode.py <self-port> <peer-port> <window-size> [ -d <value-of-n> | j -p <value-of-p>]

Where depending on if its sender or receiver side, the value-of-n (an int larger than window size) or value-of-p (a float from 0 to 1) determines if we drop the ack or packet, respectively.

Upon starting, the user picks who is the sender by typing:

node> send <some-string-of-characters>

When hitting enter, the program should run automatically.

----------------------
dvnode.py
----------------------
OVERVIEW:
This program uses the Bellman-Ford algorithm in order to calculate the shortest distances from nodes given weights from node to node. The trickiest part of the program was getting all the nodes to send information to each other when each node only starts out knowing information about its closest neighbors only. However, following the procedure outlined in the assignment. Each node sends back and forth only when the distance vector is updated for each node.

The basic structure/pseudocode I followed is below when executing the main algorithm:

 function BellmanFord(list vertices, list edges, vertex source)
   ::distance[],predecessor[]

   for each vertex v in vertices:
       distance[v] := inf            
       predecessor[v] := null         
   
   distance[source] := 0              
      for i from 1 to size(vertices)-1:
       for each edge (u, v) with weight w in edges:
           if distance[u] + w < distance[v]:
               distance[v] := distance[u] + w
               predecessor[v] := u

----------------------
MY PROGRAM FEATURES:
We use a multithreaded program that always listens to the incoming list of neighbors that is always sent out when the distance vector is updated. Otherwise, the format of dvnode is relatively simple. The primary data strcture used is the dictionary. Within dvnode, there are two major dictionaries: one is the "distances" dictionary, whose keys are the ports of the destination nodes that exist within the topography. The values of the distances dictionary are the weights to the destination and the final hop predecessor. The predecessors dictionary contains a string of hops for every destination node. From there, I can determine the next hop by splitting the string.

----------------------
FLAWS IN MY PROGRAM:
My program is not user friendly. Furthermore, I have not tested it extensively. In my opinion, the most probable thing to fail would be finding the next hop in a complicated topography.
Additionally, due to the nature of the Bellman-Ford, the algorithm may never converge.
Lastly, once again, I may not have caught all the edge cases.
----------------------
HOW TO RUN MY PROGRAM:

The following command is input into the terminal running the program. Depending on how many immediate neighbors a node has, the argument string will be greater or less than the one provided. The key to running my program is the input of the last command. Upon reception of last as the last terminal being opened, the algorithm kickstarts. Do not start the last node's program until all other nodes have been implemented.

python cnnode.py <local-port> receive <neighbor1-port> <loss-rate-1> <neighbor2-port> <loss-rate-2> ... <neighborM-port>
<loss-rate-M> send <neighbor(M+1)-port> <neighbor(M+2)-port> ... <neighborN-port> [last]

----------------------
cnnode.py
----------------------
OVERVIEW:
For cnnode, my program is not functional. However, I have implemented some features that I hope will be able to snag me some mercy points. You will notice 2 copies of my program submitted in the zip file. The first program, cnnode.py, simply probes packets continuously and counts the packets at the designated receiver, printing link costs every second. The second program, cnnode2.py is like the first one, except the Bellman-Ford gets updated every 5 seconds
------------------------
MY PROGRAM FEATURES:
We use a multithreaded approach with a whopping total of 3 different threads. The first thread always listens, the second thread is the timer, the third thread is the probe packet sender.
Essentially, we use the same process as dvnode. We send packets repeatedly and handle packets at each end. Senders and receivers are specified with drop probabilities at each end. We use dictionaries as our primary data structure, same as dvnode above.
However, we add another new dictionary call dropDict that updates drop values and weights of the links every time the Bellman Ford algorithm runs in cnnode2.py


----------------------
FLAWS IN MY PROGRAM:
My program is heavily flawed. First of all, I do not incorporate GBN succesfully. Secondly, my routing algorithms don't print out the new routing tables every 5 seconds for some reason. 

Essentially, these 2 programs are meant to be implemented in order to get me some mercy points in 2 categories: the counter catergory and the loss-rate category.

----------------------
HOW TO RUN MY PROGRAM:
The program is run using the command specified in the assignment handout. 

python cnnode.py <local-port> receive <neighbor1-port> <loss-rate-1> <neighbor2-port> <loss-rate-2> ... <neighborM-port>
<loss-rate-M> send <neighbor(M+1)-port> <neighbor(M+2)-port> ... <neighborN-port> [last]

The above command is input at every node terminal.

The second program is run the same way as cnnode.py, however instead, we just type in cnnode2.py. 

The program was tested using the example scenario given in the handout.