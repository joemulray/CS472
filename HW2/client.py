#!/usr/bin/env python

import socket
import struct
import sys
import datetime
from logging import logger
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




BUFFER  = 4024

class FTP:
	def __init__(self, socket=None, username="root", password="password"):
		self.socket = socket
		self.ftplog = socket.log
		self.username = username
		self.password = password
		self.__authorized = False
		self.datasocket = None
		self.port = 20
		self.action = { "login" : self.username, "port" : self.buildport, "eprt" : self.buildeprt, \
					"retr" : self.buildretr, "stor" : self.buildstor }
		self.commands = {
					"user" : "USER", "quit" : "QUIT", "pasv" : "PASV", \
					"epsv" : "EPSV", "port" : "PORT",  "cd" : "CWD", \
					"eprt" : "EPRT", "retr" : "RETR", "stor" : "STOR", \
					"syst" : "SYST", "list" : "LIST", "pwd" : "PWD", \
					"help" : "HELP", "pass" : "PASS", "ls" : "DIR" \
					}


	def doProtocol(self):
		while True:
			response = self.socket.receive()
			(function, response) = self.evaulate(response[:3], response)
			function(response)


	def command(self, response=None):
		cmd = raw_input("ftp> ").split()
		if cmd:
			if cmd[0] in self.commands:

				if cmd[0] in self.action:
					command = self.action[cmd[0]](cmd)
				else:
					command = self.buildcmd(cmd)

				if command:
					self.socket.send(command)
				else:
					self.command()

			else:
				self.command()
		else:
			self.command()


	def promptusername(self, response=None):
		user = "USER " + raw_input("ftp> Name: ") + "\r\n"
		self.username = user
		self.socket.send(self.username)


	def promptpassword(self, response=None):
		password = "PASS " + raw_input("ftp> Password: ") + "\r\n"
		self.password = password
		self.socket.send(self.password)


	def openconnection(self, response):
		print "\n** OPEN CONNECTION **\n"
		if self.socket.datasocket:
			respc = self.socket.datasocket.receive()
		else:
			self.datasocket = ClientSocket(sys.argv[1], sys.argv[2], self.port)
			self.socket.datasocket = self.datasocket


	def pasvmode(self, response):
		try:
			pasv = response[26:].translate(None, "().\r\n").split(",")
			p1 = int(pasv[-2])
			p2 = int(pasv[-1])

			port = (p1 * 256) + p2
			self.port = port

		except Exception as error:
			self.ftplog.error(error)

		self.datasocket = ClientSocket(sys.argv[1], sys.argv[2], self.port)
		self.socket.datasocket = self.datasocket
		self.command()

	def exit(self, response):
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


	def buildport(self, cmd):
		try:
			host = self.socket.host
			port = int(cmd[1])

			remainderport = port % 256

			#if remainder port greater than zero
			p1 = (port - remainderport) / 256
			p2 = remainderport

			hostmsg = host.replace(".", ",")

			self.port = port
			msg = "%s %s,%s,%s\r\n" %(self.commands["port"], hostmsg, p1, p2)

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("port <port number>")
			return None

		return msg

	def buildeprt(self, cmd):
		try:
			port = cmd[1]
			host = self.socket.host
			msg = "%s |%s|%s|%s|\r\n" %(self.commands["eprt"], 1, host, port)

			return msg

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("eprt <port>")
			return None

	def buildretr(self, cmd):
		try:
			filepath = cmd[1]
			msg = "%s %s\r\n" %(self.commands["retr"], filepath)
			self.socket.send(msg)
			self.socket.receive()
			filedata = self.datasocket.receive()
			with open(filepath, "w+") as openfile:
				openfile.write(filedata)

			self.socket.receive()
			return None

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("retr <path to file>")
			return None


	def buildstor(self, cmd):
		print "buildstor"

		try:
			filepath = cmd[1]
			msg = "%s %s\r\n" %(self.commands["stor"], filepath)

			# if not self.datasocket:
			# 	self.openconnection()

			content = ""

			with open(filepath, 'r') as openfile:
				content = openfile.read()
				print content

			self.socket.send(msg)
			self.socket.receive()
			self.datasocket.send(content)
			self.datasocket.close()
			self.socket.receive()

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("stor <path to file>")
			return None



	def evaulate(self, status, response):
		print "Status: %s" %status
		return {
			"login" : (self.promptusername, response),
			"125" : (self.openconnection, response),
			"150" : (self.openconnection, response),
			"220" : (self.promptusername, response),#220 FTP Server ready.
			"214" : (self.command,response), #214 The following commands are recognized:
			"221" : (self.exit, response),#221 Goodbye.
			"227" : (self.pasvmode, response),
			"226" : (self.command, response), #226 Transfer complete.
			"230" : (self.command, response), #230 Login successful.
			"228" : (self.command, response), #228 Entering Passive Mode
			"230" : (self.command, response), #230 Login Succesfuluthorized
			"250" : (self.command, response), #250 "/" is the current directory.
			"257" : (self.command, response), #257 "/" is the current directory.
			"331" : (self.promptpassword, response), #331 Username ok, send password.
			"332" : (self.command, response), #332 Need account for login.
			"421" : (self.exit, response), #421 Control connection timed out.
			"501" : (self.command,response), #501 Syntax error in parameters or arguments.
			"530" : (self.command, response), #530 Authentication failed.
			"550" : (self.command, response), #550 No such file or directory.
			}.get(status, (self.command, response)) #default just reprompt for command



class ClientSocket:
	def __init__(self, host=socket.gethostname(), filename="client.log" , port=21):
		self.host = host
		self.port = port
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log = logger(filename, "[client]")
		self.clientsocket.settimeout(5)
		self.datasocket = None

		try:
			self.clientsocket.connect((self.host, self.port))
			msg = "Connected to %s:%s" %(self.host, self.port)
			self.log.debug(msg)

		except socket.error as e:
			self.log.error(str(e))
			pass

	def close(self):
		self.clientsocket.close()


	def receive(self):
		response = ""
		try:

			message = self.clientsocket.recv(BUFFER)
			response += message

		except socket.error as error:
			pass
		if response:
			self.log.received(response)
		else:
			print "did not recieve anything"
		return response


	def send(self, command):
		try:
			self.log.sending(command)
			self.clientsocket.sendall(command)

		except struct.error as error:
			self.log.error(error)
			return False

	def acceptconnection(self):
		try:
			self.clientsocket.accept()
		except socket.timeout as error:
			pass


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
