#!/usr/bin/env python

import socket
import struct
import sys
import datetime
from logging import logger


class ClientSocket:
	def __init__(self, host=socket.gethostname(), port=21, filename="client.log"):
		self.host = host
		self.port = port
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log = logger(filename, "[client]")

		#log init
		msg = "Connecting to %s:%s" %(self.host, self.port)
		self.log.debug(msg)

		try:
			self.clientsocket.connect((self.host, self.port))
			msg = "Connected to %s:%s" %(self.host, self.port)
			self.log.debug(msg)

		except socket.error as e:
			self.log.error(str(e))
			self.clientsocket = None
			pass

	def close(self):
		self.clientsocket.close()

	def log(self, msg=""):
		print "%s [client] %s" %(time, msg)

	def receive(self):
		message = self.clientsocket.recv(4)
		try:
			chunk = struct.unpack("i", message)
			# take the first int only
			value = chunk[0]
			self.log.received(value)
		except struct.error as error:
			self.log.error(error)
			pass


	def send(self):
		try:
			value = int(sys.argv[1])
			self.log.sending(value)
			data = struct.pack("i", value)
			self.clientsocket.send(data)
			return True
		except struct.error as error:
			self.log.error(error)
			return False

	def doProtocol(self):
		#if message was actually sent
		if self.send():
			self.receive()


	def connected(self):
		if self.clientsocket:
			return True
		else:
			return False

def main():
	if len(sys.argv) == 3:
		clientsock = ClientSocket(sys.argv[1], sys.argv[2])
	else:
		clientsock = ClientSocket()

	if clientsock.connected():

		clientsock.doProtocol()
		clientsock.close()

if __name__ == "__main__" :

	main()
