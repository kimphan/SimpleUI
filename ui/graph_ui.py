from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt,QEvent
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRect
from helper.serial_scanner import SerialScan
from manage.manager import PlotManager
import pyqtgraph as pg


class GraphUi(QDialog):
    rm_button = pyqtSignal('QGroupBox',int,int)

    def __init__(self):
        super(GraphUi,self).__init__()
        self.channel_dict = dict()
        self._manager_dict = dict()
        self._os = SerialScan()
        self._plot_manager = PlotManager()
        self.add = 0
        self.yname = None
        self.xname = None

    def addgraph(self, width, height, i, key, title):

        # Setup widget
        _sample_num, _rate_num, _serial_port, _run_btn, _stop_btn = self._widget_config(i,key)
        _plot = self.plot_config(self.yname, self.xname)
        _plot.setMinimumWidth(width)
        _run_btn.pressed.connect(lambda: self.on_run_event(i, _stop_btn, _run_btn, _rate_num, _sample_num, _serial_port, _plot))
        _stop_btn.pressed.connect(lambda: self.on_stop_event(_stop_btn, _run_btn, _rate_num, _serial_port))



        # Qt Display
        layout = QHBoxLayout()
        layout.addWidget(_stop_btn)
        layout.addWidget(_run_btn)

        remove_btn = QPushButton('Remove')
        remove_btn.setObjectName(str(key))
        remove_btn.setStyleSheet('font-size: 12pt;')
        remove_btn.pressed.connect(self.on_remove_event)

        graph_widget = QGroupBox(title)
        graph_widget.setObjectName(str(key))
        graph_widget.setStyleSheet('font-size: 12pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(height)
        graph_widget.setMinimumWidth(width)

        graph_layout = QGridLayout()

        sub_widget = QWidget()
        sub_layout = QFormLayout()
        sub_layout.setAlignment(Qt.AlignRight)
        sub_layout.addRow(str('Sample: '), _sample_num)
        if i==2:
            _rate_num.setText('115200')
            sub_layout.addRow(str('Baud-rate: '), _rate_num)
            sub_layout.addRow(str('Port: '), _serial_port)
        else:
            sub_layout.addRow(str('Rate: '), _rate_num)

        sub_layout.addRow(str(''),layout)
        sub_layout.addRow(str(''),remove_btn)

        sub_widget.setLayout(sub_layout)

        graph_layout.addWidget(_plot, 0, 0, 3, 1, Qt.AlignLeft)
        graph_layout.addWidget(sub_widget, 0, 1, 3, 1,Qt.AlignLeft)

        graph_widget.setLayout(graph_layout)
        self.channel_dict.update({key: [graph_widget,_plot]})
        self.enable_ui(True,_stop_btn, _run_btn, _rate_num, _serial_port)
        return graph_widget


    def _widget_config(self, i, key):

        # Other setup config
        sample_num = QLineEdit()
        sample_num.setText('500')
        rate_num = QLineEdit()
        rate_num.setText('0.02')

        serial_port = QComboBox()
        serial_port.setEditable(True)
        serial_port.setFixedWidth(150)
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
        _object_.add_button.connect(self.display)
        _object_.closing.connect(self.clean_up)
        _object_.rescale.connect(self.plot_resize)

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
            self.rm_button.emit(self.channel_dict[remove_id][0], remove_id, self.add)
            del self.channel_dict[remove_id]

            if str(remove_id) in self._manager_dict.keys():
                self.stop_processes(self._manager_dict[str(remove_id)])
                del self._manager_dict[str(remove_id)]


        elif (m == message.No):
            pass

    # Run button Handler
    def on_run_event(self,i, stop_btn, run_btn, rate_num, sample_num, serial_port, plot):
        self.enable_ui(False,stop_btn, run_btn, rate_num, serial_port)
        add_id = self.sender().objectName()
        if add_id not in self._manager_dict.keys():
            self._plot_manager = PlotManager(i, sample_num.text(), rate_num.text(), serial_port.currentText(), plot)
            self._plot_manager.start()
            self._manager_dict.update({add_id: self._plot_manager})
        else:
            self._manager_dict[add_id].start()

    def on_stop_event(self,stop_btn, run_btn, rate_num, serial_port):
        self.enable_ui(True,stop_btn, run_btn, rate_num, serial_port)
        stop_id = self.sender().objectName()
        if stop_id in self._manager_dict.keys():
            self.stop_processes(self._manager_dict[stop_id])

    def enable_ui(self, e, stop_btn, run_btn, rate_num, serial_port):
        rate_num.setEnabled(e)
        serial_port.setEnabled(e)
        run_btn.setEnabled(e)
        stop_btn.setEnabled(not e)

    def stop_processes(self, current_plot):
        if current_plot.is_running():
            current_plot.stop()

    @pyqtSlot('QGridLayout', int, int, int, str, str, str, int)
    def display(self, graph_display, index, width, height, xname, yname, title, key):
        graph_display.setRowStretch(key, 3)
        channel = self.addgraph(width, height, index, key, title)
        graph_display.addWidget(channel, key, 0)
        self.index = index
        self.yname = yname
        self.xname = xname

    @pyqtSlot()
    def clean_up(self):
        if len(self._manager_dict) != 0 :
            for plot_id in self._manager_dict.keys():
                self.stop_processes(self._manager_dict[plot_id])
            self._manager_dict.clear()

    @pyqtSlot(int, int,int)
    def plot_resize(self,w,h,flag):

        for k in self.channel_dict.keys():
            self.channel_dict[k][0].setFixedHeight(h)
            self.channel_dict[k][0].setFixedWidth(w)
            self.channel_dict[k][1].setFixedWidth(w*3/4)




