#!/usr/bin/env python


import socket
import struct
import sys
import datetime


class ClientSocket:
	def __init__(self, host=socket.gethostname(), port=21):
		self.host = host
		self.port = port
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.clientsocket.connect((self.host, self.port))
		except socket.error as e:
			self.log("ERROR" + str(e))
			self.clientsocket = None
			pass

	def close(self):
		self.clientsocket.close()

	def log(self, msg=""):
		timenow = datetime.datetime.now()
		time = timenow.strftime("%Y-%m-%d %H:%M")
		print "%s [client] %s" %(time, msg)

	def receive(self):
		message = self.clientsocket.recv(4)
		try:
			chunk = struct.unpack("i", message)
			# take the first int only
			message = chunk[0]
			self.log("Received: " + str(message))
		except struct.error as error:
			self.log("ERROR" + str(error))
			pass


	def send(self):
		value = int(sys.argv[1])
		self.log("Sending: " + str(value))
		try:
			data = struct.pack("i", value)
			self.clientsocket.send(data)
			return True
		except struct.error as error:
			self.log("ERROR" + str(error))
			return False

	def doProtocol(self):
		#if message was actually sent
		if self.send():
			self.receive()


def main():
	if len(sys.argv) != 2 or not sys.argv[1].isdigit() :
		print("Usage: " + str(sys.argv[0]) + " <int>")
		exit(1)

	clientsock = ClientSocket()
	if clientsock.clientsocket:

		clientsock.doProtocol()
		clientsock.close()

if __name__ == "__main__" :
	main()
