"""
Parser: local process
    Role: access the data queue locally
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
"""
import signal, time
from multiprocessing import Process, Queue, Event, Manager


class Parser(Process):

    def __init__(self, data, samples, rate):
        Process.__init__(self)
        self._importQ = data
        self._sample = samples
        self._rate = rate
        self._exportQ = Queue()
        self.count = 0
        self._exit = Event()

    def run(self):
        self.dequeue()

    def stop(self):
        self._exit.set()
        time.sleep(0.1)

    def add(self, data):
        self._importQ.put(data)

    def check_init(self):
        return self.name is not None

    def dequeue(self):
        while not self._importQ.empty():
            self._exportQ = self._importQ.get()







