"""
Worker: local process
    Role: connect between data computation process and data parsing process
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
"""
from multiprocessing import Lock
from helper.parser import *
from helper.ringBuffer import *
from processes.simulator import *
from processes.serial import *


class Worker(Process):

    def __init__(self, graph_id=None, samples=500, rate=0.2, lock=None, port=None):
        Process.__init__(self)
        self._graphid = graph_id
        self._samples = samples
        self._rate = rate
        self._lock = lock
        self._port = port

        self._process = None
        self._parser = None

        self._queue = Queue()
        self._xbuffer = RingBuffer(samples)
        self._ybuffer = RingBuffer(samples)

    def run(self):
        self.clearqueue()
        self._lock.acquire()
        self._parser = Parser(data=self._queue,
                              samples=self._samples,
                              rate=self._rate)
        if self._graphid == 0:
            self._process = RandomSimulator(self._parser)
        elif self._graphid == 1:
            self._process = SineSimulator(self._parser)
        elif self._graphid == 2:
            self._process = Serial(self._parser)
        if self._process.check_init() and self._parser.check_init():
            self._parser.start()
            self._process.start()
        self._lock.release()


    def stop(self):
        self.get_plot_value()
        for process in [self._process, self._parser]:
            if process is not None and process.is_alive():
                process.stop()
                process.join(1000)

    def get_plot_value(self):
        while not self._queue.empty():
            self.distribute_values(self._queue.get(False))


    def distribute_values(self, data):
        self._xbuffer.append(data[0])
        self._ybuffer.append(data[1])

    def getxbuffer(self):
        return self._xbuffer.get_all()

    def getybuffer(self):
        return self._ybuffer.get_all()

    def clearqueue(self):
        self._xbuffer = RingBuffer(self._samples)
        self._ybuffer = RingBuffer(self._samples)
        while not self._queue.empty():
            self._queue.get()



