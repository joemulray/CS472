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
	display full output from help message
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

	
	def close(self):
		"""
		Closes the logger file

		:return: returns nothing
		"""
		self.file.close()


class FTP:
	def __init__(self, socket=None, username="root", password="password"):
		self.socket = socket
		self.ftplog = socket.log
		self.username = username
		self.password = password
		self.__authorized = False
		self.commands = {
						"user" : "USER", "pasv" : "PASV", "quit" : "QUIT", \
						"pasv" : "PASV", "epsv" : "EPSV", "port" : "PORT", \
						"eprt" : "EPRT", "retry" : "RETR", "stor" : "STOR", \
						"syst" : "SYST", "list" : "LIST", "pwd" : "PWD", \
						"help" : "HELP", "pass" : "PASS"
						}


	def doProtocol(self):
		while True:
			response = self.socket.receive()
			self.evaulate(response[:3])()



	def command(self):
		cmd = raw_input("ftp> ").split()
		if cmd:
			if cmd[0] in self.commands:
				command = self.buildcmd(cmd)
				self.socket.send(command)

			else:
				self.command()
		else:
			self.command()


	def promptusername(self):
		user = "USER " + raw_input("ftp> Name: ") + "\r\n"
		self.username = user
		self.socket.send(self.username)


	def promptpassword(self):
		password = "PASS " + raw_input("ftp> Password: ") + "\r\n"
		self.password = password
		self.socket.send(self.password)



	def exit(self):
		self.ftplog.close()
		exit(0)


	def buildcmd(self, cmd):
		#cmd is an array
		key = cmd[0]
		cmd.pop(0)

		msg = self.commands[key]
		for param in cmd:
			msg = msg + " " + param

		msg = msg + "\r\n"
		return msg


	def evaulate(self, response):

		return {
			"220" : self.promptusername, #220 FTP Server ready.
			"214" : self.command, #214 The following commands are recognized:
			"221" : self.exit, #221 Goodbye.
			"226" : self.command, #226 Transfer complete.
			"230" : self.command, #230 Login successful.
			"228" : self.command, #228 Entering Passive Mode
			"230" : self.command, #230 Login Succesfuluthorized
			"250" : self.command, #250 "/" is the current directory.
			"257" : self.command, #257 "/" is the current directory.
			"331" : self.promptpassword, #331 Username ok, send password.
			"332" : self.command, #332 Need account for login.
			"421" : self.exit, #421 Control connection timed out.
			"501" : self.command, #501 Syntax error in parameters or arguments.
			"530" : self.command, #530 Authentication failed.
			"550" : self.command, #550 No such file or directory.
			}.get(response, self.command) #default just reprompt for command



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
	if len(sys.argv) == 3:
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
