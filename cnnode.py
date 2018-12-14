#!/usr/bin/python
#cnnode.py by Tianen Chen
#UNI: tc2841
#3/1/2017
from collections import defaultdict
import socket 
import time
import threading
import sys
import random

#For the most part, the cnnode program is very similar to my dvnode. Obviously, it is not fully functional.
#I mainly can get the receivers counting packets, the loss rate converges, and the Bellman-Ford Algorithm runs, but does not display properly.
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
	global sendArray
	global startProbeThread
	global MASTERPACKETCOUNT
	global dropValue
	global linkCount
	global totalDropped
	global totalReceived

	linkCount = {}

	startProbeThread = 0
	sentinalkill = 0
	myPort = int(sys.argv[1])
	distances = {}
	totalDropped ={}
	totalReceived = {}
	receivePosition = sys.argv[:].index('send')
#Split up the input string
	receiveArray = sys.argv[:][3:receivePosition]
	sendArray = sys.argv[:][receivePosition + 1:]
	myNeighbors = []
	localNeighbors = []
	initialDistanceVector = {}
	predecessors = {}

	for i in range(0, len(receiveArray) - 1, 2):
		if sys.argv[i] != 'last':
			portandWeightTuple = (myPort, int(receiveArray[i]), float(receiveArray[i + 1]))
			myNeighbors.append(portandWeightTuple)
			secondaryTuple = (int(receiveArray[i]), myPort, float(receiveArray[i + 1]))
			myNeighbors.append(secondaryTuple)
			localNeighbors.append(portandWeightTuple)
			localNeighbors.append(secondaryTuple)
			initialDistanceVector[int(receiveArray[i])] = (float("inf"), 'null', 0, 0)

	initialDistanceVector[myPort] = (0, 'null', 0, 0)
		
	myIP = str(socket.gethostbyname(socket.getfqdn()))
	socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket.bind((myIP,myPort))	


	if sys.argv[len(sys.argv) - 1] == 'last':
		sendOutMyNeighborList()




def sendOutMyNeighborList():
	for i in range(0, len(localNeighbors)):
		outPort = localNeighbors[i][1]
		outString = 'NEIGHBORLIST|' + str(myPort) + '|' + str(myNeighbors)
		socket.sendto(outString, (myIP, outPort))
		print '[' + str(time.time()) + ']' + ' Message sent from Node ' + str(myPort) + ' to Node ' + str(outPort)


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


def startAlgorithm(neighbors, fromPort):
	global initialDistanceVector
	global localNeighbors
	global predecessors
	global startProbeThread
	global distances
	global totalDropped
	global totalReceived
	sendSomething = 0
	distances = initialDistanceVector
	count = 0
	nextHop = {}
	for edges in neighbors:
		if edges[0] not in distances:
			distances[edges[0]] = (float('inf'), 'null', 0, 0)

		if edges[1] not in distances:
			distances[edges[1]] = (float('inf'), 'null', 0, 0)

	for edges in neighbors:
		if edges[0] not in totalDropped:
			totalDropped[edges[0]] = 0
			totalReceived[edges[0]] = 0 
		if edges[1] not in totalDropped:
			totalDropped[edges[1]] = 0
			totalReceived[edges[1]] = 0
	for i in distances:
		if i not in predecessors:
			predecessors[i] = None
	for i in range(1, len(distances)):
		for edges in neighbors:
		#	print distances
			if distances[edges[0]][0] + edges[2] < distances[edges[1]][0]:
				distances[edges[1]] = (float(distances[edges[0]][0]) + edges[2], edges[0], distances[edges[1]][2], distances[edges[1]][3])
				if edges[0] != myPort:
					predecessors[edges[1]] = str(predecessors[edges[0]]) + '+' + str(edges[0])
				sendSomething = 1
			if distances[edges[1]][0] + edges[2] < distances[edges[0]][0]:

				distances[edges[0]] = (float(distances[edges[1]][0]) + edges[2], edges[1], distances[edges[0]][2], distances[edges[0]][3])
				if edges[0] != myPort:
					predecessors[edges[0]] =  str(predecessors[edges[1]]) + '+' + str(edges[1])

				sendSomething = 1

	if sendSomething == 1:
		print '[' + str(time.time()) + '] Node ' + str(myPort) + ' Routing Table'		
		for ports in predecessors:
			if predecessors[ports] != None and distances[ports][1] != myPort:
				listOfHops = predecessors[ports].split('+')
				nextHop[ports] = listOfHops[1]
				if int(nextHop[ports]) == myPort and len(listOfHops) > 2 and distances[ports][1] != myPort:
					nextHop[ports] = listOfHops[2]
			else:
				nextHop[ports] = None
		# print nextHop
		for i in distances:
			#print 'i' + str(nextHop)
		 	if (nextHop[i] == None or int(nextHop[i]) == myPort) and i != myPort:
				print ' - (' + str(distances[i][0]) + ') -> Node ' + str(i)
		 	elif i != myPort:
		 		print ' - (' + str(distances[i][0]) + ') -> Node ' + str(i) + '; Next Hop -> Node ' + str(nextHop[i])
		sendOutMyNeighborList()
		if startProbeThread == 0:
			startProbing_thread.start()
			timer_thread.start()

			startProbeThread = 1

	initialDistanceVector = distances
