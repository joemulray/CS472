#!/usr/bin/env python

import socket 
import struct
import sys
from logging import logger


class ServerSocket:
	def __init__(self, host=socket.gethostname(), port=2121, backlog=5, filename="server.log"):
		self.host = host
		self.port = port
		self.backlog = backlog
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.bind((host, port))
		self.serversocket.listen(backlog)
		self.log = logger(filename, "[server]")

		#log init
		msg = "Starting server on %s:%s" %(self.host, self.port)
		self.log.debug(msg)

	def accept(self):
		return self.serversocket.accept()

	def close(self):
		self.serversocket.close()

	def receive(self, socket):
		# unpack and get the value from the received bytes
		try:
			message = socket.recv(4)
			chunk = struct.unpack("i", message)
			value = chunk[0]
			self.log.received(value)
		except struct.error as error:
			self.log.error(error)
			value=None
		return value


	def doProtocol(self, socket=None) :
		value = self.receive(socket)

		if value:
			#this is the protocol
			value+=1
			#this is the protocol
			self.send(socket, value)


	def send(self, socket, value):
		# pack and send a value one larger back
		try:
			self.log.sending(value)
			message = struct.pack("i", value)
			socket.send(message)
		except struct.error as error:
			self.log.error(str(error))
			pass

def main():

	serversocket = ServerSocket()

	while True:
		# accept connections from outside
		(socket, address) = serversocket.accept()
		serversocket.doProtocol(socket)
		socket.close()
	
if __name__ == "__main__" :
	main()
