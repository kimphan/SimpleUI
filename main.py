
import sys
import signal
from PyQt5.QtWidgets import *
from ui.mainwindow_ui import ExampleUI
from ui.graph_ui import GraphUi
import os


def signal_handler(signum, f):
    print(str('Caught signal num {}, {}.').format(signum, os.getpid()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExampleUI()
    window.show()
    graph = GraphUi()
    graph.make_connection(window)
    window.make_connection(graph)

    # signal.signal(signal.SIGINT, signal_handler)

    sys.exit(app.exec_())






