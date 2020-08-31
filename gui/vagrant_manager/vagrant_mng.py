import os
import re
import sys
import vagrant
from logger_manager import log_file_window

from shutil import copyfile
from PyQt5 import QtCore
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QFileDialog
from qtconsole.qt import QtGui

VAGRANT_LOG_NAME = "vagrant_log.log"
ON_POSIX = 'posix' in sys.builtin_module_names

class VagrantMng(QtCore.QObject):
    # Methods for Vagrant Box
    def __init__(self,path,browse,status,start_button,stop_button):
        super(VagrantMng,self).__init__()
        #os.remove(VAGRANT_LOG_NAME)
        self.path = path
        self.browse_button = browse
        self.status_label = status
        self.start_button = start_button
        self.stop_button = stop_button
        self.status = False

        log_cm = vagrant.make_file_cm(VAGRANT_LOG_NAME)
        self.log_windows = log_file_window.SecondWindow()
        self.vagrant = vagrant.Vagrant(out_cm=log_cm, err_cm=log_cm, quiet_stdout=False)

        self.get_vagrant_machine_status()
        self.start_button.clicked.connect(self.start_vagrant)
        self.stop_button.clicked.connect(self.stop_vagrant)
        self.create_validator_vagrant_file()

    #TODO metodo de start_vagrant machine ->>config, arranque y actualice el estado
    def start_vagrant(self):
        if (self.validate_input_vagrantfile()):
            self.setup_configuratio_file()
            self.vagrant.up()
            self.get_vagrant_machine_status()
        else:
            print("Can't start the Vagrant machine")

    def create_validator_vagrant_file(self):
        reg_ex = QRegExp("\/[A-z0-9-_/]*\/Vagrantfile")
        self.input_validator = QRegExpValidator(reg_ex)
        self.path.setValidator(self.input_validator)

    def validate_input_vagrantfile(self):
        state = self.input_validator.validate(self.path.text(), 0)[0]
        value = False
        #print(state)
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b'  # green
            value = True
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        self.path.setStyleSheet('QLineEdit { background-color: %s }' % color)
        return value

    def stop_vagrant(self):
        self.vagrant.halt()
        print("Lanzada signal de parada")
        self.get_vagrant_machine_status()
        self.restore_configuration_file()

    def list_vagrant_machines(self):
        #print(self.vagrant.box_list())
        return self.vagrant.box_list()

    def search_vagrant_machine(self):
        filename = QFileDialog.getOpenFileName()
        self.path.setText(filename[0])

    # Configuration file
    def setup_configuratio_file(self):
        vagrantfile_path = str(self.path.text())
        dir_of_vagrant_file = os.path.dirname(vagrantfile_path)

        vagrant_name = self.vagrant.status()[0].name

        copyfile(str(os.getcwd()) + "/config.ini", str(os.getcwd()) + "/config.ini_bck")

        fichero_entrada = open(str(os.getcwd()) + "/config.ini_bck", "rt")
        fichero_salida = open(str(os.getcwd()) + "/config.ini" , "wt")

        for line in fichero_entrada:
            # read replace the string and write to output file
            line = re.sub(r"windows=[a-z]*", "windows="+vagrant_name, line)
            line = re.sub(r"linux=[a-z]*", "linux="+vagrant_name, line)
            line = re.sub(r"osx=[a-z]*", "osx="+vagrant_name, line)
            line = re.sub(r"kali=[a-z]*", "kali="+vagrant_name, line)
            line = re.sub(r"vagrantlocation=/Users/xxx/vagrant/", 'vagrantlocation='+vagrantfile_path, line)
            fichero_salida.write(line)
        # close input and output files
        fichero_entrada.close()
        fichero_salida.close()

    def restore_configuration_file(self):
        os.remove("config.ini")
        copyfile("config.ini_bck", "config.ini")
        os.remove("config.ini_bck")

    def get_vagrant_machine_status(self):
        print("Getting status")
        status = self.vagrant.status()
        #print(type(self.vagrant.status()[0]))

        if "poweroff" == status[0].state:
            self.status = False
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(True)
            self.status_label.setText(" Stopped ")
            self.status_label.setStyleSheet("background-color: red;")
        else:
            self.status = True
            self.stop_button.setEnabled(True)
            self.start_button.setEnabled(False)
            self.status_label.setText(" Running ")
            self.status_label.setStyleSheet("background-color: green;")

    def get_file_log(self):
        self.log_windows.loadafile(VAGRANT_LOG_NAME)
