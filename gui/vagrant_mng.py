import os
from shlex import split
from shutil import copyfile
from subprocess import Popen, PIPE

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog


class VagrantMng(QtCore.QObject):
    # Methods for Vagrant Box
    def __init__(self,combo,path,browse,setup):
        super(VagrantMng,self).__init__()
        self.combo = combo
        self.path = path
        self.browse_button = browse
        self.setup_button = setup

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
        self.path.setText(filename[0])


    # Configuration file
    def setup_configuratio_file(self):
        vagrantfile_path = str(self.path.text())
        vagrant_box = str(self.combo.currentText())

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