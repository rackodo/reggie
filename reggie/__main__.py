import queue, threading, time, sys
from reggie.renderer import Renderer
from reggie.input import Input
from reggie.client import Client

eQueue = queue.Queue()

def main():
	ren = Renderer(eQueue)
	inp = Input(eQueue)
	cli = Client(eQueue, 'irc.libera.chat', 6667, 'reggie')

	inputThread = threading.Thread(
		target=inp.Watch,
		daemon=True
	)
	inputThread.start()

	fps = 20
	while True:
		try:
			while True:
				event_type, data = eQueue.get_nowait()
				if event_type == "keypress":
					ren.onKeyPress(data)
					cli.onKeyPress(data)
				elif event_type == "message":
					ren.onClientReceive(data)
		except queue.Empty:
			pass

		time.sleep(1/fps)

if __name__ == '__main__':
	sys.exit(main())