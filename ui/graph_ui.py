from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from multiprocessing import Process, Queue
from helper.ringBuffer import *
from multiprocesses.simulator import *
import pyqtgraph as pg
import numpy as np


class GraphUi(QDialog):
    rm_button = pyqtSignal('QGroupBox',int,int)
    channel_dict = dict()
    key = 0
    add = 0

    def addgraph(self, widgetH, i, xname, yname,key):

        remove_btn = QPushButton('Remove')
        remove_btn.setObjectName(str(key))
        remove_btn.setStyleSheet('font-size: 15pt;')
        remove_btn.pressed.connect(self.on_remove_event)

        plot_widget = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        pen = pg.mkPen('#6c6d70', width=3, style=None)
        plot_widget.plotItem.showGrid(True, True, 0.7)

        if i == 0:
            x = np.random.normal(loc=0.0, scale=2, size=100)
            y = np.random.normal(loc=0.0, scale=2, size=100)
        else:
            x = np.linspace(0, 360)
            y = np.sin(x * np.pi / 180)
            q = Queue()
            self.p = SineSimulator()
            self.p.start()
            # self.p.get_xvalues()
            # x = self.p.get_xvalues()
            # y = self.p.get_yvalues()

        plot_widget.plotItem.plot(x, y, pen=pen)

        graph_widget = QGroupBox()
        graph_widget.setObjectName(str(key))
        graph_widget.setStyleSheet('font-size: 15pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(widgetH/2)

        graph_layout = QGridLayout()
        graph_layout.setColumnStretch(1, 8)
        graph_layout.addWidget(plot_widget,0,1)
        graph_layout.addWidget(remove_btn,0,2)
        graph_widget.setLayout(graph_layout)

        self.channel_dict.update({key: graph_widget})
        return graph_widget

    def make_connection(self, _object_):
        _object_.add_button.connect(self.display)

    def on_remove_event(self):
        remove_id = int(self.sender().objectName())
        message = QMessageBox()
        m = message.question(self,'Message','Do you want to delete the channel?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if (m == message.Yes):
            if len(self.channel_dict) == 2:
                if (remove_id == 1):
                    if 2 in self.channel_dict.keys():
                        self.add = 1 # add top and bottom
                    elif 3 in self.channel_dict.keys():
                        self.add = 2 # add top
                elif (remove_id == 2):
                    if 1 in self.channel_dict.keys():
                        self.add = 3 # add bottom
                    elif 3 in self.channel_dict.keys():
                        self.add = 2 # add top
                elif (remove_id == 3):
                    if 1 in self.channel_dict.keys():
                        self.add = 3 # add bottom
                    elif 2 in self.channel_dict.keys():
                        self.add = 1 # add top and bottom
            self.rm_button.emit(self.channel_dict[remove_id], remove_id, self.add)
            del self.channel_dict[remove_id]
        elif (m == message.No):
            pass

    @pyqtSlot('QGridLayout', int, str, str, int)
    def display(self, graph_display, index, xname, yname, key):
        channel = self.addgraph(self.height(), index, xname, yname,key)
        graph_display.setRowStretch(key-1, 4)
        graph_display.setColumnStretch(0, 4)
        graph_display.addWidget(channel,key-1,0)
        print('add key{}'.format(self.channel_dict.keys()))



