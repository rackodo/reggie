import readchar

class Input:
	def __init__(self):
		self._observers = []

	def attach(self, observer):
		self._observers.append(observer)

	def detach(self, observer):
		try:
			self._observers.remove(observer)
		except ValueError:
			pass

	def notify(self, key):
		for observer in self._observers:
			observer.onKeyPress(key)

	def Watch(self):
		while True:
			try:
				self.notify(readchar.readkey())
			except AttributeError:
				pass