#Probe function sends packets out continuously
def startProbing():
	global sendArray
	global distances
	if sendArray != ['last']:
		while 1:
			time.sleep(.09)
			for vertices in sendArray:
				probePacket = "PROBE|" + str(myPort) + '|blah'
 				socket.sendto(probePacket, (myIP, int(vertices)))

#Start counting
def timer():
 	global currentTime
 	global startTime 
 	global amSender
 	global distances
 	global probe
 	global totalDropped
 	global totalReceived
 	startTime = float(time.time())
 	startTime2 = float(time.time())
 	while 1:
 		currentTime = float(time.time())
 		if (currentTime - startTime) > 1 and sendArray != []:
 			startTime = float(time.time())
 			for keys in totalReceived:
 				if totalReceived[keys] != 0:
 					lossRate = totalDropped[keys]/(totalReceived[keys] * 1.0)
 					print '[' + str(time.time()) + ']' + 'Link to ' + str(keys) + ': ' + str(totalReceived[keys]) + ' sent, ' + str(totalDropped[keys]) + ' lost, loss rate ' + str(lossRate)


#Handle packets
def receiveAPacket(fromPort):
	global requestNumber
	global discardPackets
	global receivedPackets
	global packetGate
	global startTime
	global distances
	global totalDropped
	global totalReceived
	fromPort = int(fromPort)
	x = random.random()
	dropValue = distances[fromPort][0]
	if x < dropValue:
		dropIt = 1
	else:
		dropIt = 0
	if dropIt == 1: 
		totalDropped[fromPort] += 1
		totalReceived[fromPort] += 1
		#print 'drop'
	elif dropIt == 0: 
		totalReceived[fromPort] += 1
		#print 'receive'
		
	
	

#send an acknowledgement
def sendAck(ackNum):
	messageOut = ('ack', ackNum, ackNum + 1, 'probeAck')
	socket.sendto(str(messageOut), (myIP, peerPort))
	print str(float(time.time())) + ' ack' + str(ackNum) + ' sent, expecting packet ' + str(ackNum + 1)

#start up listening thread, always be listening
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

		if command == 'PROBE':
			receiveAPacket(fromPort)

#Start all my threads and exit cleanly with keyboard interrupt
if __name__ == '__main__':		
	main()

	listen_thread = threading.Thread(target=listen, args=())
	listen_thread.daemon = True
	listen_thread.start()

	startProbing_thread = threading.Thread(target = startProbing, args=())
	startProbing_thread.daemon= True



	timer_thread = threading.Thread(target=timer, args=())
	timer_thread.daemon = True


	while True:
		time.sleep(1)
		if sentinalkill == 1:
			break
