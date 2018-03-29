from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from helper.serial_scanner import SerialScan
from manage.manager import PlotManager
import pyqtgraph as pg



class GraphUi(QDialog):
    rm_button = pyqtSignal('QGroupBox',int,int)

    def __init__(self):
        super(GraphUi,self).__init__()
        self.channel_dict = dict()
        self._worker_dict = dict()
        self._os = SerialScan()
        self.add = 0

    def addgraph(self, width, height, i, key, xname, yname, title):
        # Plot Config
        self._plot_config(yname, xname,key)

        # Initial setup input
        self._setup_config(i,key)

        # Qt Display
        layout = QHBoxLayout()
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.run_btn)

        remove_btn = QPushButton('Remove')
        remove_btn.setObjectName(str(key))
        remove_btn.setStyleSheet('font-size: 12pt;')
        remove_btn.pressed.connect(self.on_remove_event)

        graph_widget = QGroupBox(title)
        graph_widget.setObjectName(str(key))
        graph_widget.setStyleSheet('font-size: 12pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(height/3)
        graph_widget.setMaximumWidth(width*4/5)

        graph_layout = QGridLayout()
        graph_layout.setColumnStretch(0, 10)
        graph_layout.setColumnStretch(1, 3)

        sub_widget = QGroupBox()
        sub_layout = QFormLayout()
        sub_layout.setAlignment(Qt.AlignRight)
        sub_layout.addRow(str('Sample: '), self.sample_num)
        if i==2:
            self.rate_num.setText('115200')
            sub_layout.addRow(str('Baud-rate: '), self.rate_num)
            sub_layout.addRow(str('Port: '), self.serial_port)
        else:
            sub_layout.addRow(str('Rate: '), self.rate_num)

        sub_layout.addRow(str(''),layout)
        sub_layout.addRow(str(''),remove_btn)

        sub_widget.setLayout(sub_layout)

        graph_layout.addWidget(self._plot, 0, 0, Qt.AlignCenter)
        graph_layout.addWidget(sub_widget, 0, 1, Qt.AlignLeft)

        graph_widget.setLayout(graph_layout)
        self.channel_dict.update({key: graph_widget})
        self.enable_ui(True)
        return graph_widget

    # Plot Widget configuration
    def _plot_config(self, yname, xname, key):
        self._plot = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        self._plot.setLabel('left', yname)
        self._plot.setLabel('bottom', xname)
        self._plot.plotItem.showGrid(True, True, 0.7)

    def _setup_config(self, i, key):
        self.sample_num = QLineEdit()
        self.sample_num.setText('500')
        self.rate_num = QLineEdit()
        self.rate_num.setText('0.02')

        self.serial_port = QComboBox()
        self.serial_port.setEditable(True)
        self.serial_port.setMaximumWidth(170)
        for o in self._os._scan_serial_port():
            self.serial_port.addItem(o)

        self.run_btn = QPushButton('Run')
        self.run_btn.setObjectName(str(key))
        self.run_btn.setStyleSheet('font-size: 12pt;')
        self.run_btn.pressed.connect(lambda: self.on_run_event(i))

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setObjectName(str(key))
        self.stop_btn.setStyleSheet('font-size: 12pt;')
        self.stop_btn.pressed.connect(self.on_stop_event)

        self.enable_ui(True)

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
            if self._plot_manager.is_running():
                self._plot_manager.stop()
        elif (m == message.No):
            pass

    # Run button Handler
    def on_run_event(self,i):
        self.enable_ui(False)
        self._plot_manager = PlotManager(i, self.sample_num.text(), self.rate_num.text(), self.serial_port.currentText(), self._plot)
        self._plot_manager.start()

    def on_stop_event(self):
        self.enable_ui(True)
        self._plot_manager.stop()

    def enable_ui(self, e):
        self.rate_num.setEnabled(e)
        self.serial_port.setEnabled(e)
        self.run_btn.setEnabled(e)
        self.stop_btn.setEnabled(not e)

    @pyqtSlot('QGridLayout', int, int, int, str, str, str, int)
    def display(self, graph_display, index, width, height, xname, yname, title, key):
        graph_display.setRowStretch(key, 4)
        channel = self.addgraph(width, height, index, key, xname, yname, title)
        graph_display.addWidget(channel, key, 0)
        self.index = index
