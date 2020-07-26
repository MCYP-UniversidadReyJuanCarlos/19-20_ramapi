import os
import threading

from PyQt5.QtWidgets import QSizePolicy, QLayout, QGridLayout

from PyQt5 import QtWidgets, QtCore
import logging

class QTextEditLogger(logging.Handler, QtCore.QObject,threading.Thread):
    appendPlainText = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()

        threading.Thread.__init__(self)
        self.daemon = False
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)

        grid = QGridLayout()
        QtCore.QObject.__init__(self)
        self.widget = parent
        self.widget.setReadOnly(True)

        self.widget.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self.widget.setMinimumSize(491,310)
        self.widget.setMaximumSize(491,160000)
        self.widget.verticalScrollBar()
        self.appendPlainText.connect(self.widget.appendPlainText)
        self.start()

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)

    def run(self,record):
        self.emit(record)