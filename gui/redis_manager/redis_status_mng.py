import psutil

from PyQt5 import QtCore


class StatusRedis(QtCore.QObject):
    def __init__(self,parent, redis_handler):
        super().__init__()
        self.widget = parent
        self.redis_handler = redis_handler

    def set_status_redis(self,button_redis_stop,button_redis_start):
        if (not self.redis_handler.redisLocalhostLive()):
            self.widget.setText(" Stopped ")
            self.widget.setStyleSheet("background-color: red;")
            button_redis_stop.setEnabled(False)
            button_redis_start.setEnabled(True)
        else:
            self.widget.setText(" Running ")
            self.widget.setStyleSheet("background-color: green;")
            button_redis_start.setEnabled(False)
            button_redis_stop.setEnabled(True)