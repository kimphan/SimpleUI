"""
Worker:
    Role: connect between data computation process and data parsing process
    References:
        https://docs.python.org/2/library/multiprocessing.html
    Credit for:
        https://github.com/ssepulveda/RTGraph
"""
from processes.parser import *
from helper.ringBuffer import *
from processes.simulator import *
from processes.serial import *


class Worker:

    def __init__(self, graph_id=None, samples=500, rate=0.02, port=None):
        self._graphid = graph_id
        self._samples = samples
        self._rate = rate
        self._port = port

        self._process = None
        self._parser = None
        self._lines = 0

        self._queue = mp.Queue()
        self._xbuffer = None
        self._ybuffer = None
        self.plist = None

    def start(self):
        # Reset and Initialize buffers data
        self._xbuffer, self._ybuffer, self._queue = self.clear_queue(self._samples,self._queue)
        self.plist = []
        self._parser = Parser(data=self._queue,
                              samples=self._samples,
                              rate=self._rate)
        if self._graphid == 2:
            self._process = RandomSimulator(self._parser)
        elif self._graphid == 1:
            self._process = SineSimulator(self._parser)
        elif self._graphid == 0:
            self._process = Serial(self._parser)
        if self._process.check_init(port=self._port, speed=self._rate):
            self._parser.start()
            self._process.start()
            self.plist.append(self._parser)
            self.plist.append(self._process)
            return True
        else:
            return False

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
        temp = data[1]
        channel_num = len(temp)
        if self._lines < channel_num:
            if channel_num > 6:
                self._lines = 6
            else:
                self._lines = channel_num
        for c in range(self._lines):
            self._ybuffer[c].append(temp[c])

    def get_channel_num(self):
        return self._lines

    def getxbuffer(self):
        return self._xbuffer.get_all()

    def getybuffer(self, i):
        return self._ybuffer[i].get_all()

    def is_running(self):
        return self._process is not None and self._process.is_alive()

    @staticmethod
    def clear_queue(s,q):
        x = RingBuffer(s)
        y = []
        i = 0
        while i < 6:
            y.append(RingBuffer(s))
            i += 1
        while not q.empty():
            q.get()
        return x, y, q


