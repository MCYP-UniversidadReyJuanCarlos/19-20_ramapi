import subprocess
import time
import log_file_window
import sys

from threading import Thread
from PyQt5 import QtCore
from loguru import logger
from queue import Queue

ON_POSIX = 'posix' in sys.builtin_module_names

REDIS_LOG_NAME = 'log_redis.log'

class ManageRedis(QtCore.QObject):
    def __init__(self,stop_button,start_button,redis_status,redis_handler):
        super(ManageRedis, self).__init__()
        self.stop_button = stop_button
        self.start_button = start_button
        self.status_redis = redis_status
        self.redis_handler = redis_handler

        logger.add(REDIS_LOG_NAME, filter=lambda record: record["extra"]["task"] == "redis")
        self.logger_a = logger.bind(task="redis")
        self.log_windows = log_file_window.SecondWindow()

    def enqueue_output(self,out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
            self.logger_a.info(line)
        out.close()

    def start_redis(self):
        self.logger_a.info("redis")
        cmd_line_redis_starter = "redis-server"

        process = subprocess.Popen([cmd_line_redis_starter],stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
        q = Queue()
        t = Thread(target=self.enqueue_output, args=(process.stdout, q))
        t.daemon = True
        t.start()

        self.check_redis_status()

        # TODO setWarning status -- Se the logs ?

    def stop_redis(self):
        cmd_line_redis_stop = 'pkill -9 redis-server'
        subprocess.call(cmd_line_redis_stop, shell=True)
        time.sleep(2)

        self.check_redis_status()

    def check_redis_status(self):
        timer = 0;
        while (timer < 5 and not(self. redis_handler.redisLocalhostLive())):
            time.sleep(1)
            timer += 1
        self.status_redis.set_status_redis(self.stop_button, self.start_button)

    def get_file_log(self):
        self.log_windows.loadafile(REDIS_LOG_NAME)

