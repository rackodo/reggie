import socket, sys, threading, readchar, string

class Client:
	def __init__(self, address, port, nick):
		self.address = address
		self.port = port
		self.nick = nick
		self.channel = "#rudechat"

		self._observers = []

		# Lifted from https://github.com/bl4de/irc-client/blob/master/irc_client_py3.py
		self.cmd = ""
		self.joined = False
		self.quitting = False
		
		clientThread = threading.Thread(target=self.Begin)
		clientThread.start()

	def Begin(self):
		self.connect()

		while (self.joined == False):
			resp = self.get_response()
			self.notify(resp.strip('\n'))
			if "No Ident response" in resp:
				self.updateNick()
				
			# we're accepted, let's join the channel
			if "376" in resp:
				self.join_channel()
			
			# username already in use? change with _ at the start
			if "433" in resp:
				self.nick = "_" + self.nick
				self.updateNick()
			
			# ping and pong
			if "PING" in resp:
				self.send_cmd("PONG", ":" + resp.split(":")[1])

			# we've joined
			if "366" in resp:
				self.joined = True

		respThread = threading.Thread(target=self.print_response)
		respThread.start()

	# KeyPress Observer
	def onKeyPress(self, key):
		if key == readchar.key.BACKSPACE:
			self.cmd = self.cmd[:-1]
		
		elif key == readchar.key.ENTER:
			if self.cmd == "/quit":
				self.send_cmd("QUIT", "Goodbye from Reggie!")

			elif self.cmd != "":
				self.send_message_to_channel({self.cmd})
				self.cmd = ""

		# If all else fails, this is probably a message...
		elif len(key) == 1 and (key in string.printable and (key not in string.whitespace or key == " ")) and key not in "\x0b\x0c":
			self.cmd += key
		
		else:
			pass

	# Utility
	def updateNick(self):
		self.send_cmd("NICK", self.nick)
		self.send_cmd("USER", "{} * * :{}".format(self.nick, self.nick))

	# Observer Code
	def attach(self, observer):
		self._observers.append(observer)

	def detach(self, observer):
		try:
			self._observers.remove(observer)
		except ValueError:
			pass

	def notify(self, data):
		for observer in self._observers:
			observer.onClientReceive(data)
	
	# Response Daemon
	def print_response(self):
		while True:
			resp = self.get_response()
			if resp:
				msg = resp.strip().split(":")
				self.notify("<{}> {}".format(msg[1].split("!")[0], msg[2].strip()))

	# Client Code
	def connect(self):
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((self.address, self.port))

	def get_response(self):
		return self.conn.recv(512).decode("utf-8")
	
	def send_cmd(self, cmd, message):
		command = "{} {}\r\n".format(cmd, message).encode("utf-8")
		self.conn.send(command)

	def send_message_to_channel(self, message):
		command = "PRIVMSG {}".format(self.channel)
		msg = ":" + list(message)[0]
		self.send_cmd(command, msg)
		self.notify("<{}> {}".format(self.nick, msg))

	def join_channel(self):
		cmd = "JOIN"
		channel = self.channel
		self.send_cmd(cmd, channel)