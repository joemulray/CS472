import random

class PortManager:
	def __init__(self):
		self.ports = []
		self.lowerbound = 1024
		self.upperbound = 65535

	def exists(self, port):
		return True if port in self.ports else False

	def addport(self, port):
		self.ports.append(port)

	def getport(self):
		port = random.randint(self.lowerbound, self.upperbound)
		while port in self.ports:
			port = random.randint(self.lowerbound, self.upperbound)

		self.ports.append(port)
		return port

	def removeport(self, port):
		self.ports.remove(port)
