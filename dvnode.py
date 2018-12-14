#!/usr/bin/python
#dvnode.py by Tianen Chen
#UNI: tc2841
#4/22/2017
from collections import defaultdict
import socket 
import time
import threading
import sys

#Main function starts up the program, declares all global variables, and takes the user input.
def main():
	global clientPort
	global myIP
	global socket
	global sentinalkill
	global myPort
	global myNeighbors
	global edgeCount
	global lastNode
	global localNeighbors
	global initialDistanceVector
	global predecessors

	sentinalkill = 0
	myPort = int(sys.argv[1])
	myNeighbors = []
	localNeighbors = []
	initialDistanceVector = {}
	predecessors = {}
	#Append a tuple of all the edges to myNeighbors
	#Create an initial distance vector
	for i in range(2, len(sys.argv) - 1, 2):

		if sys.argv[i] != 'last':
			portandWeightTuple = (myPort, int(sys.argv[i]), float(sys.argv[i + 1]))
			myNeighbors.append(portandWeightTuple)
			localNeighbors.append(portandWeightTuple)
			initialDistanceVector[int(sys.argv[i])] = (float("inf"), 'null')

	initialDistanceVector[myPort] = (0, 'null')
		
	myIP = str(socket.gethostbyname(socket.getfqdn()))
	socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket.bind((myIP,myPort))	

#If the last argument is last, start everything up by sending out a neighbor list
	if sys.argv[len(sys.argv) - 1] == 'last':
		sendOutMyNeighborList()


#Send out a list of my neighbors to all closest neighbors
def sendOutMyNeighborList():
	for i in range(0, len(localNeighbors)):
		outPort = localNeighbors[i][1]
		outString = 'NEIGHBORLIST|' + str(myPort) + '|' + str(myNeighbors)
		socket.sendto(outString, (myIP, outPort))
		print '[' + str(time.time()) + '] Message sent from Node ' + str(myPort) + ' to Node ' + str(outPort)

#Append to my received neighbor array and start up the Bellman-Ford algorithm
def appendToMasterListTellNeighbors(arrayString, fromPort):
	global myNeighbors
	global edges
	receivedNeighborArray = eval(arrayString)
	number = 0
	for i in receivedNeighborArray: 
		if i not in myNeighbors:
			myNeighbors.append(i)
	print '[' + str(time.time()) + '] Message received at Node ' + str(myPort) + ' from Node ' + str(fromPort)
	startAlgorithm(sorted(myNeighbors), fromPort)


#Start up the Bellman Ford algorithm
def startAlgorithm(neighbors, fromPort):
	global initialDistanceVector
	global localNeighbors
	global predecessors
	sendSomething = 0
	distances = initialDistanceVector
	count = 0
	nextHop = {}
#Make sure that all the nodes are placed into my dictionary with initial distance of infinity and predecessor of null
	for edges in neighbors:
		if edges[0] not in distances:
			distances[edges[0]] = (float('inf'), 'null')
		if edges[1] not in distances:
			distances[edges[1]] = (float('inf'), 'null')

#If the node predecessor is not in the predecessor dictionary yet, make it so that it has a 'None' predecessor
	for i in distances:
		if i not in predecessors:
			predecessors[i] = None
#Iterate over the entire distances dictionary
#Run the algorithm
	for i in range(1, len(distances)):
		for edges in neighbors:
			if distances[edges[0]][0] + edges[2] < distances[edges[1]][0]:
				distances[edges[1]] = (float(distances[edges[0]][0]) + edges[2], edges[0])
				if edges[0] != myPort:
					predecessors[edges[1]] = str(predecessors[edges[0]]) + '+' + str(edges[0])
				sendSomething = 1
 
			if distances[edges[1]][0] + edges[2] < distances[edges[0]][0]:

				distances[edges[0]] = (float(distances[edges[1]][0]) + edges[2], edges[1])
				if edges[0] != myPort:
					predecessors[edges[0]] =  str(predecessors[edges[1]]) + '+' + str(edges[1])

				sendSomething = 1
#Send something tells me that my routing table has changed, so I should reprint my routing table.
	if sendSomething == 1:
		print '[' + str(time.time()) + ']' + ' Node ' + str(myPort) + ' Routing Table'		
#Print everything out in a nicely formatted manner
		for ports in predecessors:
			if predecessors[ports] != None and distances[ports][1] != myPort:
				listOfHops = predecessors[ports].split('+')
				nextHop[ports] = listOfHops[1]
				if int(nextHop[ports]) == myPort and len(listOfHops) > 2 and distances[ports][1] != myPort:
					nextHop[ports] = listOfHops[2]
			else:
				nextHop[ports] = None
		for i in distances:
		 	if (nextHop[i] == None or int(nextHop[i]) == myPort) and i != myPort:
				print ' - (' + str(distances[i][0]) + ') -> Node ' + str(i)
		 	elif i != myPort:
		 		print ' - (' + str(distances[i][0]) + ') -> Node ' + str(i) + '; Next Hop -> Node ' + str(nextHop[i])
		sendOutMyNeighborList()
		
	initialDistanceVector = distances



#Always be listening using the listening thread
def listen():
	global sendTrue
	global stop
	global lastNode
	while 1:
		message = socket.recv(1024)
		splitMessage = message.split('|')
		command = splitMessage[0]
		fromPort = splitMessage[1]
		toAppend = splitMessage[2]
	

		if command == 'NEIGHBORLIST':

			appendToMasterListTellNeighbors(toAppend, fromPort)


#Kill the program using keyboard interrupt
if __name__ == '__main__':		
	main()

	listen_thread = threading.Thread(target=listen, args=())
	listen_thread.daemon = True
	listen_thread.start()

	while True:
		time.sleep(1)
		if sentinalkill == 1:
			break
