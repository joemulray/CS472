#!/usr/bin/env python

#default imports
import socket
import struct
import sys, os


# logging class
from logging import logger

"""
Joseph Mulray
CS472 - Computer Networks
Fall 2018-2019
Homework Assignment #2

	Implement a FTP (File Transfer Protocol) client that can login, list
	directory information, and store and retrieve information from a server hosting the FTP service.
"""

BUFFER  = 4024

class FTP:
	"""
	FTP encapsulates the sending and recieving of tcp data from a socket.

	Attributes:
		socket 		The ClientSocket to handle recieving and sending data
		ftplop 		The logging object used to display and log to file
		username	The username of the ftp client
		password 	The password of the ftp client
		__authorized 	The status of authorization of the tcp connection
		action 		The commands that require action {input/parsing} before {sending/recieving}
		commands 	The available commands and their ftp command

	"""
	def __init__(self, socket=None, username="root", password="password"):
		"""
		:param socket: inputs a clientsocket that handles the sending and recieving of data
		:param username: inputs the username inputed for the ftp connection
		:param password: inputs the password the the ftp user
		:type socket: ClientSocket
		:type username: string
		:type password: string

		:return: returns nothing
		"""
		self.socket = socket
		self.ftplog = socket.log
		self.username = username
		self.password = password
		self.__authorized = False
		self.port = 20
		self.action = { "login" : self.username, "port" : self.buildport, "eprt" : self.buildeprt, \
					"retr" : self.buildretr, "stor" : self.buildstor, "list" : self.buildlist, \
					"epsv" : self.buildepsv }
		self.commands = {
					"user" : "USER", "quit" : "QUIT", "pasv" : "PASV", \
					"epsv" : "EPSV", "port" : "PORT",  "cd" : "CWD", \
					"eprt" : "EPRT", "retr" : "RETR", "stor" : "STOR", \
					"syst" : "SYST", "ls" : "LIST", "pwd" : "PWD", \
					"help" : "HELP", "pass" : "PASS" \
					}


	def doProtocol(self):
		"""		
		Runs a continuous protocol and evaluates the return status

		:return: returns nothing
		"""
		while True:
			response = self.socket.receive()
			(function, response) = self.evaulate(response[:3], response)
			function(response)


	def command(self, response=None):
		"""
		Runs a command given that the command is in available commands and evaluates action
		from there

		:param response: the response from the clientsocket
		:returns: command, action, self
		"""


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
		"""
		Prompts username from stdin for ftp client

		:param response: the response from the clientsocket
		:return: returns nothing
		"""
		user = "USER " + raw_input("ftp> Name: ") + "\r\n"
		self.username = user
		self.socket.send(self.username)


	def promptpassword(self, response=None):
		"""
		Prompts password from stdin from ftp client
		
		:param response: the response from the clientsocket
		:return: returns nothing
		"""
		password = "PASS " + raw_input("ftp> Password: ") + "\r\n"
		self.password = password
		self.socket.send(self.password)


	def openconnection(self, response=None):
		"""
		Opens a connection to the datasocket for the clientsocket

		:param response: the response from the clientsocket
		:return: returns nothing
		"""
		if not self.socket.datasocket:
			"""Creates a datasocket with definded port {default 20} if none exist"""
			self.socket.datasocket = ClientSocket(sys.argv[1], sys.argv[2], self.port)


	def dataconnection(self):
		if not self.socket.datasocket:
			self.ftplog.debug("Received: 425 Use PORT or PASV first.")
			return False
		else:
			return True


	def pasvmode(self, response):
		"""
		Passive mode parses the response from the server, and establishes a new ftp dataconnection

		:param response: the response from the clientsocket
		:return: returns nothing
		"""
		try:
			#parse p1, p2 convert to port
			pasv = response[26:].translate(None, "().\r\n").split(",")
			p1 = int(pasv[-2])
			p2 = int(pasv[-1])

			port = (p1 * 256) + p2
			self.port = port

		except Exception as error:
			self.ftplog.error(error)

		#establish a new connection
		self.socket.datasocket = None
		self.openconnection()
		self.command()

	def exit(self, response):
		"""
		Exits the program and closes the logging file

		:param response: returns the response from the clientsocket
		:return: returns nothing
		"""

		self.ftplog.close()
		exit(0)


	def buildcmd(self, cmd):
		"""
		Helper function to build the commands from stdin

		:param cmd: the stdin input from user
		:type cmd: array
		:return: returns string message to send to server
		"""

		key = cmd[0]
		cmd.pop(0)

		#build msg string
		msg = self.commands[key]
		for param in cmd:
			msg = msg + " " + param

		msg = msg + "\r\n"
		return msg



	def buildepsv(self, cmd):
		"""
		Function to build the epsv command

		:param cmd: the stdin input from user
		:type cmd: array
		:return: returns nothing
		"""
		try:
			msg = self.commands["epsv"] + "\r\n"
			self.socket.send(msg)
			response = self.socket.receive()
			port = response[35:].translate(None, "().|\r\n")
			self.port = int(port)
			self.openconnection()


		except Exception as error:
			self.ftplog.error(error)
			return None


	def buildport(self, cmd):
		"""
		Port commmand to send to ftp server inputs a port from stdin

		:param cmd: the stdin input from user
		:type cmd: array
		:returns: msg {PORT 63421}, None

		"""
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
		"""
		EPRT command to send to the ftp server port from user and builds msg object

		:param cmd: the stdin input from user
		:type cmd: array
		:return: returns msg object

		"""
		try:
			port = cmd[1]
			host = self.socket.host
			msg = "%s |%s|%s|%s|\r\n" %(self.commands["eprt"], 1, host, port)

			return msg

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("eprt <port>")
			return None


	def buildlist(self, cmd):
		"""
		List command to send to ftp server checks if datasocket exists

		:param cmd: the stdin input from user
		:type cmd: array
		:return: returns nothing
		"""
		try:
			if not self.dataconnection():
				return

			msg = "%s\r\n" %(self.commands["list"])
			self.socket.send(msg)
			self.socket.receive()

			self.socket.datasocket.close()
			self.socket.datasocket = None

		except Exception as error:
			self.ftplog.error(error)
			return None


	def buildretr(self, cmd):
		"""
		RETR command to retrieve file from the ftp server {retr <path to file> <(optional) path to filename>}

		:param cmd: the stdin input from user
		:type cmd: array
		:return: returns nothing
		"""

		try:

			if not self.dataconnection():
				return

			filepath = cmd[1]
			if len(cmd) > 2:
				file = cmd[2]
			else:
				file = os.path.basename(filepath)

			msg = "%s %s\r\n" %(self.commands["retr"], filepath)
			self.socket.send(msg)
			(response, filedata) = self.socket.receive()

			if not filedata:
				filedata = ""

			with open(file, "w+") as openfile:
				openfile.write(filedata)

			#close the datasocket
			self.socket.datasocket.close()
			self.socket.datasocket = None

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("retr <path to file> < (optional) path to filename>")
			return None


	def buildstor(self, cmd):
		"""
		STOR command to stor file from the ftp server {stor <path to file> <file destination>}
		
		:param cmd: the stdin input from user
		:type cmd: array
		:return: returns nothing
		"""

		try:

			if not self.dataconnection():
				return

			filepath = cmd[1]
			
			#handle default input if path is not specified 
			if len(cmd) > 2:
				destination = cmd[2]
			else:
				destination = cmd[1]

			msg = "%s %s\r\n" %(self.commands["stor"], destination)

			content = ""

			with open(filepath, 'r') as openfile:
				content = openfile.read()

			self.socket.send(msg)
			repsonse = self.socket.receive(True, content)
			self.socket.datasocket.close()
			self.socket.datasocket = None

		except Exception as error:
			self.ftplog.error(error)
			self.ftplog.usage("stor <path to file> <file destination>")
			return None



	def evaulate(self, status, response):
		"""
		Returns the correct function based on the status returned from the server

		:param status: the status of the response from the ftp server {125, 229, 501}
		:param response: the full response from the ftp server
		:returns: correct function based on status
		"""
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
			"229" : (self.command, response),
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
	"""
	ClientSocket encapsulates the handling of recieving and sending data by the ftp client

	Attributes:
		host 		The sepcified host of the server to connect to
		port 		The specified port of teh server to connect to
		clientsocket The socket object used to accept and connect
		log 		The logging object to debug and highlight errors
		datasocket	The socket to transport data from the client to the server {vise versa}
	"""
	def __init__(self, host=socket.gethostname(), filename="client.log" , port=21):

		self.host = host
		self.port = port
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log = logger(filename, "[client]")
		self.clientsocket.settimeout(2)
		self.datasocket = None
		
		"""
		Establishes a connection otherwise exists the program
		"""
		try:
			self.clientsocket.connect((self.host, self.port))
			msg = "Connected to %s:%s" %(self.host, self.port)
			self.log.debug(msg)

		except socket.error as e:
			self.log.error(str(e))
			exit(0)
			pass

	def close(self):
		"""
		Closes the clientsocket connection

		:return: returns nothing
		"""
		self.clientsocket.close()


	def receive(self, debug=True, senddata=None):
		"""
		Function to recieve data from the server, some data requires opening a dataconnection and handling of that

		:param debug: to display debug or standard logs, used in the case datasocket, dont want to be displaying wrong logs
		:param senddata: data read from a file to be send when the server opens a dataconnection
		:type debug: boolean
		:type senddata: string
		:return: returns the response from the server, data if any.
		"""
		response = ""
		dataconnection = False
		try:
			#loop until breaking otherwise will not get all the data if buffer is full
			while True:

				message = self.clientsocket.recv(BUFFER)
				if message and debug:
					self.log.received(message)
				elif message and not debug:
					self.log.log(message)

				#handle for dataconnections needed
				if message[:3] == "150" or message[:3] == "125":
					dataconnection=True
					data = None

					#if there was no datasocket available ftp server not handling for this
					if not self.datasocket:
						msg = "425 Use PORT or PASV first."
						self.log.received(msg)
						return msg

					#if client needs to send data
					if senddata:
						data = self.datasocket.send(senddata)
					else:
						data = self.datasocket.datareceive()

				response += message

				if not message:
					break

		except socket.error as error:
			pass
		
		if dataconnection:
			return message, data

		return response


	def datareceive(self):
		"""
		Helper function for the datasocket to recieve `data` from the server
		do not want debug messages everytime buffer gets full

		:return: returns response from the datasocket
		"""

		response = ""
		try:
			while True:
				message = self.clientsocket.recv(BUFFER)
				
				if not message:
					break
				response += message
				self.log.log(message)

			return response

		except socket.error as error:
			pass


	def send(self, command):
		"""
		Fucntion to send command through the clientsocket

		:param command: command object {msg string from the ftp class}
		:return: returns nothing
		"""

		try:
			self.log.sending(command)
			self.clientsocket.sendall(command)
			return True

		except socket.error as error:
			self.log.error(error)
			return False

	def acceptconnection(self):
		"""
		Accepts a connection to the clientsocket

		:return: returns nothing
		"""
		try:
			self.clientsocket.accept()
		except socket.timeout as error:
			pass


	def connected(self):
		"""
		Helper function to check the status of the clientsocket

		:return: returns boolean on status of the clientsocket
		"""
		if self.clientsocket:
			return True
		else:
			return False

def main():
	"""
	MAIN function, passes command line arguments into Clientsocket object and runs the ftp protocol

	:return: returns nothing:
	"""
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
	#execute main function
	main()
