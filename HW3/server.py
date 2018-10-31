#!/usr/bin/env python

import socket 
import struct
import sys
from logging import logger
import thread


BUFFER = 1029

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

	def __init__(self, socket, address=None, filename="server.log"):
		self.socket = socket
		self.address = address
		self.log = logger(filename, "[server]")
		self.path = "/"
		self.username = None
		self.password = None
		self.__authenticated = False
		self.users = { "root" : "root" , "josephmulray" : "root" }

	def doProtocol(self):
		self.start()
		while True:
			message = self.receive()
			if message:
				self.log.debug(message)
				parsedmessage = message.split()
				(function, cmd) = self.evaluation(parsedmessage[0], parsedmessage)
				function(cmd)


	def receive(self):
		response = ""
		while True:
			message = self.socket.recv(BUFFER)
			response += message
			if '\n' in message:
				break

		return response


	def send(self, command=None):
		try:
			self.log.sending(command)
			self.socket.sendall(command)

		except socket.error as error:
			self.log.error(error)


	def start(self):
		command = "220 Service ready for new user."
		self.send(command)

	def user(self, cmd):
		command = "501 Syntax error in parameters or arguments."
		if len(cmd) == 2:
			self.username = cmd[1]
			command = "331 Please specify the password."

		self.send(command)

	def passwd(self, cmd):
		command = "501 Syntax error in parameters or arguments."
		if len(cmd) == 2:
			password = cmd[1]
			self.password = password
			self.__authenticated = self.verifyauthentication()

			if self.__authenticated:
				command = "230 Login successful"
			else:
				command = "530 Authentication Failed"

		self.send(command)


	def verifyauthentication(self):
		print self.username
		print self.users
		if self.username in self.users:
			print "IN USERNAMES"
			if self.users[self.username] == self.password:
				print "true"
				return True
			return False
		return False


	def changeworkingdirectory(self, cmd):
		"print changeworkingdirectory"
		#authroization
		pass

	def cdup(self, cmd):
		print "cdup"
		#authorization
		pass

	def quit(self, cmd):
		print "quit"
		pass


	def pasv(self, cmd):
		#authorization
		print "pasv"
		pass

	def epsv(self, cmd):
		#authorization
		print "epsv"
		pass

	def port(self, cmd):
		#authorization
		print "port"
		pass

	def eprt(self, cmd):
		#authorization
		print "eprt"
		pass

	def retr(self, cmd):
		#authorization
		print "retr"
		pass

	def stor(self, cmd):
		#authorization
		print "stor"
		pass

	def pwd(self, cmd):
		#authorization
		print "pwd"
		pass

	def syst(self, cmd):
		#authentication
		print "syst"
		pass

	def list(self, cmd):
		#authentication
		print "list"
		pass

	def help(self, cmd):
		print "help"
		pass


	def invalid(self, cmd):
		print "invalid"
		pass


	def evaluation(self, command, parsedmessage):
			return {
			"USER" : (self.user, parsedmessage),
			"PASS" : (self.passwd, parsedmessage),
			"CWD" : (self.changeworkingdirectory, parsedmessage),
			"CDUP" : (self.cdup, parsedmessage),
			"QUIT" : (self.quit, parsedmessage),
			"PASV" : (self.pasv, parsedmessage),
			"EPSV" : (self.epsv, parsedmessage),
			"PORT" : (self.port, parsedmessage),
			"EPRT" : (self.eprt, parsedmessage),
			"RETR" : (self.retr, parsedmessage),
			"STOR" : (self.stor, parsedmessage),
			"PWD" : (self.pwd, parsedmessage),
			"SYST" : (self.syst, parsedmessage),
			"LIST" : (self.list, parsedmessage),
			"HELP" : (self.help, parsedmessage),
			}.get(command, (self.invalid, parsedmessage))



class ServerSocket:
	def __init__(self, filename="server.log", port=2121, backlog = 5):
		self.port = int(port)
		self.backlog = backlog
		self.host = socket.gethostname()
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


def main():

	if len(sys.argv) == 3:

		filename = sys.argv[1]
		port = sys.argv[2]
		
		serversocket = ServerSocket(filename, port)

	else:
		print "Usage: server.py <hostname> <filename> <port>"
		exit(0)

	while True:
		# accept connections from outside

		(clientsocket, address) = serversocket.accept()
		ftpserver = FTPServer(clientsocket, address, filename)
		ftpserver.doProtocol()
		# clientsocket.close()
		# thread.start_new_thread(ftpserver.doProtocol(), )
	
if __name__ == "__main__" :
	main()
