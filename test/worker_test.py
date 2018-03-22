import unittest
from time import sleep

from processes.worker import Worker


class WorkerTests(unittest.TestCase):
    def test_one(self):
        time = 2
        speed = 0.02
        error = 0.95
        zeros = 0
        passed = False
        samples = int(time * (1/speed))
        samples_plus_error = int(samples / error)

        worker = Worker(graph_id=0,
                        samples=500,
                        rate=0.2,
                        port=None)
        worker.start()
        sleep(time)
        worker.stop()
        worker.get_plot_value()

        for v in worker.getybuffer(0):
            if v == 0:
                zeros += 1
        print(zeros)
        # if 0 < zeros <= ((samples_plus_error - samples) * 2):
        #     passed = True
        # self.assertTrue(passed)


if __name__ == '__main__':
    unittest.main()
