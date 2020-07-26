from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

import sys
import platform

import redis_status_mng
import redis_version_mng
import redis_connect
import redis_management
import vagrant_mng

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Load the main window
        uic.loadUi("main_gui.ui",self)

        #self.logCeleryFile = logToFile.LogPipe(logging.INFO, 'celery_log')
        #self.log = self.logCeleryFile.logging.getLogger('celery_log')
        self.setup()

    def setup(self):

        # Setup logger
        '''
        self.logTextBox = logger.QTextEditLogger(self.plainTextEdit_celery_log)
        # log to text box
        self.logTextBox.widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        self.log = logging.getLogger("main")
        self.logTextBox.setFormatter(
            logging.Formatter(
                '[%(asctime)s %(levelname)s;%(module)s;%(funcName)s] %(message)s'))
        self.log.addHandler(self.logTextBox)
        self.log.setLevel(logging.DEBUG)
        '''

        # Initialize the REDIS group box
        redis_version = redis_version_mng.RedisVersion(self.version_of_redis_label)
        redis_version.set_redis_version(self.group_redis,self.install_redis_button)

        self.redis_machine.setText('localhost')
        self.redis_port.setText('6379')

        redis_handler = redis_connect.RedisHandler(self.redis_machine,self.redis_port)

        # Initialize Redis status
        redis_status = redis_status_mng.statusRedis(self.status_redis, redis_handler)
        redis_status.set_status_redis(self.stop_redis_button,self.start_redis_button)

        self.redis_hdi = redis_management.ManageRedis(self.stop_redis_button, self.start_redis_button,
                                                      redis_status, redis_handler)



        self.start_redis_button.clicked.connect(self.redis_hdi.start_redis)
        self.stop_redis_button.clicked.connect(self.redis_hdi.stop_redis)


        # List vagrant boxes
        self.vagrant_manager = vagrant_mng.VagrantMng(self.combo_vagrant_boxes,self.path_to_vagrantfile,
                                                 self.open_browse_files_vagrant, self.set_up_config_ini)
        list_machines = self.vagrant_manager.list_vagrant_machines()

        if list_machines == []:
            self.group_vagrant.setEnabled(False)
            self.install_vagrant_button.setEnabled(True)
        else:
            self.group_vagrant.setEnabled(True)
            self.install_vagrant_button.setEnabled(False)
            for i in range(len(list_machines)):
                self.combo_vagrant_boxes.addItem(str(list_machines[i]))

        self.open_browse_files_vagrant.clicked.connect(self.vagrant_manager.search_vagrant_machine)

        # Setup de file config.ini
        self.set_up_config_ini.clicked.connect(self.vagrant_manager.setup_configuratio_file)

        # TODO - Make the installation of REDIS relative to the OS, in a new pop-up window.
        print(platform.system())
        redis_status.get_status_redis()

        # Celery log
        #self.log.info('celery_log')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
