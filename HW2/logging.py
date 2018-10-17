#!/usr/bin/env python

"""
Logger class for client and server
"""

import datetime

class logger:
	def __init__(self, filename, service=None, format="%Y-%m-%d %H:%M"):
		self.file = open(filename, 'w+')
		self.service = service
		self.format = format
		self.debugmsg = "[debug]"
		self.errormsg = "[ERROR]"
		self.timestamp = self.time()

	def debug(self,msg):
		log = "%s : %s %s : %s" %(self.timestamp, self.service, self.debugmsg, str(msg))
		print log
		self.file.write(log + "\n")

	def error(self,msg):
		log = "%s : %s %s : %s" %(self.timestamp, self.service, self.errormsg, str(msg))
		print log
		self.file.write(log + "\n")

	def time(self):
		timenow = datetime.datetime.now()
		return timenow.strftime(self.format)

	def sending(self, value):
		self.debug("Sent: " + str(value))

	def received(self, value):
		self.debug("Received: " + str(value))
