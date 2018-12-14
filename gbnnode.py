#!/usr/bin/python
#gbnode.py by Tianen Chen
#UNI: tc2841
#4/22/2017

#Set global variables and get the sys.argv arguments

import socket 
import time
import threading
import sys
import time
import random
import signal
global socket
global selfPort
global peerPort
global windowSize
global dropType


selfPort = int(sys.argv[1])
peerPort = int(sys.argv[2])
windowSize = int(sys.argv[3])
dropType = str(sys.argv[4])
myIP = '127.0.0.1'
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((myIP,selfPort))



#Main function sets up global variables, calls procedures and sets up the gates and packet counters
def main():
#A lot of global variables to be used across all methods
	global sentinalkill
	global selfPort
	global peerPort
	global windowSize
	global dropType
	global dropValue
	global socket
	global realMessage
	global lastOneWasDropped
	global windowBegin
	global droppedAcks
	global myIP
	global masterList
	global requestNumber 
	global receivedPackets
	global startTime
	global currentTime
	global droppedAcks
	global receivedAcks
	global discardPackets
	global receivedPackets
	global firstFlushNum
	global currentPacket
	global MASTERPACKETCOUNT
	global MASTERACKCOUNT
	global packetGate
	global ackGate
	global timer_thread
	global listen_thread
	global amSender


	requestNumber = 0
	packetGate = 0
	ackGate = 0
	currentPacket = 0
	MASTERPACKETCOUNT = 0
	MASTERACKCOUNT = 0
	droppedAcks = 0
	lastOneWasDropped = 0

	sentPackets = 0
	discardPackets = 0
	receivedPackets = 0

	sentinalkill = 0
	#Sets up a drop value, depending if the drop is deterministic or probabilistic
	if dropType == '-p':
		dropValue = float(sys.argv[5])
	else:
		dropValue = int(sys.argv[5])
#A bug of my code. For some reason, the deterministic drop value cannot be smaller than window size
		if windowSize > dropValue:
			print '[' + str(time.time()) + '] The deterministic drop value is smaller than the window! Pick a bigger window and try again.'
			sys.exit()

	requestNumber = 0
#Get the user input and start up the listening thread
	sys.stdout.write('node> ')
	sys.stdout.flush()

	listen_thread = threading.Thread(target=listen, args=())
	listen_thread.daemon = True
	listen_thread.start()

	amSender = 0
	input = raw_input()
	amSender = 1
#Split up the input and send out my data packet
	inputParts = input.split(None, 1)
	realMessage = inputParts[1]
	masterList = []
	seqNum = 0


#masterList is my buffer. 
#masterList contains all information, it is a dynamically changing buffer depending on input. 
	for i in realMessage:
		masterList.append(('m',seqNum, i, 'probe'))
		seqNum = seqNum + 1
	windowBegin = 0 


	sendAWindow(windowBegin)

#This is the basic listening thread. I handle the acks and packets via this thread.
def listen():
	global requestNumber
	global windowBegin
	global masterList
	global receivedPackets
	global startTime
	global sentinalkill
	global MASTERPACKETCOUNT
	global MASTERACKCOUNT
	global allSent
	global timer_thread
	global listen_thread
	global amSender
	windowBegin = 0
	requestNumber = 0

	while 1:
		firstMessage = socket.recv(1024)
		message = eval(firstMessage)
		messageType = message[0]
		number = message[1]
		data = message[2]
		flushOrNot = message[3]
#There are 4 types of messages. m stands for packet, and ack stands for acknowledgements.
#m stands for packets, ack stands for ACKS, allsent tells me all my packets have been sent, and shitIsOver tells me to print my summary for the sender
		if messageType == 'allsent':
			allSent = 1
		if messageType == 'ack':
			time.sleep(.000001)
			MASTERACKCOUNT += 1

			receiveAnAck(number)
		if messageType == 'm':
			time.sleep(.0001)
			MASTERPACKETCOUNT += 1
			receiveAPacket(number, data)
		if messageType == 'shitIsOver':
			lossRate = float(discardPackets)/receivedPackets * 100
			print '[' + str(float(time.time())) + ']' + ' [Summary] ' + str(discardPackets) + '/' + str(receivedPackets) + ' packets dropped, loss rate = '  + str(lossRate)  + "%"
			amSender = 0
			main()
			break


#This is my timer. 
#It has a relatively simple operation, if the current time is bigger than the start time, then resend the window of packets

def timer():
 	global currentTime
 	global startTime 
 	global amSender
 	while 1:
 		currentTime = float(time.time())
 		if (currentTime - startTime) > .5 and amSender == 1:
 			if windowBegin < len(masterList):
 				print '[' + str(float(time.time())) + '] packet ' + str(windowBegin) + ' timeout'
 			sendAWindow(windowBegin)


#This is the sendAWindow method that shoots out all packets in my current window on the sender side.
def sendAWindow(windowBegin):
	global startTime 
	global allSent
	global sentPackets
	global firstFlushNum
	global flushMode
	global mostRecentPacket
	global packetGate
	allSent = 0 
#Loops over the beginning of the window
	for i in range(windowBegin, windowBegin + windowSize):
		if i < len(masterList):
			startTime = time.time()
			firstFlushNum = windowBegin
			messageOut = masterList[i]
			flushMode = 1
			print '[' + str(float(time.time())) + '] packet ' + str(messageOut[1]) + ' ' + messageOut[2] + ' sent'
			socket.sendto(str(messageOut), (myIP, peerPort))
			mostRecentPacket = i
			if i == windowBegin:
				startTime = time.time()

	allSent = 1		


