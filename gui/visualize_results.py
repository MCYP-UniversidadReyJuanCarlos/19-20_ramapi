import os

from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtWebEngineWidgets
class visualize_results(QtWidgets.QWidget):

    def __init__(self):
        super(visualize_results,self).__init__()
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.init_ui()

    def init_ui(self):
        v_layout = QtWidgets.QVBoxLayout(self)
        v_layout.addWidget(self.view)
        self.setWindowTitle('Results')

    def load_results(self):
        path  = os.path.split(os.path.abspath(__file__))[0]+r'/../log.html'
        print(path)
        self.view.load(QtCore.QUrl().fromLocalFile(
            path
        ))
        self.show()