import subprocess
import sys
import threading

from queue import Queue
from loguru import logger

TEST_RUNNER_LOG = 'test_runner_log.log'
ON_POSIX = 'posix' in sys.builtin_module_names

class AsincTestRunner(threading.Thread):

    def __init__(self, cmd, start_button, status_label):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.startButton = start_button
        self.status = status_label


        logger.add(TEST_RUNNER_LOG, filter=lambda record: record["extra"]["task"] == "test_runner",
               format="{level} | {message}")
        self.logger_a = logger.bind(task="test_runner")
        
    def run(self):
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)

        q = Queue()
        t = threading.Thread(target=self.enqueue_output, args=(self.process.stdout, q, "info"))
        t_error = threading.Thread(target=self.enqueue_output, args=(self.process.stderr, q, "error"))
        t.daemon = True
        t_error.daemon = True
        t.start()
        t_error.start()

        if self.is_alive():
            self.status.setStyleSheet("background-color: cyan ")
            self.status.setText(" Running ")
            self.startButton.setEnabled(False)

        exit_code = self.process.wait()

        if (exit_code == 0):
            self.status.setText(" Finished ")
            self.status.setStyleSheet("background-color: green")
        else:
            self.status.setText(" Error ")
            self.status.setStyleSheet("background-color: red")

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
