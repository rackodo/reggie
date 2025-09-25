import time

class Clock:
	def __init__(self):
		self.fps = 20
		self._observers = []
	
	def attach(self, observer):
		self._observers.append(observer)

	def detach(self, observer):
		try:
			self._observers.remove(observer)
		except ValueError:
			pass

	def notify(self):
		for observer in self._observers:
			observer.onTick()

	def Tick(self):
		while True:
			self.notify()
			time.sleep(1/self.fps)