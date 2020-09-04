import os

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileSystemModel, QTreeView
from qtconsole.qt import QtCore
from test_manager import run_test

class MettaTestVisualizer(QtCore.QObject):

    def __init__(self, group_box_test, test_runner):
        super().__init__()
        self.box = group_box_test
        self.complete_file_path = ''
        self.test_runner = test_runner

    def setup(self):
        self.tree = QTreeView()
        self.tree.model = QFileSystemModel()
        os.chdir('MITRE')
        self.tree.model.setRootPath(QDir.currentPath())

        self.tree.setModel(self.tree.model)
        self.tree.setRootIndex(self.tree.model.index(QDir.currentPath()))

        os.chdir('../..')

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnWidth(0, 400)

        self.box.addWidget(self.tree)
        self.tree.clicked.connect(self.get_test_name)

    def get_test_name(self, index):
        indexItem = self.tree.model.index(index.row(), 0, index.parent())

        filePath = self.tree.model.filePath(indexItem)

        run_test.RunTest.test_selected(self.test_runner,filePath)
        self.complete_file_path = filePath

    def getModel(self):
        return self.tree.model

    def set_base_path(self, base_path):
        os.chdir(base_path)
