import os
import re
import sys

from logger_manager import log_file_window
from loguru import logger
from PyQt5 import QtCore

from test_manager.asinc_test_runner import asinc_test_runner

TEST_RUNNER_LOG = 'test_runner_log.log'
ON_POSIX = 'posix' in sys.builtin_module_names


class run_test(QtCore.QObject):
    def __init__(self, startButton, statusLabel,celery_instance,redis_instance,vagrant_instance):
        try:
            os.remove(TEST_RUNNER_LOG)
        except:
            print("There is no log file")

        super(run_test, self).__init__()
        self.setup()
        self.startButton = startButton
        self.base_path = None
        self.status = statusLabel
        self.path_of_the_test = ''

        self.celery = celery_instance
        self.vagrant = vagrant_instance
        self.redis = redis_instance

        self.status.setText(" Stoped ")
        self.status.setStyleSheet("background-color: red")
        self.startButton.setEnabled(False)

    def setup(self):
        logger.add(TEST_RUNNER_LOG, filter=lambda record: record["extra"]["task"] == "test_runner",
                   format="{level} | {message}")
        self.logger_a = logger.bind(task="test_runner")
        self.log_windows = log_file_window.SecondWindow()

    def start_test(self):
        cmd_test_runner = "python run_simulation_yaml.py -f " + str(
            self.path_of_the_test)  # Needs the MITRE/XXXXXX/test_XXXX_XXXX.yml
        self.command_runner = asinc_test_runner(cmd_test_runner, self.startButton, self.status)
        if (not self.is_test_running()):
            self.command_runner.start()
        else:
            self.logger_a.warning("Can't execute a test, one is already running")
            self.startButton.setEnabled(False)

    def test_selected(self, file_path):

        if not (re.match(r"[A-z\/0-9-]*\.yml", str(file_path))):
            self.startButton.setEnabled(False)
        else:
            self.path_of_the_test = file_path
            if (not self.is_test_running() and self.redis.redis_handler.redisLocalhostLive()
                    and self.celery.is_celery_working() and self.vagrant.status):
                self.status.setText(" Stoped ")
                self.status.setStyleSheet("background-color: red")
                self.startButton.setEnabled(True)
            else:
                print("Esta corriendo")

    def is_test_running(self):
        try:
            print("Is thread alive " + str(self.command_runner.is_alive()))
            return self.command_runner.is_alive()
        except:
            print("Can't get the status of the thread")

    def set_base_path(self, base_path):
        self.base_path = base_path

    def get_file_log(self):
        self.log_windows.loadafile(TEST_RUNNER_LOG)

    def enqueue_output(self, out, queue, mode):
        for line1 in iter(out.readline, b''):
            line = str(line1, 'utf-8')
            queue.put(line)
            if "info" == mode:
                self.logger_a.info(line)
            if "error" == mode:
                self.logger_a.error(line)
            else:
                self.logger_a.warning(line)
        out.close()
