from PyQt5 import QtWidgets
from PyQt5 import QtCore

class SecondWindow(QtWidgets.QWidget):

    def __init__(self):
        super(SecondWindow, self).__init__()
        self.text = QtWidgets.QPlainTextEdit(self)
        self.text.setMinimumSize(800,800)
        self.text.setReadOnly(True)
        self.init_ui()

    def init_ui(self):
        v_layout = QtWidgets.QVBoxLayout(self)
        v_layout.addWidget(self.text)
        self.setWindowTitle('Log Window')

    @QtCore.pyqtSlot()
    def loadafile(self,filename):
        try:
            with open(filename, 'r') as f:
                file_text = f.read()
                self.text.setPlainText(file_text)
            self.show()
        except:
            print("Can't open the log file")