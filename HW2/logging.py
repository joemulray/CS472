#!/usr/bin/env python

"""
Logger class for client and server
"""

import os
import datetime

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

		#if file does not exist
		if not os.path.exists(filename):
			mode = "w+"
		else:
			mode = "w+"
		self.file = open(filename, 'a')
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
		self.file.flush()

	def error(self,msg):
		"""
		Display/write errors messages to file or stdout

		:param msg: The message to be logged
		:return: returns nothing
		"""
		log = "%s : %s %s : %s" %(self.timestamp, self.service, self.errormsg, str(msg).rstrip())
		print log
		self.file.write(log + "\n")
		self.file.flush()


	def usage(self, msg):
		log =  "Usage: %s" %msg
		print log

	def log(self, msg):
		log = "%s" %msg
		print log.strip()
		self.file.write(log)
		self.file.flush()


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