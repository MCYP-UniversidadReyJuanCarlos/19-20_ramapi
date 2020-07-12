from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import uic
import sys
import platform

from subprocess import Popen, PIPE
from shlex import split

from subprocess import check_output



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Load the main window
        uic.loadUi("main_gui.ui",self)

        # Initialize the REDIS group box
        redis_version = self.set_redis_version()
        self.version_of_redis_label.setText(redis_version)
        if redis_version == "None":
            self.group_redis.setEnabled(False)
            self.install_redis_button.setEnabled(True)
        else:
            self.group_redis.setEnabled(True)
            self.install_redis_button.setEnabled(False)

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

        self.status_redis.setStyleSheet("background-color: yellow;")

        # Print the running OS.
        print(platform.system())


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

    #def get_status_redis(self):


    def get_pid(self,name):
        return check_output(["pidof", name])



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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
