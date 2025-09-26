from reggie.renderer import Renderer
from reggie.input import Input
from reggie.client import Client
import sys, threading, os

def main():
	ren = Renderer()

	inp = Input()
	inp.attach(ren)

	cli = Client('irc.libera.chat', 6667, 'reggieIrcTest')
	cli.attach(ren)

	inp.attach(cli)

	inputThread = threading.Thread(
		target=inp.Watch
	)
	inputThread.start()
	inputThread.join()

if __name__ == '__main__':
	sys.exit(main())