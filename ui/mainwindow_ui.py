from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

class ExampleUI (QMainWindow):
    LABELFONT = 15
    add_button = pyqtSignal('QGridLayout', int, str, str, int)

    def __init__(self):
        super(ExampleUI, self).__init__()

        self.resize(1000, 800)
        self.center()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle('Example')
        self.setMenuBar(self.mymenu())

        self.key = 0
        self.is_rm_c1 = False
        self.is_rm_c2 = False
        self.is_rm_c3 = False
        self.addtop = False
        self.addtopbottom = False
        self.rm_list = list()

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
        self.graph_type.addItem('Random')
        self.graph_type.addItem('Sine wave')
        self.graph_type.addItem('Real-time plot')

        vertical_menu = QVBoxLayout()
        vertical_menu.setAlignment(Qt.AlignLeft)
        vertical_menu.SetFixedSize

        channel_select = QGroupBox('Channel Select')
        channel_select.setStyleSheet('font-size: 14pt; font-style: bold; color: 606060;')
        selectC = QHBoxLayout()
        selectC.addWidget(self.channel_list)
        channel_select.setLayout(selectC)
        channel_select.setFixedWidth(self.width()/4)
        channel_select.setFixedHeight(self.height()/8)

        add_channel = QGroupBox('Add Channel')
        add_channel.setStyleSheet('font-size: 14pt; font-style: bold; color: 606060;')
        addC = QFormLayout()
        addC.addRow(str('Graph type: '), self.graph_type)
        addC.addRow(str('Channel Name: '), self.channel_name)
        addC.addRow(str('x-Axis: '), self.x_axis)
        addC.addRow(str('y-Axis: '), self.y_axis)
        addC.addRow(str(''), add_btn)

        add_channel.setLayout(addC)
        add_channel.setFixedWidth(self.width()/4)

        vertical_menu.addWidget(channel_select)
        vertical_menu.addWidget(add_channel)

        self.graph_display = QGridLayout()
        self.graph_display.setAlignment(Qt.AlignTop)
        self.graph_display.SetMinAndMaxSize

        self.windowLayout.addLayout(vertical_menu)
        self.windowLayout.addLayout(self.graph_display)

    # Label
    @staticmethod
    def label(name,fontsize=20):
        lbl = QLabel()
        lbl.setText(name)
        lbl.minimumSizeHint()
        lbl.setStyleSheet('font-size: {}pt; font-style: bold; color: 606060;'.format(fontsize))
        return lbl

    # @staticmethod
    # def addgraph(title, button,label):
    #     graph_holder = QGroupBox(title)
    #
    #     graph = QVBoxLayout()
    #     lbl = QLabel()
    #     lbl.setText(label)
    #     lbl.minimumSizeHint()
    #     lbl.setStyleSheet('font-size: 15pt; font-style: bold; color: 606060;')
    #     btn = QPushButton(button)
    #     btn.setStyleSheet('font-size: 15pt;')
    #
    #     graph.addWidget(lbl)
    #     # graph.addWidget(clist2, 5, Qt.AlignLeft)
    #     graph.addWidget(btn, Qt.AlignRight)
    #     graph_holder.setLayout(graph)
    #
    #     return graph_holder

    # Put the application window in the center of the screen
    def center(self):
            qr = self.frameGeometry()  # specifying geometry of the main window with a rectangle 'qr'
            cp = QDesktopWidget().availableGeometry().center()  # screen size resolution+get the center point
            qr.moveCenter(cp)  # set the rectangle center to the center of the screen
            self.move(qr.topLeft())  # move the top-left point of the application window to the 'qr'

        # Menu bar
    def mymenu(self):
         # saveaction = self.actiondef('Save',QKeySequence.Save,self.saveact)
            # editaction = self.actiondef('Edit',QKeySequence.Back,self.editact)

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
        if self.addtop and self.key == 2:
            self.key = 4
        elif self.addtopbottom and self.key == 1:
            self.key = 3
        else:
            self.key += 1

        if self.key >= 4:
            message = QMessageBox.information(self, 'Message', 'Number of displayed graph exceeds the limit.', QMessageBox.Ok)
            if QMessageBox.Ok:
                pass
        else:
            self.add_button.emit(self.graph_display, self.graph_type.currentIndex(), self.x_axis.text(), self.y_axis.text(), self.key)
            self.channel_name.clear()
            self.x_axis.clear()
            self.y_axis.clear()

    def make_connection(self, _object_):
        _object_.rm_button.connect(self.remove_channel)

    @pyqtSlot('QGroupBox',int,int)
    def remove_channel(self, rm_layout, rm_id, add_position):
        rm_layout.close()
        self.rm_list.append(rm_id)

        # Add 1 widget on top and 1 at botton
        if add_position == 1:
            self.key = 0
            self.addtopbottom = True
        # Add 2 widget on top
        elif add_position == 2:
            self.key = 0
            self.addtop = True
        # Add 2 widget on bottom
        elif add_position == 3:
            self.key = 1
        else:
            self.key = rm_id-1











