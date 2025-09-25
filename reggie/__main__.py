import shutil, os, time, threading, readchar, sys

class Reggie:
	def __init__(self):
		'''
		Reggie. Text-based IRC client (hopefully)
		'''
		self.width = shutil.get_terminal_size()[0]
		self.height = shutil.get_terminal_size()[1] - 2
		self.lines = []
		self.offset = 0
		self.latched = True
		self.fps = 30

		self.appendToLog(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash.txt'),'rb').readlines())

		self.cnt = 0

	def appendToLog(self, feed):
		self.lines += [line.decode('unicode-escape').strip('\n') for line in feed]

	def draw(self): # Render the lines.
		while True:
			sys.stdout.write("\033[H\033[J")

			for i in range(0, self.height):
				try:
					print(self.lines[i + self.offset])
				except IndexError:
					print("")
			sys.stdout.write("-" * self.width)

			statusLeft = f"{self.offset}/{len(self.lines)}"
			statusRight = "Latched" if self.latched else "Unlatched"

			space_count = max(0, self.width - len(statusLeft) - len(statusRight))
			statusBar = statusLeft + (" " * space_count) + statusRight

			sys.stdout.write(statusBar)
			sys.stdout.flush()
			time.sleep(1/self.fps)

	def KeyEventManager(self): # 
		while True:
			try:
				key = readchar.readkey()
				if key == readchar.key.UP:
					self.offset -= 1
					if self.latched:
						self.latched = False
					if self.offset < 0:
						self.offset = 0
				elif key == readchar.key.DOWN:
					if self.latched:
						pass
					else:
						self.offset += 1
						if self.offset > len(self.lines) - self.height:
							self.offset = len(self.lines) - self.height
							self.latched = True
			except AttributeError:
				pass

	def increment(self): # Stand-in function to populate the lines array. This won't stay.
		while True:
			self.lines.append(str(self.cnt))
			time.sleep(1/10)
			self.cnt += 1

			if self.latched:
				self.offset = len(self.lines) - self.height + 1
				if self.offset < 0:
					self.offset = 0

def main():
	reg = Reggie()

	drawer = threading.Thread(
		target=reg.draw,
		name="Renderer")
	drawer.start()

	adder = threading.Thread(
		target=reg.increment,
		name="Incrementer")
	adder.start()

	input = threading.Thread(
		target=reg.KeyEventManager,
		name="Input"
	)
	input.start()
	input.join()

if __name__ == '__main__':
	sys.exit(main())