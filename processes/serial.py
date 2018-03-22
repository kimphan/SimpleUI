
"""
Real-Time Graph: local process
    Role: data computation for Sine Wave graph
    References:
        https://docs.python.org/2/library/multiprocessing.html
        https://github.com/ssepulveda/RTGraph
"""
import multiprocessing as mp
import serial
from serial.tools import list_ports
from time import time, sleep
import numpy as np


class Serial(mp.Process):

    # Constructor
    def __init__(self, prser):
        mp.Process.__init__(self)
        self._parser = prser
        self._exit = mp.Event()
        self._serial = serial.Serial()

    @staticmethod
    def _is_ports_available(port):
        for p in list(list_ports.comports()):
            if p.device == port:
                return True

    def run(self):
        t1 = time()
        if self._is_ports_available(self._serial.port):
            if not self._serial.is_open:
                self._serial.open()
                t = time() - t1
                print(self._exit.is_set())
                while not self._exit.is_set():
                    print(self._serial.readline())
                    # self._parser.add([t, self._serial.readline()])
                self._serial.close()
        else:
            print('Port is not available.')

    def check_init(self, port=None, speed=115200):
        if self.name is not None:
            self._serial.port = port
            self._serial.baudrate = int(speed)
            self._serial.stopbits = serial.STOPBITS_ONE
            self._serial.bytesize = serial.EIGHTBITS
            self._serial.timeout = 1
            return True
        else:
            return False

    def stop(self):
        print('serial stop')
        self._exit.set()







