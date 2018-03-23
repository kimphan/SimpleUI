"""
Worker: local process
    Role: connect between data computation process and data parsing process
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
        Signal handler: https://docs.python.org/3/library/signal.html
"""
import multiprocessing as mp
from helper.parser import *
from helper.ringBuffer import *
from processes.simulator import *
from processes.serial import *


class Worker(mp.Process):

    def __init__(self, graph_id=None, samples=500, rate=0.2, port=None):
        mp.Process.__init__(self)
        self._graphid = graph_id
        self._samples = samples
        self._rate = rate
        self._port = port

        self._process = None
        self._parser = None
        self._lines = 0

        self._queue = mp.Queue()
        self._xbuffer = RingBuffer(samples)
        self._ybuffer = [RingBuffer(samples)]
        self.plist = []

    def run(self):
        self.clear_queue(self._samples)
        self._parser = Parser(data=self._queue,
                              samples=self._samples,
                              rate=self._rate)
        if self._graphid == 0:
            self._process = RandomSimulator(self._parser)
        elif self._graphid == 1:
            self._process = SineSimulator(self._parser)
        elif self._graphid == 2:
            self._process = Serial(self._parser)
        if self._process.check_init(port=self._port, speed=self._rate) and self._parser.check_init():
            self._parser.start()
            self.plist.append(self._parser)
            self._process.start()
            self.plist.append(self._process)

    def stop(self):
        self.get_plot_value()
        for process in self.plist:
            if process is not None and process.is_alive():
                process.stop()
                process.join(1000)

    def get_plot_value(self):
        while not self._queue.empty():
            self.distribute_values(self._queue.get_nowait())

    def distribute_values(self, data):
        self._xbuffer.append(data[0])
        self.split_channel_values(data[1])

    def split_channel_values(self, sig_data):
        channel_num = len(sig_data)
        if self._lines < channel_num:
            if channel_num > 5:
                self._lines = 5
            else:
                self._lines = channel_num
        for i in range(self._lines):
            self._ybuffer[i].append(sig_data[i])

    def get_channel_num(self):
        return self._lines

    def getxbuffer(self):
        return self._xbuffer.get_all()

    def getybuffer(self,i=0):
        return self._ybuffer[i].get_all()

    def clear_queue(self,s):
        self._xbuffer = RingBuffer(s)
        self._ybuffer = []
        for i in range(5):
            self._ybuffer.append(RingBuffer(s))
        while not self._queue.empty():
            self._queue.get()



