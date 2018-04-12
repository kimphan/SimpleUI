from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt,QEvent
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRect
from helper.serial_scanner import SerialScan
from manage.manager import PlotManager
import pyqtgraph as pg


class GraphUi(QDialog):
    rm_action = pyqtSignal(int)
    plot_action = pyqtSignal(int)
    stop_action = pyqtSignal(int)


    def __init__(self, graph_i=0, width=900, height=300, xn=None, yn=None, title=None, key=0):
        super(GraphUi,self).__init__()
        self.channel_dict = dict()
        self._manager_dict = dict()
        self.channel_list = None
        self._os = SerialScan()

        self.add = 0
        self.graphID = graph_i
        self.width = width
        self.height = height
        self.xname = xn
        self.yname = yn
        self.graphName = title
        self.dkey = key
        self._plot = None
        self._sample_num = None
        self._rate_num = None
        self._serial_port = None
        self._run_btn = None
        self._stop_btn = None
        self._remove_btn = None


    def addgraph(self):
        # Setup widget
        self._sample_num, self._rate_num, self._serial_port, self._run_btn, self._stop_btn = self._widget_config(self.dkey)
        self._plot = self.plot_config(self.yname, self.xname)
        self._plot.setMinimumWidth(self.width)
        self._run_btn.pressed.connect(lambda: self.on_run_event(self.graphID, self._stop_btn, self._run_btn, self._rate_num, self._sample_num, self._serial_port, self._plot))
        self._stop_btn.pressed.connect(lambda: self.on_stop_event(self._stop_btn, self._run_btn, self._rate_num, self._serial_port))

        # Qt Display
        layout = QHBoxLayout()
        layout.addWidget(self._stop_btn)
        layout.addWidget(self._run_btn)

        self._remove_btn = QPushButton('Remove')
        self._remove_btn.setObjectName(str(self.dkey))
        self._remove_btn.setStyleSheet('font-size: 12pt;')
        self._remove_btn.pressed.connect(self.on_remove_event)

        graph_widget = QGroupBox(self.graphName)
        graph_widget.setObjectName(str(self.dkey))
        graph_widget.setStyleSheet('font-size: 12pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(self.height)
        graph_widget.setMinimumWidth(self.width)

        graph_layout = QGridLayout()

        sub_widget = QWidget()
        sub_layout = QFormLayout()
        sub_layout.setAlignment(Qt.AlignRight)
        sub_layout.addRow(str('Sample: '), self._sample_num)
        if self.graphID==0:
            self._rate_num.setText('115200')
            sub_layout.addRow(str('Baudrate: '), self._rate_num)
            sub_layout.addRow(str('Port: '), self._serial_port)
        else:
            sub_layout.addRow(str('Rate: '), self._rate_num)

        sub_layout.addRow(str(''),layout)
        sub_layout.addRow(str(''),self._remove_btn)

        sub_widget.setLayout(sub_layout)

        graph_layout.addWidget(self._plot, 0, 0, 3, 1, Qt.AlignLeft)
        graph_layout.addWidget(sub_widget, 0, 1, 3, 1,Qt.AlignLeft)

        graph_widget.setLayout(graph_layout)
        self.channel_dict.update({self.dkey: [graph_widget, self._plot]})

        self.enable_ui(True,self._stop_btn, self._run_btn, self._rate_num, self._serial_port)
        return graph_widget


    def _widget_config(self,key):
        # Other setup config
        sample_num = QLineEdit()
        sample_num.setText('500')
        rate_num = QLineEdit()
        rate_num.setText('0.02')

        serial_port = QComboBox()
        serial_port.setEditable(True)
        serial_port.setFixedWidth(100)
        for o in self._os._scan_serial_port():
            serial_port.addItem(o)

        run_btn = QPushButton('Run')
        run_btn.setObjectName(str(key))
        run_btn.setStyleSheet('font-size: 12pt;')

        stop_btn = QPushButton('Stop')
        stop_btn.setObjectName(str(key))
        stop_btn.setStyleSheet('font-size: 12pt;')

        return sample_num, rate_num, serial_port, run_btn, stop_btn

    def plot_config(self, yname, xname):
        # Plot Widget config
        plot = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        plot.setLabel('left', yname)
        plot.setLabel('bottom', xname)
        plot.setAntialiasing(True)
        plot.plotItem.showGrid(True, True, 1)
        return plot

    def make_connection(self, _object_):
        # _object_.add_button.connect(self.display)
        _object_.closing.connect(self.clean_up)
        _object_.rescale.connect(self.plot_resize)

    # Remove button Handler
    def on_remove_event(self):
        remove_id = int(self.sender().objectName())
        self.rm_action.emit(remove_id)

    # Run button Handler
    def on_run_event(self, i, stop_btn, run_btn, rate_num, sample_num, serial_port, plot):
        self.enable_ui(False,stop_btn, run_btn, rate_num, serial_port)
        run_id = int(self.sender().objectName())
        self.plot_action.emit(run_id)

    def on_stop_event(self,stop_btn, run_btn, rate_num, serial_port):
        self.enable_ui(True,stop_btn, run_btn, rate_num, serial_port)
        stop_id = int(self.sender().objectName())
        self.stop_action.emit(stop_id)

    def enable_ui(self, e, stop_btn, run_btn, rate_num, serial_port):
        rate_num.setEnabled(e)
        serial_port.setEnabled(e)
        run_btn.setEnabled(e)
        stop_btn.setEnabled(not e)

