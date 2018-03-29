import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from manage.worker import Worker


class PlotManager(object):

    def __init__(self, g_id, samples, rate, port, plot_widget):
        # mp.Process.__init__(self)
        self._worker = Worker()
        self._graph_id = g_id
        self._samples = int(samples)
        self._rate = float(rate)
        self._port = port
        self._plot = plot_widget

        self._configure_timers()
        self.color_dict = ({0:'#6c6d70',1:'#EB340D',2:'#0D46EB', 3:'#d01bd3', 4:'#ed9615'})

    def start(self):
        self._worker = Worker(graph_id=self._graph_id,
                              samples=self._samples,
                              rate=self._rate,
                              port=self._port)
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

    def _update_plot(self):
        if self._worker.is_running():
            self._worker.get_plot_value()
            self._plot.plotItem.clear()
            channel = self._worker.get_channel_num()
            for i in range(channel):
                pen = pg.mkPen(self.color_dict[i], width=3, style=None)
                self._plot.plotItem.plot(self._worker.getxbuffer(), self._worker.getybuffer(i), pen=pen)
        else:
            print('Failed')

    def is_running(self):
        return self._worker.is_running()