#This method is for when the window moves and we need to shoot the packet on the 'edge' of the window.
def sendAnEdgePacket(packetNumber):
	global sentPackets
	if packetNumber < min(len(masterList), windowBegin + windowSize):
		messageOut = masterList[packetNumber]
		socket.sendto(str(messageOut), (myIP, peerPort))
		print '['+ str(float(time.time())) + '] packet ' + str(messageOut[1]) + ' ' + messageOut[2] + ' sent'
		startTime = time.time()

 
#Receive an ACK handles the acknowledgements sent.
def receiveAnAck(ackNum):
	global windowBegin
	global startTime
	global allSent
	global flushMode
	global currentPacket
	global sentinalkill
	global droppedAcks
	global mostRecentPacket
	global ackGate
	global lastOneWasDropped
	global timer_thread
	global listen_thread

	global startTime
	global amSender
	ackGate += 1
#Check the type of drop and drop deterministically or probabilistically
	if dropType == '-p':
		x = random.random()
		if x < dropValue:
			dropIt = 1
		else:
			dropIt = 0
	if dropType == '-d':
		if (ackGate) % dropValue == 0 and ackGate != 0:
			dropIt = 1
		else: 
			dropIt = 0
#Dropped ack procedure
	if dropIt == 1: 
		print '[' + str(float(time.time())) + '] ack' + str(ackNum) + ' discarded'
		startTime = time.time()
		if allSent == 1:
			sendAnEdgePacket(ackNum + windowSize)
		droppedAcks += 1
		lastOneWasDropped = 1
		if ackNum == len(masterList) - 1:
			sendAnEdgePacket(ackNum)
	
#Received ack procedure that has the ack number higher or equal to the beginning of the window
	elif dropIt == 0 and ackNum >= windowBegin:
		print '[' + str(float(time.time())) + '] ack' + str(ackNum) + ' received, window moves to ' + str(ackNum + 1)
		windowBegin = ackNum + 1
	

		if allSent == 1 and lastOneWasDropped == 0:
			sendAnEdgePacket(windowBegin + windowSize - 1)
		elif allSent == 1 and lastOneWasDropped == 1:
			sendAnEdgePacket(windowBegin + windowSize)
		
		lastOneWasDropped = 0

#Start it over once done parsing through the information
		if ackNum == len(masterList) - 1 and ackNum != 0:
			lossRate = float(droppedAcks)/(MASTERACKCOUNT + 1) * 100
			print '[' + str(time.time()) + '] [Summary] ' + str(droppedAcks) + '/' + str(MASTERACKCOUNT+ 1) + ' discarded, loss rate = '  + str(lossRate)  + "%"
			shitIsOver = ('shitIsOver', 0, 0, 0, 0)
			socket.sendto(str(shitIsOver), (myIP, peerPort))
			amSender = 0
			allSent = 0
			main()
#Basically an edge case prevention that keeps the program running if none of the above conditionals are met
	elif dropIt == 0 and ackNum != windowBegin:
		print '[' + str(float(time.time())) + '] ack' + str(ackNum) + ' received, window moves to ' + str(ackNum + 1)




#This method sends out acknowledgements
def sendAck(ackNum):
	messageOut = ('ack', ackNum, ackNum + 1, 'probeAck')
	socket.sendto(str(messageOut), (myIP, peerPort))
	print '[' + str(float(time.time())) + '] ack' + str(ackNum) + ' sent, expecting packet ' + str(ackNum + 1)

#This method handles packets
def receiveAPacket(packetNumber, packetData):
	global requestNumber
	global discardPackets
	global receivedPackets
	global packetGate
	global startTime
#packetGate is the overall packet count that allows me drop every other
	packetGate += 1
#Determine the type of drop and drop accordingly.
	if dropType == '-p':
		x = random.random()
		if x < dropValue:
			dropIt = 1
		else:
			dropIt = 0
	if dropType == '-d':
		if packetGate % dropValue == 0 and packetGate != 0:
			dropIt = 1
		else: 
			dropIt = 0
#3 situations:
#1st situation is a dropped packet
#2nd is a recieved packet that equals my request number
#3rd  is a received packet that does not match my request number
	if dropIt == 1: 
		print '[' + str(float(time.time())) + '] packet' + str(packetNumber) + ' ' + str(packetData) + ' discarded.'
		discardPackets += 1
		receivedPackets += 1
	elif dropIt == 0 and packetNumber == requestNumber: 
		requestNumber = requestNumber + 1
		print '[' + str(float(time.time())) + '] packet' + str(packetNumber) + ' ' + str(packetData) + ' received'
		sendAck(packetNumber)
		receivedPackets += 1
	elif dropIt == 0 and packetNumber != requestNumber:
		print '[' + str(float(time.time())) + '] packet' + str(packetNumber) + ' ' + str(packetData) + ' received'
		sendAck(requestNumber - 1)
		receivedPackets += 1



#Kill the program using keyboard interrupt


if __name__ == '__main__':
	main()



	timer_thread = threading.Thread(target=timer, args=())
	timer_thread.daemon = True
	timer_thread.start()


	while True:
		time.sleep(0.000001)
		if sentinalkill == 1:
			break



