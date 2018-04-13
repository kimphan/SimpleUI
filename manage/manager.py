"""
PlotManager:
    Role: plot data
    References:
        https://github.com/ssepulveda/RTGraph
"""
import pyqtgraph as pg
from PyQt5.QtCore import QTimer,pyqtSignal,QObject
from manage.worker import Worker

class PlotManager(QObject):

    def __init__(self, g_id=0, samples=500, rate=0.02, port=None, plot_widget=None):
        super(PlotManager,self).__init__()
        # mp.Process.__init__(self)
        self.worker = Worker()
        self.graph_id = g_id
        self.samples = int(samples)
        self.rate = float(rate)
        self.port = port
        self.plot = plot_widget

        self.configure_timers()
        self.color_dict = ({0:'#6c6d70',1:'#EB340D',2:'#0D46EB', 3:'#d01bd3', 4:'#ed9615', 5: '#298909'})
        self.read_line = -1

    def start(self):
        self.worker = Worker(graph_id=self.graph_id,samples=self.samples,rate=self.rate,port=self.port)
        if self.worker.start():
            self.timer_plot.start(20)

    def stop(self):
        self.timer_plot.stop()
        self.worker.stop()

    def configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self.timer_plot = QTimer()
        self.timer_plot.timeout.connect(self.update_plot)

    def update_plot(self,read_line = -1):
        print('readline {}'.format(read_line))
        if self.worker.is_running():
            self.worker.get_plot_value()
            self.plot.plotItem.clear()
            count = self.worker.get_channel_num()
            if self.read_line < 0:
                for i in range(count):
                    pen = pg.mkPen(self.color_dict[i], width=1, style=None)
                    self.plot.plotItem.plot(self.worker.getxbuffer(), self.worker.getybuffer(i), pen=pen)
            else:
                pen = pg.mkPen(self.color_dict[self.read_line-1], width=1, style=None)
                self.plot.plotItem.plot(self.worker.getxbuffer(), self.worker.getybuffer(0), pen=pen)
        else:
            print('Failed')

    def is_running(self):
        return self.worker.is_running()

    def update_parameter(self,s,r):
        self.samples = int(s)
        self.rate = float(r)
        print('manager update')






