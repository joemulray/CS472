#!/usr/bin/env python
# coding: utf-8
import socket 
import struct
import sys
from logging import logger
from portmanager import PortManager
import thread
import os


ManagePorts = PortManager()
BUFFER = 1029


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
		self.dataport = 20 #default 20

	def doProtocol(self):
		self.start()
		while True:
			try:
				message = self.receive()
				if message:
					self.log.received(message)
					parsedmessage = message.split()
					(function, cmd) = self.evaluation(parsedmessage[0], parsedmessage)
					function(cmd)
			except socket.error as error:
				self.log.debug(self.address[0] + ": Disconneted")
				self.log.error(str(error))
				break

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
			command+="\r\n"
			self.log.sending(command)
			self.socket.sendall(command)

		except socket.error as error:
			self.log.error(error)


	def datasocket(self, command=None):
		response = "425 Can't open dataconnection"
		try:
			dsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			dsocket.connect((socket.gethostname(), self.dataport))

			for value in command:
				dsocket.send(str(value) + "\r\n")

			dsocket.close()
			response = "226 Closing data connection. Requested file action successful"

		except socket.error as error:
			self.log.error("datasocket" + str(error))
			print "port: %s host: %s" %(self.dataport, socket.gethostname())

		return response


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
		if self.username in self.users:
			if self.users[self.username] == self.password:
				return True
			return False
		return False



	def changeworkingdirectory(self, cmd):
		command = "250 Requested file action okay, completed."
		if not self.__authenticated:
			command = "530 Login incorrect."
			self.send(command)
			return

		if len(cmd) != 2:
			command = "501 Syntax error in parameters or arguments."

		newcd = cmd[1]
		if newcd[0] != "/":
			newcd = self.path + newcd

		if os.path.isdir(newcd):
			self.path = newcd
		else:
			command = "550 Requested action not taken. File unavailable"

		self.send(command)


	def cdup(self, cmd):
		print "cdup"
		#authorization
		pass

	def quit(self, cmd):
		command = "221 Goodbye."
		self.send(command)
		self.socket.close()

	def pasv(self, cmd):

		if not self.__authenticated:
			command = "530 Login incorrect."
			self.send(command)
			return

		#generate port
		self.dataport = int(ManagePorts.getport())

		hostname = socket.gethostname()
		(hostname, _, hostip) = socket.gethostbyaddr(hostname)
		host = hostip[0].replace(".", ",")

		#convert port to hex
		remainderport = self.dataport % 256

		p1 = (self.dataport - remainderport) / 256
		p2 = remainderport

		command = "227 Entering Passive Mode (%s,%s,%s)." %(host, p1, p2)
		self.send(command)

	def epsv(self, cmd):
		#authorization
		print "epsv"
		pass

	def port(self, cmd):
		#authorization
		command = "200 Port okay."

		if not self.__authenticated:
			command = "530 Login incorrect."
			self.send(command)
			return

		try:

			msg = ''.join(cmd)
			pasv = msg[4:].translate(None, "().\r\n").split(",")
			p1 = int(pasv[-2])
			p2 = int(pasv[-1])

			port = (p1 * 256) + p2
			self.dataport = port

		except Exception as error:
			self.log.error("port" + str(error))
			command = "501 Syntax error in parameters or arguments."

		self.send(command)


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
		if not self.__authenticated:
			command = "530 Login incorrect."
			self.send(command)
			return

		command = "257 %s" % (self.path)
		self.send(command)


	def syst(self, cmd):
		#authentication
		print "syst"
		pass

	def list(self, cmd):
		if not self.__authenticated:
			command = "530 Login incorrect."
			self.send(command)
			return

		arraylist = os.listdir(self.path)
		command = "150 File status okay; about to open data connection."
		self.send(command)

		command = self.datasocket(arraylist)
		self.send(command)


	def help(self, cmd):
		print "help"
		pass


	def invalid(self, cmd):
		command = "400 The command was not accepted and the requested action did not take place"
		self.send(command)


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
		self.port = int(2121)
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
