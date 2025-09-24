import shutil, os, time, threading, readchar, sys

class Reggie:
	def __init__(self):
		'''
		Reggie. Text-based IRC client (hopefully)
		'''
		self.height = shutil.get_terminal_size()[1] - 1
		self.lines = []
		self.offset = 0
		self.latched = True
		self.cnt = 0
		self.fps = 30

	def draw(self): # Render the lines.
		while True:
			os.system('cls' if os.system == 'nt' else 'clear')

			for i in range(0, self.height):
				try:
					print(self.lines[i + self.offset])
				except IndexError:
					print("")
			print(self.latched, end='')
			time.sleep(1/self.fps)

	def KeyEventManager(self): # 
		while True:
			try:
				key = readchar.readkey()
				print(key)
				if key == readchar.key.UP:
					self.offset -= 1
					if self.latched:
						self.latched = False
					if self.offset < 0:
						self.offset = 0
				elif key == readchar.key.DOWN:
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
				self.offset = len(self.lines) - self.height
				if self.offset < 0:
					self.offset = 0

def main():
	reg = Reggie()

	adder = threading.Thread(
		target=reg.increment,
		name="Incrementer")
	adder.start()

	drawer = threading.Thread(
		target=reg.draw,
		name="Renderer")
	drawer.start()

	input = threading.Thread(
		target=reg.KeyEventManager,
		name="Input"
	)
	input.start()
	input.join()

if __name__ == '__main__':
	sys.exit(main())