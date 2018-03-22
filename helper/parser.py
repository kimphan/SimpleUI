"""
Parser: local process
    Role: access the data queue locally
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
"""
import signal, time
import multiprocessing as mp


class Parser(mp.Process):

    def __init__(self, data, samples, rate):
        mp.Process.__init__(self)
        self._importQ = mp.Queue()
        self._sample = samples
        self._rate = rate
        self._exportQ = data
        self.count = 0
        self._exit = mp.Event()

    def check_init(self):
        return self.name is not None

    def run(self):
        while not self._exit.is_set():
            self._parse_data()
            time.sleep(0.005)
        self._parse_data()

    def stop(self):
        self._exit.set()

    def add(self, data):
        self._importQ.put(data)

    def _parse_data(self):
        while not self._importQ.empty():
            self._exportQ.put(self._importQ.get(timeout=0.05))







