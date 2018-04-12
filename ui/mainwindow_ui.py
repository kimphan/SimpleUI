from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtSlot
from ui.graph_ui import GraphUi
from manage.manager import PlotManager
from helper.serial_scanner import SerialScan
import os, signal

class ExampleUI (QMainWindow):
    LABELFONT = 15
    add_button = pyqtSignal('QGridLayout', int, int, int, str, str, str, int)

    def __init__(self):
        super(ExampleUI, self).__init__()
        self.w = 1200
        self.h = 700
        self.setMinimumHeight(self.h+100)
        self.setMinimumWidth(self.w)
        self.center()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle('Channel Plot')
        self.setMenuBar(self.mymenu())

        self.key = 0
        self.plot_count = 0
        self.add = 0
        self.splot_count = 0
        self.port = None
        self.addtopbottom = False

        self.store_graph = dict()
        self.store_plot = dict()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.windowLayout = QHBoxLayout()
        self.windowLayout.setAlignment(Qt.AlignLeft)
        self.central_widget.setLayout(self.windowLayout)
        self.loadui()

    # Setup UI for main window
    def loadui(self):
        add_btn = self.button('Add', self.on_add_event)
        add_btn.setMaximumWidth(80)

        self.channel_list = QComboBox()
        self.graph_type = QComboBox()
        self.channel_name = QLineEdit()
        self.x_axis = QLineEdit()
        self.y_axis = QLineEdit()

        self.x_axis.setText('Time (s)')
        self.channel_list.currentTextChanged.connect(self.selectionChange)
        # Graph type list for displaying option
        self.graph_type.addItem('Serial')
        self.graph_type.addItem('Sine Simulator')
        self.graph_type.addItem('Random Plot')

        vertical_menu = QVBoxLayout()
        vertical_menu.setAlignment(Qt.AlignLeft)
        vertical_menu.SetFixedSize

        channel_select = QGroupBox('Channel Select')
        channel_select.setStyleSheet('font-size: 12pt; color: 606060;')
        selectC = QHBoxLayout()
        selectC.addWidget(self.channel_list)
        channel_select.setLayout(selectC)
        channel_select.setFixedWidth(self.w/5)
        channel_select.setFixedHeight(self.h/8)

        add_channel = QGroupBox('Add Channel')
        add_channel.setStyleSheet('font-size: 12pt; color: 606060;')
        addC = QFormLayout()
        addC.addRow(str('Graph type: '), self.graph_type)
        addC.addRow(str('Channel Name: '), self.channel_name)
        addC.addRow(str('x-Axis: '), self.x_axis)
        addC.addRow(str('y-Axis: '), self.y_axis)
        addC.addRow(str(''), add_btn)

        add_channel.setLayout(addC)
        add_channel.setFixedWidth(self.w/5)

        vertical_menu.addWidget(channel_select)
        vertical_menu.addWidget(add_channel)

        self.graph_display = QGridLayout()
        self.graph_display.setAlignment(Qt.AlignTop)
        self.graph_display.SetFixedSize

        self.windowLayout.addLayout(vertical_menu)
        self.windowLayout.addLayout(self.graph_display)
        # self.windowLayout.addStretch()
    # Label
    @staticmethod
    def label(name,fontsize=12):
        lbl = QLabel()
        lbl.setText(name)
        lbl.minimumSizeHint()
        lbl.setStyleSheet('font-size: {}pt; color: 606060;'.format(fontsize))
        return lbl

    # Put the application window in the center of the screen
    def center(self):
        frame = self.frameGeometry()  # specifying geometry of the main window with a rectangle 'qr'
        cp = QDesktopWidget().availableGeometry().center()  # screen size resolution+get the center point
        frame.moveCenter(cp)  # set the rectangle center to the center of the screen
        self.move(frame.topLeft())  # move the top-left point of the application window to the 'qr'

        # Menu bar
    def mymenu(self):
        saveaction = self.actiondef('Save', QKeySequence.Save, self.saveact)
        editaction = self.actiondef('Edit', QKeySequence.Back, self.editact)

        mainmenu = QMenuBar(self)
        mainmenu.setNativeMenuBar(False)
        filemenu = mainmenu.addMenu('File')
        editmenu = mainmenu.addMenu('Edit')
        viewmenu = mainmenu.addMenu('View')
        toolmenu = mainmenu.addMenu('Tool')
        filemenu.addAction(saveaction)
        editmenu.addAction(editaction)
        return mainmenu

    def actiondef(self, actionname, keyseq, func):
        action = QAction(actionname, self)
        action.setShortcut(keyseq)
        action.setStatusTip(actionname)
        action.triggered.connect(func)
        return action

    def saveact(self):
        print('save act')

    def editact(self):
        print('edit act')

    # Button and event handling
    def button(self,name, handler, fontsize=12):
        btn = QPushButton(name)
        btn.setStyleSheet('font-size: {}pt;'.format(fontsize))
        btn.pressed.connect(handler)
        return btn

    def on_add_event(self):
        sending_button = self.sender()
        self.statusBar().showMessage('{}'.format(sending_button.text()))

        # Add 1 on top and 1 in bottom
        if self.addtopbottom and self.key == 1:
            self.key = 2
            self.addtopbottom = False

        if self.plot_count >= 3:
            message = QMessageBox.information(self, 'Message', 'Number of displayed graph exceeds the limit.', QMessageBox.Ok)
            if QMessageBox.Ok:
                pass
        else:
            self.channel_list.clear()
            if self.graph_type.currentIndex() == 0:
                if not self.channel_sensing():
                    print('No Serial port found')
            elif self.graph_type.currentIndex() == 1:
                self.channel_list.addItem('Both')
                for i in range(self.graph_type.currentIndex() + 1):
                    self.channel_list.addItem('Channel ' + str(i + 1))
            else:
                self.channel_list.addItem('Single plot')
            self.draw()

            self.channel_name.clear()
            self.x_axis.setText('Time (s)')
            self.y_axis.clear()

    def draw(self):
        self.plot_count += 1
        self.key += 1
        graph = GraphUi(self.graph_type.currentIndex(),
                        self.w / 5 * 3, self.h / 3,
                        self.x_axis.text(), self.y_axis.text(), self.channel_name.text(),
                        self.key)
        self.graph_display.setRowStretch(self.key, 3)
        draw_graph = graph.addgraph()
        self.graph_display.addWidget(draw_graph, self.key, 0)
        self.make_connection(graph)
        self.store_graph.update({self.key: [graph, draw_graph]})
        graph._serial_port.setCurrentText(self.port)
        _plot_manager = PlotManager(graph.graphID, graph._sample_num.text(), graph._rate_num.text(), self.port,
                                    graph._plot)
        self.store_plot.update({self.key: _plot_manager})
        graph._serial_port.setCurrentText(self.port)

    def make_connection(self, _object_):
        _object_.rm_action.connect(self.remove_plot)
        _object_.plot_action.connect(self.plot_data)
        _object_.stop_action.connect(self.stop_plot)

    def closeEvent(self, event):
        if len(self.store_plot) != 0 :
            for plot_id in self.store_plot.keys():
                self.stop_processes(self.store_plot[plot_id])
            self.store_plot.clear()
        super(ExampleUI, self).closeEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() == Qt.WindowFullScreen:
            # if self.windowState() & Qt.WindowMaximized:
                screen_resolution = qApp.desktop().screenGeometry()
                self.w, self.h = screen_resolution.width(), screen_resolution.height()
                self.h -= 100
                self.resize_plot(self.w/5*4, self.h/3)
            else:
                self.h = 700
                self.w = 1200
                self.resize_plot(self.w/5*4, self.h/3)

        super(ExampleUI,self).changeEvent(event)

    def resize_plot(self,w,h):
        for k in self.store_graph.keys():
            self.store_graph[k][1].setFixedHeight(h)
            self.store_graph[k][1].setFixedWidth(w)
            self.store_graph[k][0]._plot.setFixedWidth(w*3/4)

    @pyqtSlot(int)
    def remove_plot(self,rm_id):
        self.plot_count -= 1
        message = QMessageBox()
        m = message.question(self, 'Message', 'Do you want to delete the channel?', QMessageBox.Yes | QMessageBox.No,
                             QMessageBox.No)
        if (m == message.Yes):
            if len(self.store_graph) == 2:
                if (rm_id == 1):
                    if 2 in self.store_graph.keys():
                        self.add = 1  # add top and bottom
                    elif 3 in self.store_graph.keys():
                        self.add = 2  # add top
                elif (rm_id == 2):
                    if 1 in self.store_graph.keys():
                        self.add = 3  # add bottom
                    elif 3 in self.store_graph.keys():
                        self.add = 2  # add top
                elif (rm_id == 3):
                    if 1 in self.store_graph.keys():
                        self.add = 3  # add bottom
                    elif 2 in self.store_graph.keys():
                        self.add = 1  # add top and bottom
            self.store_graph[rm_id][1].close()
            del self.store_graph[rm_id]
        elif (m == message.No):
            pass

        # Position to add graph
        if self.plot_count == 1:
            # Add 1 widget on top and 1 at bottom
            if self.add == 1:
                self.key = 0
                self.addtopbottom = True
            # Add 2 widget on top
            elif self.add == 2:
                self.key = 0
            # Add 2 widget on bottom
            elif self.add == 3:
                self.key = 1
        elif self.plot_count > 1:
            self.key = rm_id-1
        else:
            self.key = 0

    @pyqtSlot(int)
    def plot_data(self, run_id):
        info = self.store_graph[run_id][0]
        self.store_plot[run_id].update_parameter(info._sample_num.text(), info._rate_num.text())
        self.store_plot[run_id].start()


    @pyqtSlot(int)
    def stop_plot(self,stop_id):
        if stop_id in self.store_plot.keys():
            self.stop_processes(self.store_plot[stop_id])

    @staticmethod
    def stop_processes(current_plot):
        if current_plot.is_running():
            current_plot.stop()

    def channel_sensing(self):

        scan = SerialScan()
        channel_line, port = scan.channel_scan(115200)
        if channel_line == 0:
            message = QMessageBox.information(self, 'Message', 'Cannot recognize channel.', QMessageBox.Ok)
            if QMessageBox.Ok:
                return False
        else:
            self.port = port
            self.channel_list.addItem('Both')
            for c in range(channel_line):
                self.channel_list.addItem('Channel ' + str(c+1))
        return True

    def selectionChange(self,i):
        if i == 'Both':
            pass
        else:
            t = i.split(' ')
            idx = int(t[1])
            self.draw()
            info = self.store_graph[self.key][0]
            self.store_plot[self.key].update_parameter(info._sample_num.text(), info._rate_num.text(),True)
            self.store_plot[self.key].start()
            self.store_graph[self.key][0].enable_ui(False, info._stop_btn, info._run_btn, info._rate_num, info._serial_port)

