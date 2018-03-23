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
            self._get_data()
            time.sleep(0.005)
        self._get_data()

    def stop(self):
        self._exit.set()

    def add(self, data):
        self._importQ.put(data)

    def _get_data(self):
        while not self._importQ.empty():
            queue = self._importQ.get(timeout=0.05)
            self.parse_data(queue[0], queue[1])

    def parse_data(self, t, line):
        if len(line) > 0:
            try:
                if type(line) == bytes:
                    values = line.decode("UTF-8").split(',')
                elif type(line) == str:
                    values = line.split(',')
                else:
                    raise TypeError
                values = [float(v) for v in values]
                self._exportQ.put([t, values])
            except ValueError:
                print('Value Error')
            except AttributeError:
                print('Attribute Error')









