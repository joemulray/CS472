#!/usr/bin/env python


import socket
import struct
import sys
import datetime


class ClientSocket:
	def __init__(self, host=socket.gethostname(), port=9223):
		self.host = host
		self.port = port
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientsocket.connect((self.host, self.port))

	def close(self):
		self.clientsocket.close()

	def log(self, msg=""):
		#log function
		timenow = datetime.datetime.now()
		time = timenow.strftime("%Y-%m-%d %H:%M")
		print "%s %s" %(time, msg)


	def doProtocol(self) :
		value = int(sys.argv[1])

		# pack and send our argument
		data = struct.pack("i", value)
		self.clientsocket.send(data)

		# get back a response and unpack it
		receivedMessage = self.clientsocket.recv(4)
		chunk = struct.unpack("i", receivedMessage)
		# take the first int only
		message = chunk[0]

		self.log("client received: " + str(message))


def main() :
	if len(sys.argv) != 2 or not sys.argv[1].isdigit() :
		print("Usage: " + str(sys.argv[0]) + " <int>")
		exit(1)

	clientsock = ClientSocket()
	clientsock.doProtocol()
	clientsock.close()

if __name__ == "__main__" :
	main()
