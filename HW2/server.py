#!/usr/bin/env python

import socket 
import struct
import datetime


class ServerSocket:
	def __init__(self, host=socket.gethostname(), port=9223, backlog=5):
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.bind((host, port))
		self.serversocket.listen(backlog)

	def accept(self):
		return self.serversocket.accept()

	def close(self):
		self.serversocket.close()

	def receive(self, socket):
		message = socket.recv(4)
		# unpack and get the value from the received bytes
		chunk = struct.unpack("i", message)  # TODO: error check here
		value = chunk[0]
		self.log("Received: " + str(value))
		return value


	def doProtocol(self, socket=None) :
		value = self.receive(socket)
		#this is the protocol
		value+=1
		#this is the protocol
		self.send(socket, value)


	def send(self, socket, value):
		# pack and send a value one larger back
		self.log("Sending: " + str(value))
		message = struct.pack("i", value)
		socket.send(message)

	def log(self, msg=""):
		#log function
		timenow = datetime.datetime.now()
		time = timenow.strftime("%Y-%m-%d %H:%M")
		print "%s [server] %s" %(time, msg)


def main() :

	serversocket = ServerSocket()

	while True:
		# accept connections from outside
		(socket, address) = serversocket.accept()
		serversocket.doProtocol(socket)
		socket.close()
	
if __name__ == "__main__" :
	main()
