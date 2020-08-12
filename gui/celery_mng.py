import log_file_window
import os
import subprocess
import sys
import time
import window_live_logger

from loguru import logger
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore
from queue import Queue
from threading import Thread


CELERY_LOG_NAME = "celery_log.log"
ON_POSIX = 'posix' in sys.builtin_module_names

class CeleryManager(QtCore.QObject):

    def __init__(self, status,startButton,stopButton,window_logger):
        super(CeleryManager,self).__init__()
        self.startButton = startButton
        self.stopButton = stopButton
        self.status = status
        self.window_logger = window_live_logger.QTextEditLogger(window_logger)
        #self.window_logger.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #os.chdir("..")
        logger.add(CELERY_LOG_NAME, filter=lambda record: record["extra"]["task"] == "celery")
        self.logger_a = logger.bind(task="celery")

        self.logger_a.add(self.window_logger)

        self.log_windows = log_file_window.SecondWindow()

        if not (self.is_celery_working()):
            self.status.setText(" Stoped ")
            self.status.setStyleSheet("background-color: red")
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
        else:
            self.logger_a.warning("Can't stop Celery worker")

    def enqueue_output(self, out, queue,mode):
        for line in iter(out.readline, b''):
            queue.put(line)
            if "info" == mode:
                self.logger_a.info(line)
            if "error" == mode:
                self.logger_a.error(line)
            else:
                self.logger_a.warning(line)
        out.close()

    def startCelery(self):
        if (not self.is_celery_working()):
            cmd_line_redis_starter = 'celery worker -A workers.vagranttasks -b redis://127.0.0.1/1 --loglevel=DEBUG -n vagrant@%h --concurrency=3'
            print(cmd_line_redis_starter)
            self.process = subprocess.Popen(cmd_line_redis_starter,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE ,bufsize=1, close_fds=ON_POSIX)

            q = Queue()
            t = Thread(target=self.enqueue_output, args=(self.process.stdout, q,"info"))
            t_error = Thread(target=self.enqueue_output, args=(self.process.stderr, q, "error"))
            t.daemon = True
            t_error.daemon = True

            t.start()
            t_error.start()

        self.is_celery_working()

        if self.is_celery_working():
            self.status.setText(" Running ")
            self.status.setStyleSheet("background-color: green;")
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)
        else:
            self.logger_a.warning("Can't start Celery worker")

    def stopCelery(self):
        self.logger_a.info("Terminating celery process")

        try:
            self.process.terminate()
            is_working = self.is_celery_working()
            print(is_working)
            if not(is_working):
                self.status.setText(" Stoped ")
                self.process.kill()
                self.status.setStyleSheet("background-color: red")
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
            else:
                self.logger_a.warning("Can't stop Celery worker")
        except:
            self.logger_a.warning("Can't terminate the Celery worker")

    def is_celery_working(self):
        cmd_check_status_celery = 'ps -ef | grep celery | wc -l'
        time.sleep(4)
        process = subprocess.Popen(cmd_check_status_celery, shell=True,stdout=subprocess.PIPE,bufsize=1)
        number_of_celery = (int(process.communicate()[0]))
        if (number_of_celery > 2):
            print(number_of_celery)
            return True
        else:
            return False

    def get_file_log(self):
        self.log_windows.loadafile(CELERY_LOG_NAME)