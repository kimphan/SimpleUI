"""
Simulator: local process
    Role: data computation for Sine Wave graph and Random number graph
        Plot: y = A sin(wt)
            A-amplitude
            w-frequency
            t-time
        Plot: y = x
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
"""
from multiprocessing import Process, Queue, Event
from time import time, sleep
import signal
import numpy as np


class SineSimulator(Process):

    # Constructor
    def __init__(self, parser):
        Process.__init__(self)
        self._parser = parser
        self._exit = None
        self._speed = None


    def run(self):
        t = time()
        while not self._exit.is_set():
            x = time() - t
            y = np.sin(x)
            self._parser.add([x, y])
            sleep(self._speed)

    def check_init(self, port=None, speed=0.2):
        if self.name is not None:
            self._exit = Event()
            self._speed = speed
            return True
        else:
            return False

    def stop(self):
        self._exit.set()
        time.sleep(0.1)


class RandomSimulator(Process):

    # Constructor
    def __init__(self, parser):
        Process.__init__(self)
        self._parser = parser
        self._speed = None
        self._exit = Event()

    def run(self):
        t = time()
        while not self._exit.is_set():
            x = time() - t
            y = x
            self._parser.add([x, y])
            sleep(0.2)

    def check_init(self, port=None, speed=0.2):
        if self.name is not None:
            self._exit = Event()
            self._speed = speed
            return True
        else:
            return False

    def stop(self):
        self._exit.set()
        time.sleep(0.1)





