#!/usr/bin/env python
import socket 
import sys
import threading
import os

#import configparser to read from config file
from configparser import ConfigParser, DuplicateOptionError, Error

#created classes
from logging import logger
from portmanager import PortManager


#Global Variables
authorized_users_file = "users.ini"
manageports = PortManager()
config = ConfigParser()

BUFFER = 1024
AUTHORIZED_USERS = {}
log = None
lock = threading.Lock()


"""
TODO:
	display client info in logger in logs
	pydoc comments
	fix ls command
"""


class FTPServer(threading.Thread):
	"""
	FTPServer handles managing the connections and status response from the clients

	Attributes:
		connections:

	"""

	def __init__(self, socket, address=None):
		self.socket = socket
		self.address = address
		self.path = os.getcwd()
		self.username = None
		self.password = None
		self.__authenticated = False
		self.dataport = 20 #default 20
		self.passivemode = False
		self.passivesocket = None
		threading.Thread.__init__(self)

	"""
	Decorator function to handle if user is authenticated or not
	"""
	def _authentication(function):
		def authwrapper(self, *args):
			if not self.__authenticated:
				command = "530 Login incorrect."
				self.send(command)
				return
			return function(self, *args)
		return authwrapper


	def _argumentrequired(function):
		def argumentwrapper(self, *args):
			#If I am exptecting an argument dont waste my time if not just return invalid syntax
			if len(*args) != 2:
				command = "501 Syntax error in parameters or arguments."
				self.send(command)
				return
			return function(self, *args)
		return argumentwrapper


	def _noarguments(function):
		def noargswrapper(self, *args):
			#I am expecting only one argument if you send me other info, getting a 501
			if len(*args) != 1:
				command = "501 Syntax error in parameters or arguments."
				self.send(command)
				return
			return function(self, *args)
		return noargswrapper


	def _thread(function):
		def threadwrapper(self, *args):
			threading.Thread(target=function, args=(self, )).start()
		return threadwrapper


	@_thread
	def doProtocol(self):
		self.welcome()
		while True:
			try:
				message = self.receive()
				if message:
					log.received(message)
					parsedmessage = message.split()
					(function, cmd) = self.evaluation(parsedmessage[0], parsedmessage)
					function(cmd)
			except socket.error as error:
				msg = "Client Disconneted %s:%s" %(self.address[0], self.address[1])
				log.debug(msg)
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
			log.sending(command)
			self.socket.sendall(command)

		except socket.error as error:
			log.error(error)


	def datasocket(self, command=None):
		response = "425 Can't open dataconnection"
		try:
			dsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if self.passivemode:
				(dsocket, self.address) = self.passivesocket.accept()
			else:
				dsocket.connect((socket.gethostname(), self.dataport))

			for value in command:
				dsocket.send(str(value) + "\r\n")

			#close the datasocket
			dsocket.close()

			#if we were in passive mode close the passive socket
			if self.passivemode:
				self.passivesocket.close()

			response = "226 Closing data connection. Requested file action successful"

		except socket.error as error:
			log.error("datasocket " + str(error))
			print "port: %s host: %s" %(self.dataport, socket.gethostname())

		return response



	def datasocketrecv(self):
		response = "425 Can't open dataconnection"
		recvdata = ""
		try:
			dsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if self.passivemode:
				(dsocket, self.address) = self.passivesocket.accept()
			else:
				dsocket.connect((socket.gethostname(), self.dataport))

			while True:
				message = dsocket.recv(BUFFER)
				recvdata += message
				if '\n' in message:
					break

			if self.passivemode:
				self.passivesocket.close()

			response = "226 Closing data connection. Requested file action successful"

		except socket.error as error:
			log.error("datasocketrecv " + str(error))
			return response, recvdata

		return (response, recvdata)



	def welcome(self):
		command = "220 Service ready for new user."
		self.send(command)

	@_argumentrequired
	def user(self, cmd):
		self.username = cmd[1]
		command = "331 Please specify the password."

		self.send(command)

	@_argumentrequired
	def passwd(self, cmd):

		password = cmd[1]
		self.password = password
		self.__authenticated = self.verifyauthentication()

		if self.__authenticated:
			command = "230 Login successful"
		else:
			command = "530 Authentication Failed"

		self.send(command)


	def verifyauthentication(self):
		if self.username in AUTHORIZED_USERS:
			if AUTHORIZED_USERS[self.username] == self.password:
				return True
			return False
		return False


	@_argumentrequired
	@_authentication
	def chdir(self, cmd):
		command = "250 Requested file action okay, completed"
		newcd = cmd[1]
		#if not given a full path
		if newcd[0] != "/":
			newcd = self.path + "/" + newcd

		if os.path.isdir(newcd):
			os.chdir(newcd)
			self.path = os.getcwd()

		else:
			command = "550 Requested action not taken. File unavailable"

		self.send(command)

	@_noarguments
	@_authentication
	def cdup(self, cmd):
		command = "250 Requested file action okay, completed."

		newcd = self.path + "/.."
		os.chdir(newcd)
		self.path = os.getcwd()

		self.send(command)


	def quit(self, cmd):
		command = "221 Goodbye."
		self.send(command)
		self.socket.close()

	@_noarguments
	@_authentication
	def pasv(self, cmd):

		#stop threads from getting the same port
		with lock:
			self.dataport = int(manageports.getport())

		hostname = socket.gethostname()
		(hostname, _, hostip) = socket.gethostbyaddr(hostname)
		host = hostip[0].replace(".", ",")

		#convert port to hex
		remainderport = self.dataport % 256

		p1 = (self.dataport - remainderport) / 256
		p2 = remainderport

		self.passivemode = True
		self.passivesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.passivesocket.bind((hostname, self.dataport))
		self.passivesocket.listen(5)

		command = "227 Entering Passive Mode (%s,%s,%s)." %(host, p1, p2)
		self.send(command)

	@_noarguments
	@_authentication
	def epsv(self, cmd):
		#socket.inet_pton(socket.AF_INET6, some_string) iPv6

		#stop threads from getting the same port
		with lock:
			self.dataport = int(manageports.getport())

		hostname = socket.gethostname()
		(hostname, _, hostip) = socket.gethostbyaddr(hostname)

		self.passivemode = True
		self.passivesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.passivesocket.bind((hostname, self.dataport))
		self.passivesocket.listen(5)

		command = "229 Entering Passive Mode (|||%s)." %(self.dataport)
		self.send(command)

		
	@_argumentrequired
	@_authentication
	def port(self, cmd):
		command = "200 Port okay."
		try:
			msg = ''.join(cmd)
			pasv = msg[4:].translate(None, "().\r\n").split(",")
			p1 = int(pasv[-2])
			p2 = int(pasv[-1])

			port = (p1 * 256) + p2
			self.dataport = port

			#Turn off passive mode
			self.passivemode = False

		except Exception as error:
			log.error("port" + str(error))
			command = "501 Syntax error in parameters or arguments."

		self.send(command)

	@_argumentrequired
	@_authentication
	def eprt(self, cmd):
		command = "200 Port okay."
		try:
			#EPRT |1|127.0.0.1|52540|
			eprtdata = cmd[1]
			eprtdata = eprtdata[1:-1] #remove pipe from front and back
			af, network, port = eprtdata.split("|")

			self.dataport = int(port)

			#Turn off passive mode
			self.passivemode = False

		except Exception as error:
			log.error("EPRT " + str(error))
			command = "501 Syntax error in parameters or arguments."

		self.send(command)

	@_argumentrequired
	@_authentication
	def retr(self, cmd):

		filepath = cmd[1]
		content = ""
		try:
			with open(filepath, 'r') as openfile:
				content = openfile.read()

		except IOError as error:
			log.error("RETR " + str(error))
			command = "550 Requested action not taken. File unavailable"
			self.send(command)
			return

		command = "150 File status okay; about to open data connection."
		self.send(command)

		sockdata = []
		sockdata.append(content)

		command = self.datasocket(sockdata)
		self.send(command)


	@_argumentrequired
	@_authentication
	def stor(self, cmd):
		filepath = cmd[1]

		try:
			file = open(filepath, "w+")
			#file open now send 150
			command = "150 File status okay; about to open data connection."
			self.send(command)

			command, data = self.datasocketrecv()
			file.write(data)
			file.close()

			self.send(command)

		except IOError as error:
			log.error("stor " + str(error))
			command = "550 Requested action not taken. File unavailable"
			self.send(command)


	@_noarguments
	@_authentication
	def pwd(self, cmd):
		command = "257 %s" % (self.path)
		self.send(command)

	@_noarguments
	@_authentication
	def syst(self, cmd):
		#authentication
		if len(cmd) != 1:
			command = "501 Syntax error in parameters or arguments."
			self.send(command)

		system = sys.platform
		command = "215 UNIX Type: %s" % system
		self.send(command)


	@_authentication
	def list(self, cmd):

		arraylist = os.listdir(self.path)
		command = "150 File status okay; about to open data connection."
		self.send(command)

		command = self.datasocket(arraylist)
		self.send(command)


	def help(self, cmd):
		command = "214 The following commands are recognized."
		self.send(command)
		commands = ["USER PASS CWD CDUP QUIT PASV EPSV PORT EPRT RETR STOR PWD \
		SYST LIST HELP"]
		self.datasocket(commands)


	def invalid(self, cmd):
		command = "400 %s command was not accepted and the requested action did not take place" %(cmd[0])
		self.send(command)

	def evaluation(self, command, parsedmessage):
			return {
			"USER" : (self.user, parsedmessage),
			"PASS" : (self.passwd, parsedmessage),
			"CWD" : (self.chdir, parsedmessage),
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

		#log init
		msg = "Starting server on %s:%s" %(self.host, self.port)
		log.debug(msg)

	def accept(self):
		return self.serversocket.accept()

	def close(self):
		self.serversocket.close()



def main():

	if len(sys.argv) == 3:

		filename = sys.argv[1]
		port = sys.argv[2]

		global log
		log = logger(filename, "[server]")

		try:
			config.read(authorized_users_file)
			for key in config["Authorized Users"]:
				AUTHORIZED_USERS[key] = config["Authorized Users"][key]

		except (DuplicateOptionError, Error) as error:
			log.error("Error " + str(error.message))
			msg = "Error in %s file, Fix before proceeding" %(authorized_users_file)
			log.error(msg)
			exit(1)

		serversocket = ServerSocket(filename, port)

	else:
		print "Usage: server.py <hostname> <filename> <port>"
		exit(0)

	while True:

		(clientsocket, address) = serversocket.accept()
		msg = "Client Connected at %s:%s" %(address[0], address[1])
		log.debug(msg)
		ftpserver = FTPServer(clientsocket, address)
		ftpserver.doProtocol()


	
if __name__ == "__main__" :
	main()
