#!/usr/bin/env python

import socket
import struct
import sys
import datetime

"""
Joseph Mulray
CS472 - Computer Networks
Fall 2018-2019
Homework Assignment #2

	Implement a FTP (File Transfer Protocol) client that can login, list
	directory information, and store and retrieve information from a server hosting the FTP service.
"""


"""
#TODO:
	add structure to commands `USER {user}`
	determine unathorized from authorized methhods
	handle invalid input
	remove struct error handling
	add pydoc comments
"""




BUFFER  = 77777

class logger:
	"""
	Logger encapsulates a filename, service, and time format
	"""
	def __init__(self, filename, service=None, format="%Y-%m-%d %H:%M"):
		"""
		Constructs a new 'Logger' object

		:param filename: name of file being logged to
		:param service: name of service, eg. {client, server, app}
		:param format: the format of the timestamp
		:return: returns nothing
		"""

		self.file = open(filename, 'w+')
		self.service = service
		self.format = format
		self.debugmsg = "[debug]"
		self.errormsg = "[ERROR]"
		self.timestamp = self.time()

	def debug(self,msg):
		"""
		Display/write debug messages to file or stdout

		:param msg: The message to be logged
		:return: returns nothing
		"""
		log = "%s : %s %s : %s" %(self.timestamp, self.service, self.debugmsg, str(msg).rstrip())
		print log
		self.file.write(log + "\n")

	def error(self,msg):
		"""
		Display/write errors messages to file or stdout

		:param msg: The message to be logged
		:return: returns nothing
		"""
		log = "%s : %s %s : %s" %(self.timestamp, self.service, self.errormsg, str(msg).rstrip())
		print log
		self.file.write(log + "\n")

	def time(self):
		"""
		Contructs a timestamp

		:return timestamp: returns string object of dateformat
		"""
		timenow = datetime.datetime.now()
		return timenow.strftime(self.format)

	def sending(self, value):
		"""
		Constructs Sent message for debug

		:param value: value being sent to server
		:return: returns nothing
		"""
		self.debug("Sent: " + str(value))

	def received(self, value):
		"""
		Constructs Recieved message for debug

		:param value: value being recieved from server
		:return: returns nothing
		"""
		self.debug("Received: " + str(value))



class FTP:
	def __init__(self, socket=None, username="root", password="password"):
		self.socket = socket
		self.ftplog = socket.log
		self.username = username
		self.password = password
		self.__authorized = False
		self.commands = ["user", "pass", "cwd", "quit", "pasv", "espv", "port", "eprt", "retr", \
		"stor", "pwd", "syst", "list", "help"]

	def doProtocol(self):
		message = self.socket.receive()
		if message[:3] == "220":
			self.login()

		else:
			self.ftplog.error(message)


	def login(self):
		user = "USER " + raw_input("ftp> Name: ") + "\r\n"
		self.username = user
		self.socket.send(self.username)
		repsonse = self.socket.receive()

		if repsonse[:3] == "331":
			password = "PASS " + raw_input("ftp> Password: ") + "\r\n"
			self.password = password
			self.socket.send(self.password)
			response = self.socket.receive()

			if response[:3] == "230":
				self.__authorized = True




class ClientSocket:
	def __init__(self, host=socket.gethostname(), filename="client.log" , port=21):
		self.host = host
		self.port = port
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log = logger(filename, "[client]")

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


	def receive(self):
		try:
			message = self.clientsocket.recv(BUFFER)
			self.log.received(message)
		except struct.error as error:
			self.log.error(error)
			message = ""
			pass

		return message


	def send(self, command):
		try:
			self.log.sending(command)
			self.clientsocket.sendall(command)

		except struct.error as error:
			self.log.error(error)
			return False


	def connected(self):
		if self.clientsocket:
			return True
		else:
			return False

def main():
	if len(sys.argv) ==  3:
		clientsock = ClientSocket(sys.argv[1], sys.argv[2])
	elif len(sys.argv) == 4:
		clientsock = ClientSocket(sys.argv[1], sys.argv[2], int(sys.argv[3]))
	else:
		print "Usage: client.py <hostname> <filename> <port>"
		exit(0)

	if clientsock.connected():
		ftp = FTP(clientsock)
		ftp.doProtocol()


if __name__ == "__main__" :

	main()
