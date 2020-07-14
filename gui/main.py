from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog
from PyQt5 import uic, QtWidgets
import sys
import platform
import psutil
from subprocess import Popen, PIPE
from shlex import split

from subprocess import check_output


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Load the main window
        uic.loadUi("main_gui.ui",self)
        self.w = []
        self.setup()

    def setup(self):
        # Initialize the REDIS group box
        redis_version = self.set_redis_version()
        self.version_of_redis_label.setText(redis_version)
        if redis_version == "None":
            self.group_redis.setEnabled(False)
            self.install_redis_button.setEnabled(True)
        else:
            self.group_redis.setEnabled(True)
            self.install_redis_button.setEnabled(False)

        #Initialize Redis status
        if self.get_status_redis() == None:
            self.status_redis.setText(" Stopped ")
            self.status_redis.setStyleSheet("background-color: red;")
        else:
            self.status_redis.setText(" Running ")
            self.status_redis.setStyleSheet("background-color: green;")

        # List vagrant boxes
        list_machines = self.list_vagrant_machines()

        if list_machines == []:
            self.group_vagrant.setEnabled(False)
            self.install_vagrant_button.setEnabled(True)
        else:
            self.group_vagrant.setEnabled(True)
            self.install_vagrant_button.setEnabled(False)
            for i in range(len(list_machines)):
                self.combo_vagrant_boxes.addItem(str(list_machines[i]))

        self.open_browse_files_vagrant.clicked.connect(self.search_vagrant_machine)

        # TODO - Make the installation of REDIS relative to the OS, in a new pop-up window.
        print(platform.system())
        self.get_status_redis()


    def set_redis_version(self):
        cmd_line_command_redis_version = "redis-server --version "
        cmd_line_awk_formatter = "awk '{ print $3 }' "

        p1 = Popen(split(cmd_line_command_redis_version), stdout=PIPE)
        p2 = Popen(split(cmd_line_awk_formatter), stdin=p1.stdout, stdout=PIPE)
        stdout, stderr = p2.communicate()

        stdout_formatted = str(stdout).strip('b\' , \\n ')

        if p2.errors == "None":
            return "None"
        else:
            return str(stdout_formatted)

    def get_status_redis(self):
        process_name = "redis-server"
        pid = None

        for proc in psutil.process_iter():
            if process_name in proc.name():
                pid = proc.pid
        return pid


    def get_pid(self,name):
        return int(check_output())



    # Methods for Vagrant Box
    def list_vagrant_machines(self):
        cmd_line_vagrant_box_list = "vagrant box list"

        p1 = Popen(split(cmd_line_vagrant_box_list),stdout=PIPE)
        stdout, stderr = p1.communicate()

        stdout_formatted = str(stdout).strip('b\' , \\n ')

        list_of_machines = stdout_formatted.split('\\')

        if len(list_of_machines) == 0:
            return []
        else:
            return list_of_machines

    def search_vagrant_machine(self):
        filename = QFileDialog.getOpenFileName()
        print(filename)
        self.lineEdit.setText(filename[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
