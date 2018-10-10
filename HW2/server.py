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
		(socket, address) = self.serversocket.accept()
		return (socket, address)

	def close(self):
		self.serversocket.close()

	def doProtocol(self, socket=None) :
		# read four bytes from the socket (1 padded int)
		receivedMessage = socket.recv(4)

		# unpack and get the value from the received bytes
		chunk = struct.unpack("i", receivedMessage) # TODO: error check here
		value = chunk[0]
		self.log("server received: " + str(value))
		
		# pack and send a value one larger back
		sendMessage = struct.pack("i", value + 1)
		socket.send(sendMessage)

	def log(self, msg=""):
		#log function
		timenow = datetime.datetime.now()
		time = timenow.strftime("%Y-%m-%d %H:%M")
		print "%s %s" %(time, msg)


def main() :

	serversocket = ServerSocket()

	while True:
		# accept connections from outside
		(socket, address) = serversocket.accept()
		serversocket.doProtocol(socket)
		socket.close()
	
if __name__ == "__main__" :
	main()
