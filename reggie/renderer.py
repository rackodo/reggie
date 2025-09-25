import shutil, sys, readchar, string, os, threading, textwrap

class Renderer:
	def __init__(self):
		self.width, self.height = shutil.get_terminal_size()
		self.history = []
		self.scrollPosition = 0
		self.latched = True
		self.fps = 30

		self.statusContentLeft = ""
		self.statusContentRight = ""

		self.msg = ""

		# Clear Console
		sys.stdout.write("\033[H\033[J")

		sizeThread = threading.Thread(
			target=self.adjustSize
		)
		sizeThread.start()

	def adjustSize(self):
		while True:
			newWidth, newHeight = shutil.get_terminal_size()
			if (self.width, self.height) != (newWidth, newHeight):
				self.width, self.height = newWidth, newHeight
				self.DrawFeed()
				self.DrawStatusBar()

	def onKeyPress(self, key):
		# Arrow Key Navigation
		if key == readchar.key.UP:
			self.scrollPosition -= 1
			if self.latched:
				self.latched = False
			if self.scrollPosition < 0:
				self.scrollPosition = 0
				pass
			self.DrawFeed()
		elif key == readchar.key.DOWN:
			if self.latched:
				pass
			else:
				self.scrollPosition += 1
				if self.scrollPosition > len(self.history) - (self.height - 1):
					self.scrollPosition = len(self.history) - self.height - 1
					if self.scrollPosition < 0:
						self.scrollPosition = 0
					self.latched = True
			self.DrawFeed()

		elif key == readchar.key.BACKSPACE:
			self.msg = self.msg[:-1]
		
		elif key == readchar.key.ENTER:
			if self.msg != "":
				self.AddText(f"<{os.getlogin()}> {self.msg}")
				self.msg = ""

		# If all else fails, this is probably a message...
		elif len(key) == 1 and (key in string.printable and (key not in string.whitespace or key == " ")) and key not in "\x0b\x0c":
			self.msg += key
		
		self.DrawStatusBar()

	def onFeedUpdated(self):
		self.DrawFeed()

	def AddText(self, text):
		try:
			self.history += [line.decode('unicode-escape').strip('\n') for line in text]
		except AttributeError:
			if type(text) == str:
				self.history.append(text)
			if type(text) == list:
				self.history += [line for line in text]
		
		self.onFeedUpdated()

	def DrawFeed(self):
		prettyHistory = []

		for line in self.history:
			prettyHistory += [line[i:i+self.width] for i in range(0, len(line), self.width)]

		if self.latched:
			self.scrollPosition = len(prettyHistory) - (self.height - 2)
		if self.scrollPosition < 0:
			self.scrollPosition = 0

		# Loop over lines in the history, from the scroll position to that plus the height of the console... minus 2, to make room for the status bar
		for i in range(0, self.height - 2):
			try:
				sys.stdout.write(f"\033[{i + 1};0H")
				sys.stdout.write(f"{prettyHistory[i + self.scrollPosition]}".ljust(self.width))
			except IndexError:
				sys.stdout.write(f" " * self.width)
		
		self.DrawStatusBar()

	def DrawStatusBar(self):
		# Draw Spacer
		sys.stdout.write(f"\033[{self.height - 1};0H")
		sys.stdout.write("-" * self.width)

		# Draw Status bar
		self.statusContentLeft = f"<{os.getlogin()}> {self.msg}"
		self.statusContentRight = "Latched" if self.latched else f"{self.scrollPosition}/{len(self.history)}"

		spaceCount = max(0, self.width - len(self.statusContentLeft) - len(self.statusContentRight))

		sys.stdout.write(f"\033[{self.height};0H")
		sys.stdout.write(self.statusContentLeft + (" " * spaceCount) + self.statusContentRight)
		sys.stdout.write(f"\033[{self.height};{len(self.statusContentLeft) + 1}H")

		sys.stdout.flush()