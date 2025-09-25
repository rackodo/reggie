import shutil, sys, readchar, string, os

class Renderer:
	def __init__(self):
		self.width, self.height = shutil.get_terminal_size()
		self.history = []
		self.scrollPosition = 0
		self.latched = True
		self.fps = 30

		self.msg = ""

		self.statusContentLeft = ""
		self.statusContentRight = ""

	def onTick(self):
		self.Draw()

	def onKeyPress(self, key):
		# Arrow Key Navigation
		if key == readchar.key.UP:
			self.scrollPosition -= 1
			if self.latched:
				self.latched = False
			if self.scrollPosition < 0:
				self.scrollPosition = 0
		elif key == readchar.key.DOWN:
			if self.latched:
				pass
			else:
				self.scrollPosition += 1
				if self.scrollPosition > len(self.history) - (self.height - 2):
					self.scrollPosition = len(self.history) - self.height
					if self.scrollPosition < 0:
						self.scrollPosition = 0
					self.latched = True

		elif key == readchar.key.BACKSPACE:
			self.msg = self.msg[:-1]
		
		elif key == readchar.key.ENTER:
			if self.msg != "":
				self.history.append(f"<{os.getlogin()}> {self.msg}")
				self.msg = ""

		# If all else fails, this is probably a message...
		elif len(key) == 1 and (key in string.printable and (key not in string.whitespace or key == " ")) and key not in "\x0b\x0c":
			self.msg += key

	def AddText(self, text):
		self.history += [line.decode('unicode-escape').strip('\n') for line in text]

	def Draw(self):
		self.width, self.height = shutil.get_terminal_size()

		if self.latched:
			self.scrollPosition = len(self.history) - (self.height - 2)
		if self.scrollPosition < 0:
			self.scrollPosition = 0

		# Clear Console
		sys.stdout.write("\033[H\033[J")

		# Loop over lines in the history, from the scroll position to that plus the height of the console... minus 2, to make room for the status bar
		for i in range(0, self.height - 2):
			try:
				print(self.history[i + self.scrollPosition])
			except IndexError:
				sys.stdout.write("\n")

		# Draw Spacer
		sys.stdout.write("-" * self.width)

		# Draw Status bar
		self.statusContentLeft = f"<{os.getlogin()}> {self.msg}"
		self.statusContentRight = "Latched" if self.latched else f"{self.scrollPosition}/{len(self.history)}"

		spaceCount = max(0, self.width - len(self.statusContentLeft) - len(self.statusContentRight))
		sys.stdout.write(self.statusContentLeft + (" " * spaceCount) + self.statusContentRight)
		sys.stdout.write(f"\033[{self.height};{len(self.statusContentLeft) + 1}H")

		sys.stdout.flush()