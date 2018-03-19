
"""
Real-Time Graph: local process
    Role: data computation for Sine Wave graph
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
"""
from multiprocessing import Process, Queue, Event
from serial import Serial
from serial.tools import list_ports
import signal, time
import numpy as np


class Serial(Process):

    # Constructor
    def __init__(self, parser):
        Process.__init__(self)
        self._parser = parser
        self._port = None
        self._baudrate = None
        self._serial = Serial()

    def run(self):
        print('Serial start')

    def check_init(self, port=None, speed=0.2):
        if self.name is not None:
            self._exit = Event()
            self._baudrate = speed
            self._port = port
            return True
        else:
            return False

    def stop(self):
        self.terminate()
        time.sleep(0.1)







