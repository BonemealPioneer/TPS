import threading
import time


class PeriodicExecutor(threading.Thread):

    def __init__(self, sleep, func, params):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.params = params
        self.sleep = sleep
        threading.Thread.__init__(self, name="PeriodicExecutor")
        self.setDaemon(1)

    def run(self):
        while True:
            time.sleep(self.sleep)
            self.func(*self.params)
