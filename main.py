
import sys
from PyQt5.QtWidgets import *
from ui.mainwindow_ui import ExampleUI
from ui.graph_ui import GraphUi

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExampleUI()
    window.show()
    # graph = GraphUi()
    # graph.make_connection(window)
    # window.make_connection(graph)

    sys.exit(app.exec_())






