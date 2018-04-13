
import sys
from PyQt5.QtWidgets import *
from ui.mainwindow_ui import ExampleUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExampleUI()
    window.show()
    sys.exit(app.exec_())






