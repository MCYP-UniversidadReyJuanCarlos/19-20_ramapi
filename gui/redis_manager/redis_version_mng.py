from PyQt5 import QtCore
from subprocess import Popen, PIPE
from shlex import split


class RedisVersion(QtCore.QObject):
    # Methods for REDIS
    def __init__(self,parent):
        self.widget = parent

    def get_redis_version_command(self):
        cmd_line_command_redis_version = "redis-server --version "
        cmd_line_awk_formatter = "awk '{ print $3 }' "

        p1 = Popen(split(cmd_line_command_redis_version), stdout=PIPE)
        p2 = Popen(split(cmd_line_awk_formatter), stdin=p1.stdout, stdout=PIPE)
        stdout, stderr = p2.communicate()

        stdout_formatted = str(stdout).strip('b\' , \\n , v=')

        if p2.errors == "None":
            return "None"
        else:
            return str(stdout_formatted)

    def set_redis_version(self,groupBox,installButton):
        redis_version = self.get_redis_version_command()
        self.widget.setText(redis_version)
        if redis_version == "None":
            groupBox.setEnabled(False)
            installButton.setEnabled(True)
        else:
            groupBox.setEnabled(True)
            installButton.setEnabled(False)

