# threads.py contains a custom threading.Thread Class implementation
# to catch exceptions thrown by functions executed within the thread.
# This file also contains the CheckActiveThreads function in order to
# limit the number of active threads to an arbitrary value.

import threading
from time import sleep

# Custom Thread Class for catching exceptions raised in thread.
# target function can accept either args OR kwargs, but not both.
# defaults to kwargs if both args and kwargs passed.
class ExcThread(threading.Thread):
    def __init__(self, target=None, args=(), kwargs=None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        # store exception in self.exc, if raised by self.target
        self.exc = None
        if self.kwargs is None:
            try:
                self.target(*self.args)
            except BaseException as e:
                self.exc = e
        else:
            try:
                self.target(**self.kwargs)
            except BaseException as e:
                self.exc = e

    def join(self):
        threading.Thread.join(self)
        # catch exceptions raised in thread when
        # join() is called in caller thread
        if self.exc:
            raise self.exc


# CheckActiveThreads limits threads to given max and uses exponential backoff
# to wait when active count >= 'limit'.
# 'base_ms' and 'retries' set the exponential backoff configuration.
# max_sleep_time = base_ms * (2 ** retries)
def CheckActiveThreads(limit: int, base_ms: int, retries: int):
    active = threading.activeCount()
    if active >= limit:
        sleep_time = base_ms
        for i in range(retries):
            sleep_time = sleep_time * (2 ** i)
            sleep(sleep_time / 1000)
            # check active count after waiting
            active = threading.activeCount()
            if active < limit:
                break
