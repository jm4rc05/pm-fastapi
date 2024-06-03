import random
import string
import time
import threading


class Secret:

    def __init__(self, interval: int = 3600):
        self._key = None
        self.interval = interval
        
        rotation = threading.Thread(target = self._schedule, args = (interval,))
        rotation.daemon = True
        rotation.start()

    def __call__(self) -> str:
        return self._key

    def _generate(self, length: int = 32) -> str:
       self._key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def _schedule(self, interval: int):
        while True:
            self._generate()
            time.sleep(interval)

    @property
    def key(self) -> str:
        if self._key == None:
            self._generate()

        return self._key
