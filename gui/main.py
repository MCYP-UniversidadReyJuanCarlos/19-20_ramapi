from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import sys
import os

from test_manager import metta_test_visualizer, visualize_results, run_test
from redis_manager import redis_connect, redis_management, redis_status_mng, redis_version_mng, visualize_installation
from vagrant_manager import vagrant_mng,visualize_installation_vagrant
from celery_manger import celery_mng

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Load the main window
        uic.loadUi("main_gui.ui",self)
        os.chdir('..')
        print("Main " + os.getcwd())
        self.base_path = os.getcwd()
        self.setup()

    def setup(self):

        ###############################################################################################################
        #                                               REDIS                                                         #
        ###############################################################################################################

        # Initialize the REDIS group box
        redis_version = redis_version_mng.RedisVersion(self.version_of_redis_label)
        redis_version.set_redis_version(self.group_redis,self.install_redis_button)

        self.redis_machine.setText('localhost')
        self.redis_port.setText('6379')

        redis_handler = redis_connect.RedisHandler(self.redis_machine, self.redis_port)

        # Initialize Redis status
        redis_status = redis_status_mng.StatusRedis(self.status_redis, redis_handler)
        redis_status.set_status_redis(self.stop_redis_button,self.start_redis_button)

        self.redis_hdi = redis_management.ManageRedis(self.stop_redis_button, self.start_redis_button,
                                                      redis_status, redis_handler, self.redis_port)
        self.redis_hdi.set_base_path(self.base_path)
        self.start_redis_button.clicked.connect(self.redis_hdi.start_redis)
        self.stop_redis_button.clicked.connect(self.redis_hdi.stop_redis)
        self.log_redis_button.clicked.connect(self.redis_hdi.get_file_log)

        # TODO - Make the installation of REDIS relative to the OS, in a new pop-up window.
        self.installation_redis = visualize_installation.VisualizeInstallation()
        self.installation_redis.set_base_path(self.base_path)
        self.install_redis_button.clicked.connect(self.installation_redis.load_results)
        ###############################################################################################################
        #                                           VAGRANT                                                           #
        ###############################################################################################################
        # List vagrant boxes
        self.vagrant_manager = vagrant_mng.VagrantMng(self.path_to_vagrantfile, self.open_browse_files_vagrant,
                                                      self.status_vargrant, self.start_vagrant_button,
                                                      self.stop_vagrant_button)
        list_machines = self.vagrant_manager.list_vagrant_machines()
        self.log_vagrant_button.clicked.connect(self.vagrant_manager.get_file_log)
        if not list_machines:
            self.group_vagrant.setEnabled(False)
            self.install_vagrant_button.setEnabled(True)
        else:
            self.group_vagrant.setEnabled(True)
            self.install_vagrant_button.setEnabled(False)

        self.open_browse_files_vagrant.clicked.connect(self.vagrant_manager.search_vagrant_machine)
        self.installation_vagrant = visualize_installation_vagrant.VisualizeInstallation()
        self.installation_vagrant.set_base_path(self.base_path)
        self.install_vagrant_button.clicked.connect(self.installation_vagrant.load_results)

        ###############################################################################################################
        #                                           CELERY                                                            #
        ###############################################################################################################

        #Celery Manager
        self.celery_mng = celery_mng.CeleryManager(self.status_celery, self.celery_start_button,
                                                   self.celery_stop_button, self.plainTextEdit_celery_log,
                                                   self.redis_port)
        self.celery_mng.setup()
        self.celery_start_button.clicked.connect(self.celery_mng.startCelery)
        self.celery_stop_button.clicked.connect(self.celery_mng.stopCelery)
        self.log_celery_button.clicked.connect(self.celery_mng.get_file_log)


        ###############################################################################################################
        #                                       TEST EXECUTION                                                        #
        ###############################################################################################################
        # Runner test initialize
        self.test_runner = run_test.RunTest(self.start_execution_test, self.status_label_test,
                                             self.celery_mng,self.redis_hdi,self.vagrant_manager)
        self.log_execution_test.clicked.connect(self.test_runner.get_file_log)

        # List tests to execute.
        self.list_test = metta_test_visualizer.MettaTestVisualizer(self.gridLayout_6, self.test_runner)
        self.list_test.set_base_path(self.base_path)
        self.list_test.setup()


        self.start_execution_test.clicked.connect(self.test_runner.start_test)
        self.get_results = visualize_results.VisualizeResults()
        self.get_results.set_base_path(self.base_path)
        self.visualize_results_button.clicked.connect(self.get_results.load_results)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
