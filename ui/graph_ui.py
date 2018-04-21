from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt,QEvent
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRect
from helper.serial_scanner import SerialScan
from manage.manager import PlotManager
import pyqtgraph as pg
import serial


class GraphUi(QDialog):
    rm_action = pyqtSignal(int)
    plot_action = pyqtSignal(int)
    stop_action = pyqtSignal(int)
    subplot_draw = pyqtSignal(str,int, int,int)

    def __init__(self, graph_i=0, sample='100', width=900, height=300, port=None, brate='115200', title=None, key=0):
        super(GraphUi,self).__init__()
        self.add = 0
        self.graphID = graph_i
        self.width = width
        self.height = height
        self.port = port
        self.brate = float(brate)
        self.graphName = title
        self.key = key
        self.sample = int(sample)

        self.control_panel = QFormLayout()
        self.xname = ''
        self.plot = None
        self.sample_num = QLabel(str(self.sample))
        self.rate_num = QLabel(str(self.brate))
        self.serial_port = QLabel(str(self.port))
        self.run_btn = None
        self.stop_btn = None
        self.remove_btn = None
        self.save_btn = None
        self.plot_manager = None


    def addgraph(self):

        # Setup widget
        self._widget_config()

        # Qt Display
        layout1 = QHBoxLayout()
        layout1.addWidget(self.stop_btn)
        layout1.addWidget(self.run_btn)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.save_btn)
        layout2.addWidget(self.remove_btn)

        graph_widget = QGroupBox(self.graphName)
        graph_widget.setObjectName(str(self.key))
        graph_widget.setStyleSheet('font-size: 12pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(self.height)
        graph_widget.setFixedWidth(self.width)

        graph_layout = QGridLayout()
        sub_widget = QWidget()
        self.control_panel = QFormLayout()
        self.control_panel.setAlignment(Qt.AlignRight)
        self.control_panel.addRow('Sample: ', self.sample_num)
        self.control_panel.addRow('Baudrate: ', self.rate_num)
        self.control_panel.addRow('Port: ', self.serial_port)
        self.control_panel.addRow(str(''),layout1)
        self.control_panel.addRow(str(''),layout2)

        sub_widget.setLayout(self.control_panel)

        graph_layout.addWidget(self.plot, 0, 0, 3, 1, Qt.AlignLeft)
        graph_layout.addWidget(sub_widget, 0, 1, 3, 1,Qt.AlignLeft)

        graph_widget.setLayout(graph_layout)

        self.enable_ui(True,self.stop_btn, self.run_btn)
        return graph_widget


    def _widget_config(self):
        # Plot Widget config
        self.plot = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        self.plot.setLabel('bottom', self.xname)
        self.plot.setAntialiasing(True)
        self.plot.setMinimumWidth(self.width*4/5)
        self.plot.plotItem.showGrid(True, True, 1)
        
        # Other setup config

        self.run_btn = QPushButton('Run')
        self.run_btn.setObjectName(str(self.key))
        self.run_btn.setStyleSheet('font-size: 12pt;')

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setObjectName(str(self.key))
        self.stop_btn.setStyleSheet('font-size: 12pt;')

        self.save_btn = QPushButton('Save')
        self.save_btn.setObjectName(str(self.key))
        self.save_btn.setStyleSheet('font-size: 12pt;')

        self.remove_btn = QPushButton('Remove')
        self.remove_btn.setObjectName(str(self.key))
        self.remove_btn.setStyleSheet('font-size: 12pt;')

        self.save_btn.pressed.connect(self.on_save)
        self.remove_btn.pressed.connect(self.on_remove_event)
        self.run_btn.pressed.connect(self.on_run_event)
        self.stop_btn.pressed.connect(self.on_stop_event)

    def make_connection(self, _object_):
        # _object_.add_button.connect(self.display)
        _object_.closing.connect(self.clean_up)
        _object_.rescale.connect(self.plot_resize)

    # Remove button Handler
    def on_remove_event(self):
        remove_id = int(self.sender().objectName())
        self.rm_action.emit(remove_id)

    # Run button Handler
    def on_run_event(self):
        self.enable_ui(False,self.stop_btn, self.run_btn)
        run_id = int(self.sender().objectName())
        self.plot_action.emit(run_id)

    def on_stop_event(self):
        self.enable_ui(True,self.stop_btn, self.run_btn)
        stop_id = int(self.sender().objectName())
        self.stop_action.emit(stop_id)

    def on_save(self):
        pass

    def enable_ui(self, e, stop_btn, run_btn):
        # rate_num.setEnabled(e)
        run_btn.setEnabled(e)
        stop_btn.setEnabled(not e)

    def selectionChange(self,i):
        if i > 0:
            # Draw the child graph
            self.subplot_draw.emit(self.clist.currentText(),self.key,self.graphID,i)


