import readchar

class Input:
	def __init__(self, queue):
		self.queue = queue

	def Watch(self):
		while True:
			try:
				key = readchar.readkey()
				self.queue.put(("keypress", key))
			except AttributeError:
				pass