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
import multiprocessing as mp
from time import time, sleep
import numpy as np


class SineSimulator(mp.Process):

    # Constructor
    def __init__(self, parser):
        mp.Process.__init__(self)
        self._parser = parser
        self._exit = mp.Event()
        self._period = None

    def run(self):
        t1 = time()
        w = 2 * np.pi / self._period
        while not self._exit.is_set():
            t = time() - t1
            sint = np.sin(w*t)
            cost = np.cos(w*t)
            self._parser.add([t, str('{},{}\r\n'.format(sint, cost)).encode("utf-8")])
            sleep(self._period)

    def check_init(self, port, speed):
        if self.name is not None:
            self._period = speed
            return True
        else:
            return False

    def stop(self):
        self._exit.set()

class RandomSimulator(mp.Process):

    # Constructor
    def __init__(self, parser):
        mp.Process.__init__(self)
        self._parser = parser
        self._speed = None
        self._exit = mp.Event()

    def run(self):
        t = time()
        while not self._exit.is_set():
            x = time() - t
            y = x / self._speed
            self._parser.add([x, str('{}\r\n'.format(y)).encode("utf-8")])
            sleep(self._speed)

    def check_init(self, port, speed):
        if self.name is not None:
            self._speed = speed
            return True
        else:
            return False

    def stop(self):
        self._exit.set()






