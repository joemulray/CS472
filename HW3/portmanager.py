class PortManager:
	def __init__(self):
		self.ports = []

	def exists(self, port):
		return True if port in self.ports else False

	def addport(self, port):
		self.ports.append(port)

