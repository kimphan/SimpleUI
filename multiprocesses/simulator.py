import multiprocessing
import numpy as np

class SineSimulator(multiprocessing.Process):

    # Constructor
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.xQ = np.linspace(0, 360)
        self.plotQ = multiprocessing.Queue()

    # Method representing the process's activity
    #   invokes the callable object passed to the object's constructor as the target argument
    def run(self):
        for x in self.xQ:
            y = np.sin(x * np.pi / 180)
            self.plotQ.put(str('{},{}').format(x,y))

    def get_xvalues(self):
        x = []
        while self.plotQ is not None:
            print(self.plotQ.get())

    def get_yvalues(self):
        return self.plotQ