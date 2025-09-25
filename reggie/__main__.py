from reggie.renderer import Renderer
from reggie.input import Input
import sys, threading, os

def main():
	ren = Renderer()

	ren.AddText(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash.txt'),'rb').readlines())

	inp = Input()
	
	inp.attach(ren)

	inputThread = threading.Thread(
		target=inp.Watch
	)
	inputThread.start()
	inputThread.join()

if __name__ == '__main__':
	sys.exit(main())