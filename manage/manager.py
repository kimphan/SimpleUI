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
        self._worker = Worker()
        self._graph_id = g_id
        self._samples = int(samples)
        self._rate = float(rate)
        self._port = port
        self._plot = plot_widget

        self._configure_timers()
        self.color_dict = ({0:'#6c6d70',1:'#EB340D',2:'#0D46EB', 3:'#d01bd3', 4:'#ed9615', 5: '#298909'})
        self.read_line = -1

    def start(self):
        self._worker = Worker(graph_id=self._graph_id,samples=self._samples,rate=self._rate,port=self._port)
        if self._worker.start():
            self._timer_plot.start(20)

    def stop(self):
        self._timer_plot.stop()
        self._worker.stop()

    def _configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self._timer_plot = QTimer()
        self._timer_plot.timeout.connect(self._update_plot)

    def _update_plot(self,read_line = -1):
        if self._worker.is_running():
            self._worker.get_plot_value()
            self._plot.plotItem.clear()
            count = self._worker.get_channel_num()
            if read_line < 0:
                for i in range(count):
                    pen = pg.mkPen(self.color_dict[i], width=1, style=None)
                    self._plot.plotItem.plot(self._worker.getxbuffer(), self._worker.getybuffer(i), pen=pen)
            else:
                pen = pg.mkPen(self.color_dict[read_line-1], width=1, style=None)
                self._plot.plotItem.plot(self._worker.getxbuffer(), self._worker.getybuffer(0), pen=pen)
        else:
            print('Failed')

    def is_running(self):
        return self._worker.is_running()

    def update_parameter(self,s,r):
        self._samples = int(s)
        self._rate = float(r)
        print('manager update')






