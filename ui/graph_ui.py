from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer
from multiprocessing import Lock
from helper.ringBuffer import *
from processes.worker import Worker
import pyqtgraph as pg
import numpy as np
import os


class GraphUi(QDialog):
    rm_button = pyqtSignal('QGroupBox',int,int)

    def __init__(self):
        super(GraphUi,self).__init__()
        self.channel_dict = dict()
        self.color_dict = ({0:'#6c6d70',1:'#EB340D',2:'#0D46EB'})
        self.add = 0


    def addgraph(self, width, height, i, key, xname, yname, title):
        # Plot Config
        self.plot_widget = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        self.plot_widget.setLabel('left', yname)
        self.plot_widget.setLabel('bottom', xname)
        self.plot_widget.plotItem.showGrid(True, True, 0.7)
        self.pen = pg.mkPen(self.color_dict[key-1], width=3, style=None)

        # Display Setup
        self.sample_num = QLineEdit()
        self.sample_num.setText('500')
        self.rate_num = QLineEdit()
        self.rate_num.setText('0.2')
        self.serial_port = QLineEdit()

        self.run_btn = QPushButton('Run')
        self.run_btn.setObjectName('run')
        self.run_btn.setStyleSheet('font-size: 13pt;')
        self.run_btn.pressed.connect(lambda: self.on_run_event(i))

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setObjectName('stop')
        self.stop_btn.setStyleSheet('font-size: 13pt;')
        self.stop_btn.pressed.connect(self.on_stop_event)


        layout = QHBoxLayout()
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.run_btn)

        remove_btn = QPushButton('Remove')
        remove_btn.setObjectName(str(key))
        remove_btn.setStyleSheet('font-size: 13pt;')
        remove_btn.pressed.connect(self.on_remove_event)

        graph_widget = QGroupBox(title)
        graph_widget.setObjectName(str(key))
        graph_widget.setStyleSheet('font-size: 15pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(height/3)
        graph_widget.setMinimumWidth(width*4/5)

        graph_layout = QGridLayout()
        graph_layout.setColumnStretch(0, 10)
        graph_layout.setColumnStretch(1, 3)

        sub_widget = QGroupBox()
        sub_layout = QFormLayout()
        sub_layout.setAlignment(Qt.AlignRight)
        sub_layout.addRow(str('Sample: '), self.sample_num)

        if i==2:

            sub_layout.addRow(str('Baurate: '), self.rate_num)
            sub_layout.addRow(str('Port: '), self.serial_port)
        else:
            sub_layout.addRow(str('Rate: '), self.rate_num)

        sub_layout.addRow(str(''),layout)
        sub_layout.addRow(str(''),remove_btn)

        sub_widget.setLayout(sub_layout)

        graph_layout.addWidget(self.plot_widget, 0, 0, Qt.AlignCenter)
        graph_layout.addWidget(sub_widget, 0, 1, Qt.AlignLeft)

        graph_widget.setLayout(graph_layout)
        self.channel_dict.update({key: graph_widget})
        self.worker = Worker()
        self._configure_timers()
        return graph_widget

    # Set timer to update graph every 20 ms
    def _configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self._timer_plot = QTimer(self)
        self._timer_plot.timeout.connect(self._update_plot)

    def _update_plot(self):
        self.worker.get_plot_value()
        self.plot_widget.plotItem.plot(self.worker.getxbuffer(), self.worker.getybuffer(), pen=self.pen)

    def make_connection(self, _object_):
        _object_.add_button.connect(self.display)

    # Remove button Handler
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
            self._timer_plot.stop()
            self.worker.stop()
        elif (m == message.No):
            pass

    # Run button Handler
    def on_run_event(self,i):
        self.run_btn.setEnabled(False)
        self.lock = Lock()
        self.worker = Worker(graph_id= i,
                             samples=int(self.sample_num.text()),
                             rate=float(self.rate_num.text()),
                             lock=self.lock,
                             port=self.serial_port.text())

        self.worker.start()
        if self.worker.is_alive():
            self._timer_plot.start(20)
        else:
            print('worker not start')

    def on_stop_event(self):
        self.run_btn.setEnabled(True)
        self._timer_plot.stop()

    @pyqtSlot('QGridLayout', int, int, int, str, str, str, int)
    def display(self, graph_display, index, width, height, xname, yname, title, key):
        graph_display.setRowStretch(key, 4)
        channel = self.addgraph(width, height, index, key, xname, yname, title)
        graph_display.addWidget(channel, key, 0)
        self.index = index
        print('add key{}'.format(self.channel_dict.keys()))



