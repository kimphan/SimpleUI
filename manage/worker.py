"""
Worker:
    Role: connect between data computation process and data parsing process
    References:
        https://docs.python.org/2/library/multiprocessing.html
    Credit for:
        https://github.com/ssepulveda/RTGraph
"""
import numpy as np
from scipy.signal import correlate,savgol_filter
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

        self.lags = None
        self.ynorm = None
        self.autocorr= None

    def start(self):
        # Reset and Initialize buffers data
        self._xbuffer, self._ybuffer, self._queue = self.clear_queue(self._samples,self._queue)
        self.lags = RingBuffer(self._samples)
        self.autocorr = RingBuffer(self._samples)
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

    # Distributed collected data into separate buffers
    # Maximum channel allows is 6
    # Helper function: distribute_value
    # Input: data queue from Parser process (_queue)
    # Output: x-axis: _xbuffer (time)
    #         y-axis: _ybuffer (data from channel)
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

    # Return number of channel is read from Serial/Simulator process
    def get_channel_num(self):
        return self._lines

    # Get timer value
    def getxbuffer(self):
        # Normalize time values where the autocorrelation values are found
        xnorm = self._xbuffer.get_all() - np.mean(self._xbuffer.get_all())
        return xnorm

    # Get raw data from sensors and compute
    # Computation: filter raw data using Saviztky-Golay method
    #              detect the randomness in data with autocorrelation coefficient function
    #  Note: Lag value is an integer denoting how many time steps separate one value form another.
    #        Testing for randomness, need only one value of autocorrelation coefficient using lag k = 1
    def getybuffer(self, i):
        sgf = savgol_filter(self._ybuffer[i].get_all(),polyorder=3,window_length=37) # Filter the raw data
        ynorm = sgf - np.mean(sgf) # Normalize data
        y1 = np.sum(ynorm**2)      # Lag value at k=1
        autocorr = correlate(ynorm,ynorm,mode='same')/y1  # autocorrelation coefficient
        return autocorr

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


