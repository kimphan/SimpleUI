import unittest
import numpy as np
from multiprocessing import Queue
from helper.parser import *


class ParserProcessTests(unittest.TestCase):
    def test_fast_consumer(self):
        parser, queue = self._create_parser()
        parser.start()
        parser.add([1,5.5])
        self._stop_parser(parser)
        values = queue.get(False)

    @staticmethod
    def _create_parser():
        queue = Queue()
        parser = Parser(data=queue,
                        samples=500,
                        rate=0.2)
        return parser, queue

    @staticmethod
    def _stop_parser(parser):
        parser.stop()
        parser.join(1000)

    @staticmethod
    def _create_random_value(p):
        x = np.linspace(0,360)
        for i in x:
            y = np.sin(2*np.pi/180*i)
            p.add([x,y])


if __name__ == '__main__':
    unittest.main()
