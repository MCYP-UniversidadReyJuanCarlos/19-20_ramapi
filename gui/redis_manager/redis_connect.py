import redis

class RedisHandler():
    def __init__(self,machine,port):
        super().__init__()
        self.machine = machine
        self.port = port

    def redisLocalhostLive(self):
        print(self.port.toPlainText())
        redtest = redis.Redis(host=self.machine.toPlainText(),
                                      port=int(self.port.toPlainText()), db=0)  # non-default ports could go here
        try:
            return redtest.ping()
        except (redis.ConnectionError, ConnectionRefusedError) as e:

            # raise e from None
            print(e)
            return False
