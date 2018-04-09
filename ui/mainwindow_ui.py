from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtSlot
import os, signal

class ExampleUI (QMainWindow):
    LABELFONT = 15
    add_button = pyqtSignal('QGridLayout', int, int, int, str, str, str, int)
    closing = pyqtSignal()
    def __init__(self):
        super(ExampleUI, self).__init__()

        self.resize(1200, 800)
        self.center()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle('Channel Plot')
        self.setMenuBar(self.mymenu())

        self.key = 0
        self.channel_count = 0
        self.addtopbottom = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.windowLayout = QHBoxLayout()
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

        # Graph type list for displaying option
        self.graph_type.addItem('Random Plot')
        self.graph_type.addItem('Sine Simulator')
        self.graph_type.addItem('Serial')

        vertical_menu = QVBoxLayout()
        vertical_menu.setAlignment(Qt.AlignLeft)
        vertical_menu.SetFixedSize

        channel_select = QGroupBox('Channel Select')
        channel_select.setStyleSheet('font-size: 12pt; color: 606060;')
        selectC = QHBoxLayout()
        selectC.addWidget(self.channel_list)
        channel_select.setLayout(selectC)
        channel_select.setFixedWidth(self.width()/5)
        channel_select.setFixedHeight(self.height()/8)

        add_channel = QGroupBox('Add Channel')
        add_channel.setStyleSheet('font-size: 12pt; color: 606060;')
        addC = QFormLayout()
        addC.addRow(str('Graph type: '), self.graph_type)
        addC.addRow(str('Channel Name: '), self.channel_name)
        addC.addRow(str('x-Axis: '), self.x_axis)
        addC.addRow(str('y-Axis: '), self.y_axis)
        addC.addRow(str(''), add_btn)

        add_channel.setLayout(addC)
        add_channel.setFixedWidth(self.width()/5)

        vertical_menu.addWidget(channel_select)
        vertical_menu.addWidget(add_channel)

        self.graph_display = QGridLayout()
        self.graph_display.setAlignment(Qt.AlignTop)
        self.graph_display.SetMinAndMaxSize

        self.windowLayout.addLayout(vertical_menu)
        self.windowLayout.addLayout(self.graph_display)
        self.windowLayout.addStretch(1)

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
            qr = self.frameGeometry()  # specifying geometry of the main window with a rectangle 'qr'
            cp = QDesktopWidget().availableGeometry().center()  # screen size resolution+get the center point
            qr.moveCenter(cp)  # set the rectangle center to the center of the screen
            self.move(qr.topLeft())  # move the top-left point of the application window to the 'qr'

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

        if self.channel_count >= 3:
            message = QMessageBox.information(self, 'Message', 'Number of displayed graph exceeds the limit.', QMessageBox.Ok)
            if QMessageBox.Ok:
                pass
        else:
            self.channel_count += 1
            self.key += 1

            self.add_button.emit(self.graph_display, self.graph_type.currentIndex(),
                                 self.width()/5*3.5,self.height()/3,
                                 self.x_axis.text(), self.y_axis.text(), self.channel_name.text(),
                                 self.key)
            self.channel_name.clear()
            self.x_axis.clear()
            self.y_axis.clear()


    def make_connection(self, _object_):
        _object_.rm_button.connect(self.remove_channel)

    def closeEvent(self, event):
        self.closing.emit()
        super(ExampleUI, self).closeEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                print('changeEvent: Minimised')
            elif event.oldState() & Qt.WindowMinimized:
                print('changeEvent: Normal/Maximised/FullScreen')
        QWidget.changeEvent(self, event)

    @pyqtSlot('QGroupBox',int,int)
    def remove_channel(self, rm_widget, rm_id, add_position):
        rm_widget.close()
        self.channel_count -= 1

        # Position to add graph
        if self.channel_count == 1:
            # Add 1 widget on top and 1 at bottom
            if add_position == 1:
                self.key = 0
                self.addtopbottom = True
            # Add 2 widget on top
            elif add_position == 2:
                self.key = 0
            # Add 2 widget on bottom
            elif add_position == 3:
                self.key = 1
        elif self.channel_count > 1:
            self.key = rm_id-1
        else:
            self.key = 0











