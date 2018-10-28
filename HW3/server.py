#!/usr/bin/env python

import socket 
import struct
import sys
from logging import logger
import thread

class PortManager:
	def __init__(self):
		self.ports = []

	def exists(self, port):
		return True if port in self.ports else False

	def addport(self, port):
		self.ports.append(port)


class FTPServer:
	"""
	FTPServer handles managing the connections and status response from the clients

	Attributes:
		connections:

	"""

	def __init__(self, socket, address):
		self.socket = socket
		self.address = address
		self.cd = "/"
		self.__authenticated = False
		self.users = { "root" : "password" , "josephmulray" : "root" }

	def doProtocol(self):
		pass


	def user(self, cmd):
		pass

	def password(self, cmd):
		pass

	def changeworkingdirectory(self, cmd):
		#authroization
		pass

	def cdup(self, cmd):
		#authorization
		pass

	def quit(self, cmd):
		pass


	def pasv(self, cmd):
		#authorization
		pass

	def espv(self, cmd):
		#authorization
		pass

	def port(self, cmd):
		#authorization
		pass

	def eprt(self, cmd):
		#authorization
		pass

	def retr(self, cmd):
		#authorization
		pass

	def stor(self, cmd):
		#authorization
		pass

	def pwd(self, cmd):
		#authorization
		pass

	def syst(self, cmd):
		#authentication
		pass

	def list(self, cmd):
		#authentication
		pass

	def help(self, cmd):
		pass


	def invalid(self, cmd):
		pass


	def evaluation(self, commmand, fullmsg):
			return {
			"USER" : (self.user, fullmsg),
			"PASS" : (self.password, fullmsg),
			"CWD" : (self.changeworkingdirectory, fullmsg),
			"CDUP" : (self.cdup, fullmsg),
			"QUIT" : (self.quit,fullmsg),
			"PASV" : (self.pasv, fullmsg),
			"EPSV" : (self.epsv, fullmsg),
			"PORT" : (self.port, fullmsg),
			"EPRT" : (self.eptr, fullmsg),
			"RETR" : (self.retr, fullmsg),
			"STOR" : (self.stor, fullmsg),
			"PWD" : (self.pwd, fullmsg),
			"SYST" : (self.syst, fullmsg),
			"LIST" : (self.list, fullmsg),
			"HELP" : (self.help, fullmsg),
			}.get(status, (self.invalid, fullmsg))



class ServerSocket:
	def __init__(self, host=socket.gethostname(), filename="server.log", port=2121, backlog = 5):
		self.host = host
		self.port = int(port)
		self.backlog = backlog

		print "host : %s port: %s" %(host, port)

		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.bind((self.host, self.port))
		self.serversocket.listen(self.backlog)
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

	if len(sys.argv) == 3:

		host = sys.argv[1],
		filename = sys.argv[2]

		serversocket = ServerSocket(host, filename)

	elif len(sys.argv) == 4:

		host = sys.argv[1],
		filename = sys.argv[2]
		port = sys.argv[3]

		serversocket = ServerSocket(host, filename, port)
	# else:
		# print "Usage: server.py <hostname> <filename> <port>"
		# exit(0)

	while True:
		# accept connections from outside

		(clientsocket, address) = serversocket.accept()
		ftpserver = FTPServer(clientsocket, address)
		ftpserver.doProtocol()
		# thread.start_new_thread(ftpserver.doProtocol(), )
	
if __name__ == "__main__" :
	main()
