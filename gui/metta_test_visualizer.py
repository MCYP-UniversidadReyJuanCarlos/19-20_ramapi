import os

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileSystemModel, QTreeView
from qtconsole.qt import QtCore


class metta_test_visualizer(QtCore.QObject):
    def __init__(self,group_box_test):
        super().__init__()
        self.box= group_box_test

        self.model = QFileSystemModel()
        print(os.getcwd())
        os.chdir('MITRE')
        self.model.setRootPath(QDir.currentPath())

        print(os.getcwd())
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.currentPath()))
        os.chdir('..')
        print(os.getcwd())
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnHidden(1,True)
        self.tree.setColumnHidden(2,True)
        self.tree.setColumnWidth(0,400)

        self.box.addWidget(self.tree)

    def getModel(self):
        return self.model