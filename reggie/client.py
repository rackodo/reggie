import socket, sys, threading, readchar, string, irctokens

class Client:
	def __init__(self, queue, address, port, nick):
		self.queue = queue

		self.address = address
		self.port = port
		self.nick = nick
		self.channel = "##reggie"

		# Lifted from https://github.com/bl4de/irc-client/blob/master/irc_client_py3.py
		self.cmd = ""
		self.buffer = ""
		
		clientThread = threading.Thread(target=self.Begin)
		clientThread.start()

	def Begin(self):
		self.connect()

		respThread = threading.Thread(target=self.serverMessageDaemon)
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
		self.queue.put(("nick", self.nick))

	def serverMessageHandler(self, message):
		tokens = irctokens.tokenise(message.strip())

		if "*** No Ident response" in tokens.params:
			self.updateNick()
			
		# we're accepted, let's join the channel
		if tokens.command == "376":
			self.join_channel()
		
		# username already in use? change with _ at the start
		if tokens.command == "433":
			self.nick = "_" + self.nick
			self.updateNick()
		
		# ping and pong
		if tokens.command == "PING":
			self.send_cmd("PONG", ":" + message.split(":")[1])

		self.queue.put(("message", message.strip()))

	# Response Daemon
	def serverMessageDaemon(self):
		while True:
			resp = self.get_response()
			if not resp:
				break
			self.buffer += resp.decode('utf-8')

			while '\r\n' in self.buffer:
				line, self.buffer = self.buffer.split('\r\n', 1)
				self.serverMessageHandler(line)

	# Client Code
	def connect(self):
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((self.address, self.port))

	def get_response(self):
		return self.conn.recv(4096)
	
	def send_cmd(self, cmd, message):
		command = "{} {}\r\n".format(cmd, message).encode("utf-8")
		self.conn.send(command)

	def send_message_to_channel(self, message):
		command = "PRIVMSG {}".format(self.channel)
		msg = ":" + list(message)[0]
		self.send_cmd(command, msg)
		# self.queue.put(("message", "<{}> {}".format(self.nick, msg)))

	def join_channel(self):
		cmd = "JOIN"
		channel = self.channel
		self.send_cmd(cmd, channel)