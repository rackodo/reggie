import shutil, os, time, threading, readchar, sys, string

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

		self.msg = ""

		self.appendToLog(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash.txt'),'rb').readlines())

	def appendToLog(self, feed):
		self.lines += [line.decode('unicode-escape').strip('\n') for line in feed]

	def draw(self): # Render the lines.
		while True:
			self.width = shutil.get_terminal_size()[0]
			self.height = shutil.get_terminal_size()[1] - 2

			sys.stdout.write("\033[H\033[J")

			if self.latched:
				self.offset = len(self.lines) - self.height
				if self.offset < 0:
					self.offset = 0

			for i in range(0, self.height):
				try:
					print(self.lines[i + self.offset])
				except IndexError:
					sys.stdout.write("\n")
			sys.stdout.write("-" * self.width)

			statusLeft = f"<{os.getlogin()}> {self.msg}"
			statusRight = "Latched" if self.latched else f"{self.offset}/{len(self.lines)}"

			space_count = max(0, self.width - len(statusLeft) - len(statusRight))
			statusBar = statusLeft + (" " * space_count) + statusRight

			sys.stdout.write(statusBar)
			sys.stdout.flush()
			time.sleep(1/self.fps)

	def KeyEventManager(self): # 
		while True:
			try:
				key = readchar.readkey()

				# Arrow Key Navigation
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
							if self.offset < 0:
								self.offset = 0
							self.latched = True

				elif key == readchar.key.BACKSPACE:
					self.msg = self.msg[:-1]
				
				elif key == readchar.key.ENTER:
					if self.msg != "":
						self.lines.append(f"<{os.getlogin()}> {self.msg}")
						self.msg = ""

				# If all else fails, this is probably a message...
				elif len(key) == 1 and (key in string.printable and (key not in string.whitespace or key == " ")) and key not in "\x0b\x0c":
					self.msg += key
			except AttributeError:
				pass

def main():
	reg = Reggie()

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