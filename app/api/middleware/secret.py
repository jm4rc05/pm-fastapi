import random
import string
import time
import threading


class Secret:

    def __init__(self, interval: int = 3600):
        self._key = None
        self.interval = interval
        
        self.rotation = threading.Thread(target = self._schedule, args = (interval,))
        self.rotation.stop = threading.Event()
        self.rotation.daemon = True

    def __call__(self) -> str:
        return self._key

    def __enter__(self):
        self.rotation.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.rotation.stop.set()

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
