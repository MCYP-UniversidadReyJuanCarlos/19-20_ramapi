from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QAbstractScrollArea, QSizePolicy, \
    QVBoxLayout
from PyQt5 import uic, QtWidgets, QtCore
from subprocess import Popen, PIPE
from shlex import split
from shutil import copyfile

import sys
import platform
import psutil
import time
import redis
import subprocess
import os
import logging


from subprocess import check_output


class QTextEditLogger(logging.Handler, QtCore.QObject):
    appendPlainText = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QtCore.QObject.__init__(self)
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setMinimumSize(491,211)
        self.widget.setMaximumSize(491,160000)
        self.widget.verticalScrollBar()
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Load the main window
        uic.loadUi("main_gui.ui",self)
        self.w = []
        self.setup()

    def setup(self):

        logTextBox = QTextEditLogger(self.celery_log)
        # log to text box
        logTextBox.widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)


        logTextBox.setFormatter(
            logging.Formatter(
                '[%(asctime)s %(levelname)s;%(module)s;%(funcName)s] %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

        # log to file
        fh = logging.FileHandler('my-log.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'))
        logging.getLogger().addHandler(fh)

        for i in range(100):
            logging.info("ey")


        # Initialize the REDIS group box
        self.set_redis_version()
        # Initialize Redis status
        self.set_status_redis()
        self.start_redis_button.clicked.connect(self.start_redis)
        self.stop_redis_button.clicked.connect(self.stop_redis)

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

        # Setup de file config.ini
        self.set_up_config_ini.clicked.connect(self.setup_configuratio_file)

        # TODO - Make the installation of REDIS relative to the OS, in a new pop-up window.
        print(platform.system())
        self.get_status_redis()


    # Methods for REDIS
    def get_redis_version_command(self):
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

    def set_redis_version(self):
        redis_version = self.get_redis_version_command()
        self.version_of_redis_label.setText(redis_version)
        if redis_version == "None":
            self.group_redis.setEnabled(False)
            self.install_redis_button.setEnabled(True)
        else:
            self.group_redis.setEnabled(True)
            self.install_redis_button.setEnabled(False)

    def get_status_redis(self):
        process_name = "redis-server"
        pid = None

        for proc in psutil.process_iter():
            if process_name in proc.name():
                pid = proc.pid
        return pid

    def get_pid(self,name):
        return int(check_output())

    def set_status_redis(self):
        if (not self.redisLocalhostLive()):
            self.status_redis.setText(" Stopped ")
            self.status_redis.setStyleSheet("background-color: red;")
            self.stop_redis_button.setEnabled(False)
            self.start_redis_button.setEnabled(True)
        else:
            self.status_redis.setText(" Running ")
            self.status_redis.setStyleSheet("background-color: green;")
            self.start_redis_button.setEnabled(False)
            self.stop_redis_button.setEnabled(True)

############################### CLEAN UP #####################################

    def start_redis(self):
        cmd_line_redis_starter = "redis-server"

        subprocess.Popen([cmd_line_redis_starter],shell=True)
        time.sleep(1)
        timer = 0;
        while not(self.redisLocalhostLive() or timer > 5):
            time.sleep(1)
            timer += 1
        self.set_status_redis()

        # TODO setWarning status -- Se the logs ?

    def redisLocalhostLive(self):
        redtest = redis.Redis('localhost',6379)  # non-default ports could go here
        try:
            return redtest.ping()
        except (redis.exceptions.ConnectionError,ConnectionRefusedError) as e:
            #raise e from None
            print(e)
            return False

    def stop_redis(self):
        cmd_line_redis_stop = 'pkill -9 redis-server'

        subprocess.call(cmd_line_redis_stop, shell=True,timeout=5,)
        time.sleep(2)

        timer = 0;
        while (self.redisLocalhostLive() or timer > 5):
            print("Esperando muerte")
            time.sleep(1)
            timer += 1

        self.set_status_redis()

############################### CLEAN UP #####################################

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
        self.path_to_vagrantfile.setText(filename[0])


    # Configuration file
    def setup_configuratio_file(self):
        vagrantfile_path = str(self.path_to_vagrantfile.text())
        vagrant_box = str(self.combo_vagrant_boxes.currentText())

        vagrant_box = vagrant_box.split(' ')[0]

        with open(vagrantfile_path) as f:
            if vagrant_box in f.read():
                print("The Vagrant file and the Vagrant machine match")

        copyfile(str(os.getcwd()) + "/../config.ini", str(os.getcwd()) + "/../config.ini_bck")

        fichero_entrada = open(str(os.getcwd()) + "/../config.ini_bck", "rt")

        fichero_salida = open(str(os.getcwd()) + "/../config.ini" , "wt")

        for line in fichero_entrada:
            # read replace the string and write to output file
            fichero_salida.write(line.replace('vagrantlocation=/Users/xxx/vagrant/', 'vagrantlocation=' + vagrantfile_path))
        # close input and output files
        fichero_entrada.close()
        fichero_salida.close()

    def restore_configuration_file(self):
        os.remove("../config.ini")
        copyfile("../config.ini_bck", "../config.ini")
        os.remove("../config.ini_bck")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
