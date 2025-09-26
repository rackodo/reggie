import shutil, sys, readchar, string, os, threading, textwrap
from wcwidth import wcswidth

def wrap_line(line, width):
    wrapped = []
    buf = ""
    for ch in line:
        if wcswidth(buf + ch) > width - 1:
            wrapped.append(buf)
            buf = ch
        else:
            buf += ch
    if buf:
        wrapped.append(buf)
    return wrapped

class Renderer:
	def __init__(self, queue):
		self.queue = queue

		self.width, self.height = shutil.get_terminal_size()
		self.history = []
		self.prettyHistory = []
		self.scrollPosition = 0
		self.latched = True
		self.fps = 30

		self.statusContentLeft = ""
		self.statusContentRight = ""

		# Clear Console
		sys.stdout.write("\033[H\033[J")

		self.DoSplash()

		sizeThread = threading.Thread(
			target=self.adjustSize
		)
		sizeThread.start()

		self.DrawFeed()

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
				if self.scrollPosition > len(self.prettyHistory) - self.height:
					self.scrollPosition = len(self.prettyHistory) - self.height
					if self.scrollPosition < 0:
						self.scrollPosition = 0
					self.latched = True
			self.DrawFeed()

		self.DrawStatusBar()

	def onClientReceive(self, data):
		self.history.append(data)
		self.onFeedUpdated()

	def onFeedUpdated(self):
		self.DrawFeed()

	def DoSplash(self):
		splash = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash.txt'),'rb').readlines()
		self.history += [line.decode('unicode-escape') for line in splash]

	def AddText(self, text):
		self.history.append(text)
		
		self.DrawFeed()

	def DrawFeed(self):
		self.prettyHistory = []

		for line in self.history:
			line = line.lstrip(":")
			pLines = line.split(":")
			try:
				l = "".join(pLines[x] for x in range(1, len(pLines)))
				self.prettyHistory.extend(wrap_line(l, self.width - 1))
				self.prettyHistory.append("\n")
			except IndexError:
				self.prettyHistory.extend(wrap_line(line, self.width - 1))

		if self.latched:
			self.scrollPosition = len(self.prettyHistory) - (self.height - 2)
		if self.scrollPosition < 0:
			self.scrollPosition = 0

		# Loop over lines in the history, from the scroll position to that plus the height of the console... minus 2, to make room for the status bar
		buffer = []
		for i in range(0, self.height - 2):
			try:
				buffer.append(self.prettyHistory[i + self.scrollPosition].ljust(self.width))
			except IndexError:
				buffer.append(" " * self.width)

		feed = "".join(
			f"\033[{i+1};0H{row}" for i, row in enumerate(buffer)
		)
		sys.stdout.write(feed)
		
		self.DrawStatusBar()

	def DrawStatusBar(self):
		# Draw Spacer
		buffer = []

		buffer.append("-" * self.width)

		# Draw Status bar
		self.statusContentLeft = f"<{os.getlogin()}>"
		self.statusContentRight = "Latched" if self.latched else f"{self.scrollPosition}/{len(self.prettyHistory)}"

		spaceCount = max(0, self.width - len(self.statusContentLeft) - len(self.statusContentRight))

		buffer.append(self.statusContentLeft + (" " * spaceCount) + self.statusContentRight)

		bar = "".join(
			f"\033[{(self.height - 2) + i + 1};0H{row}" for i, row in enumerate(buffer)
		)

		sys.stdout.write(bar)
		sys.stdout.write(f"\033[{self.height};{len(self.statusContentLeft) + 2}H")
		sys.stdout.flush()